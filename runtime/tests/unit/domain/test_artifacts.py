from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from rrs.domain.artifacts import (
    ArtifactCommitGroup,
    ArtifactMetadata,
    ArtifactRef,
    ArtifactVersion,
    ResourceRef,
    SchemaRef,
    StagedArtifact,
)
from rrs.domain.enums import ArtifactRuntimeStatus, ArtifactType
from rrs.domain.ids import ArtifactId, CommitGroupId, ExecutionId, OperationKey


def test_artifact_version_starts_at_one() -> None:
    assert ArtifactVersion(1).value == 1


@pytest.mark.parametrize("value", [0, -1, -100])
def test_artifact_version_rejects_nonpositive_values(value: int) -> None:
    with pytest.raises(ValueError, match=">= 1"):
        ArtifactVersion(value)


def test_artifact_versions_are_orderable() -> None:
    assert ArtifactVersion(1) < ArtifactVersion(2)


def test_artifact_ref_preserves_exact_identity() -> None:
    ref = ArtifactRef(
        artifact_type=ArtifactType.JOB_EXPERIENCE_ANALYSIS,
        artifact_id=ArtifactId("artifact-jea"),
        artifact_version=ArtifactVersion(3),
        uri="file:///data/artifacts/artifact-jea/v3.yaml",
    )

    assert ref.artifact_type is ArtifactType.JOB_EXPERIENCE_ANALYSIS
    assert ref.artifact_id == "artifact-jea"
    assert ref.artifact_version == ArtifactVersion(3)
    assert ref.uri.endswith("v3.yaml")


@pytest.mark.parametrize(
    ("artifact_id", "uri"),
    [
        ("", "file:///data/artifact"),
        ("artifact-1", ""),
    ],
)
def test_artifact_ref_rejects_empty_identity_fields(
    artifact_id: str,
    uri: str,
) -> None:
    with pytest.raises(ValueError):
        ArtifactRef(
            artifact_type=ArtifactType.TARGET_JOB,
            artifact_id=ArtifactId(artifact_id),
            artifact_version=ArtifactVersion(1),
            uri=uri,
        )


def test_resource_ref_separates_semantic_identity_from_git_provenance() -> None:
    first = ResourceRef(
        path="agents/researcher/contract.md",
        content_hash="sha256:semantic-content",
        git_commit="commit-a",
    )
    second = ResourceRef(
        path="agents/researcher/contract.md",
        content_hash="sha256:semantic-content",
        git_commit="commit-b",
    )

    assert first.content_hash == second.content_hash
    assert first.git_commit != second.git_commit


def test_schema_ref_preserves_exact_schema_identity() -> None:
    schema = SchemaRef(
        path="schemas/job-experience-analysis.yaml",
        content_hash="sha256:jea-schema",
        git_commit="commit-a",
    )

    assert schema.path == "schemas/job-experience-analysis.yaml"
    assert schema.content_hash == "sha256:jea-schema"


@pytest.mark.parametrize("ref_type", [ResourceRef, SchemaRef])
def test_resource_refs_require_path_and_content_hash(
    ref_type: type[ResourceRef] | type[SchemaRef],
) -> None:
    with pytest.raises(ValueError):
        ref_type(path="", content_hash="hash")
    with pytest.raises(ValueError):
        ref_type(path="resource", content_hash="")


def test_artifact_metadata_preserves_storage_and_provenance() -> None:
    committed_at = datetime(2026, 8, 24, 12, 0, tzinfo=UTC)
    metadata = ArtifactMetadata(
        artifact_id=ArtifactId("artifact-1"),
        artifact_version=ArtifactVersion(2),
        artifact_type=ArtifactType.EVIDENCE_RESPONSE,
        storage_uri="file:///data/artifacts/artifact-1/v2.yaml",
        content_hash="sha256:artifact-content",
        committed_by_execution_id=ExecutionId("execution-1"),
        operation_key=OperationKey("operation-key-1"),
        committed_at=committed_at,
        runtime_status=ArtifactRuntimeStatus.COMMITTED,
    )

    assert metadata.artifact_version == ArtifactVersion(2)
    assert metadata.committed_by_execution_id == "execution-1"
    assert metadata.committed_at == committed_at
    assert metadata.runtime_status is ArtifactRuntimeStatus.COMMITTED


def test_target_job_metadata_may_have_no_execution() -> None:
    metadata = ArtifactMetadata(
        artifact_id=ArtifactId("target-job-1"),
        artifact_version=ArtifactVersion(1),
        artifact_type=ArtifactType.TARGET_JOB,
        storage_uri="file:///data/artifacts/target-job-1/v1.pdf",
        content_hash="sha256:target-job",
        committed_by_execution_id=None,
        operation_key=None,
        committed_at=None,
        runtime_status=ArtifactRuntimeStatus.COMMITTED,
    )

    assert metadata.committed_by_execution_id is None
    assert metadata.operation_key is None


def test_commit_group_preserves_exact_artifact_refs() -> None:
    ref = ArtifactRef(
        artifact_type=ArtifactType.TARGETED_RESUME,
        artifact_id=ArtifactId("resume-1"),
        artifact_version=ArtifactVersion(1),
        uri="file:///data/artifacts/resume-1/v1.docx",
    )
    group = ArtifactCommitGroup(
        commit_group_id=CommitGroupId("commit-group-1"),
        execution_id=ExecutionId("execution-1"),
        artifacts=(ref,),
        committed_at=None,
    )

    assert group.artifacts == (ref,)


def test_staged_artifact_has_no_authoritative_artifact_id_or_version() -> None:
    staged = StagedArtifact(
        artifact_type=ArtifactType.RESUME_EVALUATION,
        execution_id=ExecutionId("execution-1"),
        staged_path="/data/staging/execution-1/evaluation.yaml",
        content_hash="sha256:staged",
        media_type="application/yaml",
    )

    assert not hasattr(staged, "artifact_id")
    assert not hasattr(staged, "artifact_version")


def test_artifact_values_are_immutable() -> None:
    version = ArtifactVersion(1)

    with pytest.raises(FrozenInstanceError):
        version.value = 2  # type: ignore[misc]
