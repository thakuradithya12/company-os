from __future__ import annotations

import http.server
import ipaddress
import ssl
import threading
import time
from pathlib import Path
from typing import Any

import pytest

from company_os.domain.network_security import (
    BoundedHttpClient,
    HttpResponse,
    HttpTimeoutError,
    NetworkSecurityError,
    ResponseSizeExceededError,
    SSRFPenetrationGuard,
    SSRFSecurityError,
)


@pytest.mark.parametrize(
    "prohibited_target",
    [
        "http://127.0.0.1/",
        "http://127.0.0.2:8080/test",
        "http://localhost/",
        "http://localhost:5000/api",
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.1.1/",
        "http://10.0.0.1/",
        "http://10.254.0.1:9000/",
        "http://172.16.0.1/",
        "http://172.31.255.255/",
        "http://192.168.0.1/",
        "http://192.168.1.100:80/",
        "http://100.64.0.1/",
        "http://0.0.0.0/",
        "http://[::1]/",
        "http://[::ffff:127.0.0.1]/",
        "http://[fe80::1]/",
        "http://[fc00::1]/",
    ],
)
def test_ssrf_guard_rejects_prohibited_ips_and_names(prohibited_target: str) -> None:
    guard = SSRFPenetrationGuard()
    with pytest.raises(SSRFSecurityError):
        guard.validate_and_resolve(prohibited_target, allow_loopback=False)


@pytest.mark.parametrize(
    "invalid_scheme_url",
    [
        "file:///etc/passwd",
        "file:///C:/Windows/System32/drivers/etc/hosts",
        "ftp://ftp.example.com/file",
        "gopher://evil.com/",
        "dict://dict.org/",
        "javascript:alert(1)",
        "data:text/plain;base64,SGVsbG8=",
    ],
)
def test_ssrf_guard_rejects_non_http_schemes(invalid_scheme_url: str) -> None:
    guard = SSRFPenetrationGuard()
    with pytest.raises(SSRFSecurityError, match="Unsupported scheme"):
        guard.validate_and_resolve(invalid_scheme_url)


def test_ssrf_guard_prohibited_ip_logic() -> None:
    guard = SSRFPenetrationGuard()
    assert guard.is_prohibited_ip(ipaddress.ip_address("127.0.0.1")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("169.254.169.254")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("10.0.0.1")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("172.20.0.1")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("192.168.1.1")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("100.64.0.1")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("0.0.0.0")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("::1")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("::ffff:127.0.0.1")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("fe80::1")) is True
    assert guard.is_prohibited_ip(ipaddress.ip_address("fc00::1")) is True

    # Public addresses must be allowed
    assert guard.is_prohibited_ip(ipaddress.ip_address("93.184.216.34")) is False
    assert guard.is_prohibited_ip(ipaddress.ip_address("8.8.8.8")) is False


class _TestHttpServer:
    def __init__(self, handler_cls: type[http.server.BaseHTTPRequestHandler]) -> None:
        self.server = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def test_bounded_http_client_real_get_success() -> None:
    class SuccessHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Custom-Header", "tested")
            self.end_headers()
            body = (
                b"<html><head><title>Research Doc</title></head>"
                b"<body>Verified Findings</body></html>"
            )
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestHttpServer(SuccessHandler)
    try:
        client = BoundedHttpClient(allow_loopback=True)
        resp: HttpResponse = client.get(f"http://127.0.0.1:{server.port}/doc")
        assert resp.status_code == 200
        assert "Research Doc" in resp.text
        assert resp.content_type == "text/html; charset=utf-8"
        assert resp.byte_length > 0
        assert resp.headers.get("x-custom-header") == "tested"
    finally:
        server.stop()


def test_bounded_http_client_blocks_redirect_to_prohibited_ip() -> None:
    class RedirectToPrivateHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(302)
            self.send_header("Location", "http://169.254.169.254/latest/meta-data/")
            self.end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestHttpServer(RedirectToPrivateHandler)
    try:
        # Loopback allowed for first hop in test, but target (169.254.169.254) is prohibited
        client = BoundedHttpClient(allow_loopback=True)
        with pytest.raises(SSRFSecurityError, match="Prohibited IP address"):
            client.get(f"http://127.0.0.1:{server.port}/redirect")
    finally:
        server.stop()


def test_bounded_http_client_enforces_size_ceiling() -> None:
    class OversizedHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            chunk = b"X" * 65536
            for _ in range(32):
                self.wfile.write(chunk)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestHttpServer(OversizedHandler)
    try:
        client = BoundedHttpClient(allow_loopback=True, max_bytes=131072)
        with pytest.raises(ResponseSizeExceededError):
            client.get(f"http://127.0.0.1:{server.port}/oversized")
    finally:
        server.stop()


def test_bounded_http_client_enforces_timeout() -> None:
    class SlowHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            time.sleep(1.0)
            self.send_response(200)
            self.end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestHttpServer(SlowHandler)
    try:
        client = BoundedHttpClient(allow_loopback=True, timeout_seconds=0.2)
        with pytest.raises(HttpTimeoutError):
            client.get(f"http://127.0.0.1:{server.port}/slow")
    finally:
        server.stop()


class _TestHttpsServer:
    def __init__(
        self,
        handler_cls: type[http.server.BaseHTTPRequestHandler],
        cert_file: Path,
        key_file: Path,
    ) -> None:
        self.server = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(certfile=str(cert_file), keyfile=str(key_file))
        self.server.socket = ctx.wrap_socket(self.server.socket, server_side=True)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def test_bounded_http_client_direct_https_success() -> None:
    fixtures_dir = Path(__file__).parent / "fixtures" / "certs"
    cert_path = fixtures_dir / "localhost_cert.pem"
    key_path = fixtures_dir / "localhost_key.pem"

    class SecureHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Direct HTTPS Success Content")

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestHttpsServer(SecureHandler, cert_path, key_path)
    try:
        client_ctx = ssl.create_default_context(cafile=str(cert_path))
        client = BoundedHttpClient(
            allow_loopback=True,
            ssl_context=client_ctx,
        )
        resp = client.get(f"https://localhost:{server.port}/secure")
        assert resp.status_code == 200
        assert resp.text == "Direct HTTPS Success Content"
    finally:
        server.stop()


def test_bounded_http_client_direct_https_untrusted_cert_rejected() -> None:
    fixtures_dir = Path(__file__).parent / "fixtures" / "certs"
    cert_path = fixtures_dir / "localhost_cert.pem"
    key_path = fixtures_dir / "localhost_key.pem"

    class SecureHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestHttpsServer(SecureHandler, cert_path, key_path)
    try:
        # Default SSL context without custom CA must reject untrusted self-signed cert
        client = BoundedHttpClient(allow_loopback=True)
        with pytest.raises(NetworkSecurityError, match="TLS certificate verification failed"):
            client.get(f"https://localhost:{server.port}/secure")
    finally:
        server.stop()


def test_bounded_http_client_direct_https_hostname_mismatch_rejected() -> None:
    fixtures_dir = Path(__file__).parent / "fixtures" / "certs"
    cert_path = fixtures_dir / "mismatch_cert.pem"  # Cert is for other.example.com
    key_path = fixtures_dir / "mismatch_key.pem"

    class SecureHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestHttpsServer(SecureHandler, cert_path, key_path)
    try:
        client_ctx = ssl.create_default_context(cafile=str(cert_path))
        client = BoundedHttpClient(
            allow_loopback=True,
            ssl_context=client_ctx,
        )
        # Server presents cert for other.example.com, but target host is localhost
        with pytest.raises(NetworkSecurityError, match="TLS certificate verification failed"):
            client.get(f"https://localhost:{server.port}/secure")
    finally:
        server.stop()


def test_bounded_http_client_https_redirect_to_ssrf_rejected() -> None:
    fixtures_dir = Path(__file__).parent / "fixtures" / "certs"
    cert_path = fixtures_dir / "localhost_cert.pem"
    key_path = fixtures_dir / "localhost_key.pem"

    class RedirectHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(302)
            self.send_header("Location", "http://169.254.169.254/latest/meta-data/")
            self.end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestHttpsServer(RedirectHandler, cert_path, key_path)
    try:
        client_ctx = ssl.create_default_context(cafile=str(cert_path))
        client = BoundedHttpClient(
            allow_loopback=True,
            ssl_context=client_ctx,
        )
        with pytest.raises(SSRFSecurityError, match="Prohibited IP"):
            client.get(f"https://localhost:{server.port}/redirect-ssrf")
    finally:
        server.stop()

