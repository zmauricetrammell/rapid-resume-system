"""Immutable artifact and resource value objects for the RRS runtime."""

from dataclasses import dataclass
from datetime import datetime

from rrs.domain.enums import ArtifactRuntimeStatus, ArtifactType
from rrs.domain.ids import ArtifactId, CommitGroupId, ExecutionId, OperationKey


def _require_nonempty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} must be nonempty")


@dataclass(frozen=True, order=True)
class ArtifactVersion:
    """Immutable professional artifact version, distinct from RuntimeJob revision."""

    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise ValueError("artifact version must be >= 1")


@dataclass(frozen=True)
class ArtifactRef:
    """Exact immutable reference to one professional artifact version."""

    artifact_type: ArtifactType
    artifact_id: ArtifactId
    artifact_version: ArtifactVersion
    uri: str

    def __post_init__(self) -> None:
        _require_nonempty(self.artifact_id, "artifact_id")
        _require_nonempty(self.uri, "uri")


@dataclass(frozen=True)
class ResourceRef:
    """Reference to a professional resource with semantic content identity."""

    path: str
    content_hash: str
    git_commit: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty(self.path, "path")
        _require_nonempty(self.content_hash, "content_hash")


@dataclass(frozen=True)
class SchemaRef:
    """Reference to the exact schema used for invocation and runtime validation."""

    path: str
    content_hash: str
    git_commit: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty(self.path, "path")
        _require_nonempty(self.content_hash, "content_hash")


@dataclass(frozen=True)
class ArtifactMetadata:
    """Durable metadata for one immutable artifact version."""

    artifact_id: ArtifactId
    artifact_version: ArtifactVersion
    artifact_type: ArtifactType
    storage_uri: str
    content_hash: str
    committed_by_execution_id: ExecutionId | None
    operation_key: OperationKey | None
    committed_at: datetime | None
    runtime_status: ArtifactRuntimeStatus

    def __post_init__(self) -> None:
        _require_nonempty(self.artifact_id, "artifact_id")
        _require_nonempty(self.storage_uri, "storage_uri")
        _require_nonempty(self.content_hash, "content_hash")


@dataclass(frozen=True)
class ArtifactCommitGroup:
    """Logical group of artifact references committed by one Execution."""

    commit_group_id: CommitGroupId
    execution_id: ExecutionId
    artifacts: tuple[ArtifactRef, ...]
    committed_at: datetime | None

    def __post_init__(self) -> None:
        _require_nonempty(self.commit_group_id, "commit_group_id")
        _require_nonempty(self.execution_id, "execution_id")


@dataclass(frozen=True)
class StagedArtifact:
    """Professional output staged on disk but not yet authoritative."""

    artifact_type: ArtifactType
    execution_id: ExecutionId
    staged_path: str
    content_hash: str
    media_type: str

    def __post_init__(self) -> None:
        _require_nonempty(self.execution_id, "execution_id")
        _require_nonempty(self.staged_path, "staged_path")
        _require_nonempty(self.content_hash, "content_hash")
        _require_nonempty(self.media_type, "media_type")


__all__ = [
    "ArtifactCommitGroup",
    "ArtifactMetadata",
    "ArtifactRef",
    "ArtifactVersion",
    "ResourceRef",
    "SchemaRef",
    "StagedArtifact",
]
