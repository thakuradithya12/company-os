"""SSRF penetration guard and bounded direct-to-IP HTTP client."""

from __future__ import annotations

import http.client
import ipaddress
import socket
import ssl
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

_CARRIER_GRADE_NAT = ipaddress.ip_network("100.64.0.0/10")
_DEFAULT_TIMEOUT_SECONDS = 5.0
_DEFAULT_MAX_BYTES = 1024 * 1024  # 1 MB


class NetworkSecurityError(Exception):
    """Base exception for bounded network operations."""


class SSRFSecurityError(NetworkSecurityError):
    """Raised when an outbound URL targets a prohibited destination."""


class HttpTimeoutError(NetworkSecurityError):
    """Raised when an HTTP request exceeds its timeout ceiling."""


class ResponseSizeExceededError(NetworkSecurityError):
    """Raised when an HTTP response exceeds the maximum allowed byte length."""


class InvalidContentTypeError(NetworkSecurityError):
    """Raised when an HTTP response returns an unaccepted media type."""


@dataclass(frozen=True)
class HttpResponse:
    """Immutable envelope of a bounded HTTP retrieval."""

    status_code: int
    headers: dict[str, str]
    content: bytes
    text: str
    content_type: str
    byte_length: int


class SSRFPenetrationGuard:
    """Validates destinations and resolves DNS to prevent SSRF and DNS rebinding."""

    def is_prohibited_ip(
        self,
        ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
        allow_loopback: bool = False,
    ) -> bool:
        """Return True if the IP address is private, loopback, link-local, or reserved."""
        # Handle IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            return self.is_prohibited_ip(ip.ipv4_mapped, allow_loopback=allow_loopback)

        if ip.is_loopback:
            return not allow_loopback

        if (
            ip.is_private
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return True

        if isinstance(ip, ipaddress.IPv4Address) and ip in _CARRIER_GRADE_NAT:
            return True

        return False

    def validate_and_resolve(
        self,
        url: str,
        allow_loopback: bool = False,
    ) -> tuple[str, str, int, list[ipaddress.IPv4Address | ipaddress.IPv6Address], str]:
        """Validate URL scheme and resolve host to verified IP addresses.

        Returns (scheme, hostname, port, validated_ips, path_and_query).
        """
        parsed = urlparse(url)
        scheme = (parsed.scheme or "").lower()
        if scheme not in {"http", "https"}:
            raise SSRFSecurityError(
                f"Unsupported scheme {scheme!r}; only http and https are permitted"
            )

        hostname = parsed.hostname
        if not hostname:
            raise SSRFSecurityError("URL is missing a valid hostname")

        port = parsed.port or (443 if scheme == "https" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        # Resolve host addresses using getaddrinfo
        try:
            addr_info = socket.getaddrinfo(
                hostname, port, type=socket.SOCK_STREAM
            )
        except socket.gaierror as exc:
            raise SSRFSecurityError(
                f"DNS resolution failed for host {hostname!r}"
            ) from exc

        if not addr_info:
            raise SSRFSecurityError(
                f"No addresses resolved for host {hostname!r}"
            )

        # Inspect all resolved addresses; if ANY resolved IP is prohibited, reject
        validated_ips: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
        for entry in addr_info:
            sockaddr = entry[4]
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)

            if self.is_prohibited_ip(ip_obj, allow_loopback=allow_loopback):
                raise SSRFSecurityError(
                    f"Prohibited IP address {ip_str!r} for host {hostname!r}"
                )

            if ip_obj not in validated_ips:
                validated_ips.append(ip_obj)

        if not validated_ips:
            raise SSRFSecurityError(
                f"Could not find a valid IP for host {hostname!r}"
            )

        return scheme, hostname, port, validated_ips, path


class DirectIPHTTPSConnection(http.client.HTTPSConnection):
    """Direct-to-IP HTTPS connection enforcing TLS SNI and cert hostname verification."""

    def __init__(
        self,
        ip_address: str,
        server_hostname: str,
        port: int | None = None,
        *,
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
        context: ssl.SSLContext | None = None,
    ) -> None:
        super().__init__(ip_address, port=port, timeout=timeout, context=context)
        self._server_hostname = server_hostname

    def connect(self) -> None:
        """Connect directly to the validated IP and wrap with TLS for server_hostname."""
        self.sock = self._create_connection(
            (self.host, self.port), self.timeout, self.source_address
        )
        try:
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError:
            pass

        ssl_ctx = self._context or ssl.create_default_context()
        self.sock = ssl_ctx.wrap_socket(
            self.sock,
            server_hostname=self._server_hostname,
        )


class BoundedHttpClient:
    """Performs direct-to-IP HTTP/HTTPS GET requests with anti-rebinding and bounds."""

    def __init__(
        self,
        allow_loopback: bool = False,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
        max_bytes: int = _DEFAULT_MAX_BYTES,
        accepted_content_types: frozenset[str] | None = None,
        ssl_context: ssl.SSLContext | None = None,
    ) -> None:
        self._guard = SSRFPenetrationGuard()
        self._allow_loopback = allow_loopback
        self._timeout_seconds = timeout_seconds
        self._max_bytes = max_bytes
        self._ssl_context = ssl_context
        self._accepted_content_types = accepted_content_types or frozenset({
            "text/html",
            "text/plain",
            "application/json",
            "application/xml",
            "text/xml",
        })

    def get(self, url: str, max_redirects: int = 3) -> HttpResponse:
        """Perform a bounded GET request following redirects manually with SSRF checks."""
        current_url = url
        for _ in range(max_redirects + 1):
            scheme, hostname, port, validated_ips, path = self._guard.validate_and_resolve(
                current_url, allow_loopback=self._allow_loopback
            )

            response: http.client.HTTPResponse | None = None
            last_conn_error: Exception | None = None
            host_header = hostname if port in (80, 443) else f"{hostname}:{port}"
            headers = {
                "Host": host_header,
                "User-Agent": "CompanyOS-ResearchBot/1.0",
                "Accept": "*/*",
                "Connection": "close",
            }

            for ip_addr in validated_ips:
                conn: http.client.HTTPConnection | DirectIPHTTPSConnection
                ip_str = str(ip_addr)

                if scheme == "https":
                    context = self._ssl_context or ssl.create_default_context()
                    conn = DirectIPHTTPSConnection(
                        ip_str,
                        server_hostname=hostname,
                        port=port,
                        timeout=self._timeout_seconds,
                        context=context,
                    )
                else:
                    conn = http.client.HTTPConnection(
                        ip_str,
                        port=port,
                        timeout=self._timeout_seconds,
                    )

                try:
                    conn.request("GET", path, headers=headers)
                    response = conn.getresponse()
                    break
                except TimeoutError:
                    conn.close()
                    last_conn_error = HttpTimeoutError(
                        f"HTTP request timed out after {self._timeout_seconds}s"
                    )
                except ssl.SSLCertVerificationError as exc:
                    conn.close()
                    raise NetworkSecurityError(
                        f"TLS certificate verification failed for {hostname!r}: "
                        f"{exc.verify_message}"
                    ) from exc
                except ssl.SSLError as exc:
                    conn.close()
                    raise NetworkSecurityError(
                        f"TLS handshake failed for {hostname!r}: {exc}"
                    ) from exc
                except ConnectionRefusedError as exc:
                    conn.close()
                    last_conn_error = exc
                    continue
                except Exception as exc:
                    conn.close()
                    last_conn_error = exc

            if response is None:
                if isinstance(last_conn_error, NetworkSecurityError):
                    raise last_conn_error
                raise NetworkSecurityError(
                    f"Connection failed: {type(last_conn_error).__name__}"
                ) from last_conn_error

            # Handle redirects manually
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                conn.close()
                if not location:
                    raise SSRFSecurityError("Redirect missing Location header")
                # Resolve relative redirects safely
                current_url = urljoin(current_url, location)
                continue

            # Process response
            resp_headers: dict[str, str] = {
                k.lower(): v for k, v in response.getheaders()
            }
            content_type_header = resp_headers.get("content-type", "")
            media_type = content_type_header.split(";")[0].strip().lower()
            if media_type and media_type not in self._accepted_content_types:
                conn.close()
                raise InvalidContentTypeError(
                    f"Unaccepted content type {media_type!r}"
                )

            chunks: list[bytes] = []
            total_read = 0
            chunk_size = 8192

            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                total_read += len(chunk)
                if total_read > self._max_bytes:
                    conn.close()
                    raise ResponseSizeExceededError(
                        f"Response size exceeded {self._max_bytes} bytes"
                    )
                chunks.append(chunk)

            conn.close()
            content = b"".join(chunks)
            text = content.decode("utf-8", errors="replace")

            return HttpResponse(
                status_code=response.status,
                headers=resp_headers,
                content=content,
                text=text,
                content_type=content_type_header,
                byte_length=total_read,
            )

        raise SSRFSecurityError(
            f"Exceeded maximum allowed redirects ({max_redirects})"
        )
