"""Durable, retrievable evidence artifact store for Company OS execution engine."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class EvidenceArtifact:
    """Immutable durable evidence artifact produced by verified execution."""

    artifact_uri: str
    task_id: str | None
    execution_id: str | None
    tool_id: str
    source_url: str
    retrieved_at: str
    content_sha256: str
    content_type: str
    byte_length: int
    content_snippet: str
    verification_checks: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceArtifact:
        return cls(**data)


class EvidenceStore:
    """Manages durable persistence and retrieval of execution evidence artifacts."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        self._storage_dir = storage_dir
        self._memory_cache: dict[str, EvidenceArtifact] = {}
        if self._storage_dir:
            self._storage_dir.mkdir(parents=True, exist_ok=True)

    def store(
        self,
        *,
        tool_id: str,
        source_url: str,
        content_sha256: str,
        content_type: str,
        byte_length: int,
        content_snippet: str,
        verification_checks: list[dict[str, Any]],
        task_id: UUID | str | None = None,
        execution_id: UUID | str | None = None,
        retrieved_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceArtifact:
        """Persist a durable evidence artifact and return it with a stable URI."""
        now_str = (retrieved_at or datetime.now(UTC)).isoformat()
        clean_sha = content_sha256.lower().strip()
        exec_part = str(execution_id) if execution_id else "direct"
        artifact_uri = f"artifact://evidence/{tool_id}/{exec_part}/{clean_sha}"

        artifact = EvidenceArtifact(
            artifact_uri=artifact_uri,
            task_id=str(task_id) if task_id else None,
            execution_id=str(execution_id) if execution_id else None,
            tool_id=tool_id,
            source_url=source_url,
            retrieved_at=now_str,
            content_sha256=clean_sha,
            content_type=content_type,
            byte_length=byte_length,
            content_snippet=content_snippet,
            verification_checks=verification_checks,
            metadata=metadata or {},
        )

        self._memory_cache[artifact_uri] = artifact

        if self._storage_dir:
            file_name = f"{clean_sha}_{exec_part}.json"
            file_path = self._storage_dir / file_name
            file_path.write_text(
                json.dumps(artifact.to_dict(), indent=2, sort_keys=True),
                encoding="utf-8",
            )

        return artifact

    def retrieve(self, artifact_uri: str) -> EvidenceArtifact | None:
        """Retrieve a stored evidence artifact by its stable URI."""
        if artifact_uri in self._memory_cache:
            return self._memory_cache[artifact_uri]

        if not self._storage_dir or not self._storage_dir.exists():
            return None

        # Look for matching artifact on disk
        for file_path in self._storage_dir.glob("*.json"):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
                if data.get("artifact_uri") == artifact_uri:
                    artifact = EvidenceArtifact.from_dict(data)
                    self._memory_cache[artifact_uri] = artifact
                    return artifact
            except Exception:
                continue

        return None


_DEFAULT_EVIDENCE_STORE: EvidenceStore | None = None


def get_default_evidence_store() -> EvidenceStore:
    """Retrieve or initialize the process-wide default evidence store."""
    global _DEFAULT_EVIDENCE_STORE
    if _DEFAULT_EVIDENCE_STORE is None:
        storage_path = Path(".company_os_storage") / "evidence"
        _DEFAULT_EVIDENCE_STORE = EvidenceStore(storage_dir=storage_path)
    return _DEFAULT_EVIDENCE_STORE
