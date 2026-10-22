from __future__ import annotations

import http.server
import threading
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from company_os.domain.network_security import SSRFSecurityError
from company_os.domain.tools import (
    ExecutionRequest,
    RiskTier,
    SourceVerifierInput,
    create_default_tool_registry,
)


class _TestServer:
    def __init__(self, handler_cls: type[http.server.BaseHTTPRequestHandler]) -> None:
        self.server = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def test_tool_registry_authorization() -> None:
    registry = create_default_tool_registry()
    tool = registry.get("research.source_verifier")
    assert tool is not None
    assert tool.risk_tier == RiskTier.TIER_0_READ_ONLY
    assert "AG-03" in tool.allowed_agent_ids

    # AG-03 is authorized
    assert registry.is_agent_authorized("research.source_verifier", "AG-03") is True
    # AG-07 (builder) is NOT authorized for research tool
    assert registry.is_agent_authorized("research.source_verifier", "AG-07") is False
    # Unregistered tool
    assert registry.is_agent_authorized("unknown.tool", "AG-03") is False


def test_source_verifier_input_validation() -> None:
    # Valid input
    valid = SourceVerifierInput(url="https://example.com/research")
    assert valid.url == "https://example.com/research"

    # Reject empty URL
    with pytest.raises(ValidationError):
        SourceVerifierInput(url="")

    # Reject extra fields
    with pytest.raises(ValidationError):
        SourceVerifierInput(url="https://example.com", extra_field="bad")  # type: ignore[call-arg]


def test_source_verifier_real_execution() -> None:
    class DocHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Q3 Financial Evidence</h1></body></html>")

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _TestServer(DocHandler)
    try:
        registry = create_default_tool_registry()
        tool = registry.get("research.source_verifier")
        assert tool is not None

        params = tool.input_schema(
            url=f"http://127.0.0.1:{server.port}/evidence",
            expected_snippet="Q3 Financial Evidence",
            allow_loopback_for_testing=True,
        )
        output, checks, evidence_ref = tool.handler(params)

        assert output["status_code"] == 200
        assert "Q3 Financial Evidence" in output["snippet_preview"]
        assert output["content_sha256"] is not None
        assert evidence_ref.startswith("evidence:research:sha256:")

        # Verification checks must contain structured evidence
        assert len(checks) >= 3
        check_ids = {c["check_id"] for c in checks}
        assert "http_status" in check_ids
        assert "snippet_present" in check_ids
        assert all(c["passed"] is True for c in checks)
    finally:
        server.stop()


def test_source_verifier_rejects_ssrf() -> None:
    registry = create_default_tool_registry()
    tool = registry.get("research.source_verifier")
    assert tool is not None

    params = tool.input_schema(
        url="http://169.254.169.254/latest/meta-data/",
        allow_loopback_for_testing=False,
    )
    with pytest.raises(SSRFSecurityError):
        tool.handler(params)


def test_execution_contracts() -> None:
    task_id = uuid4()
    req = ExecutionRequest(
        task_id=task_id,
        agent_id="AG-03",
        tool_id="research.source_verifier",
        parameters={"url": "https://example.com"},
    )
    assert req.task_id == task_id
    assert req.agent_id == "AG-03"
    assert req.tool_id == "research.source_verifier"
