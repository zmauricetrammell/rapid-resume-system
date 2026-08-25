from __future__ import annotations

from enum import StrEnum

import pytest

from rrs.domain.enums import (
    ArtifactRuntimeStatus,
    ArtifactType,
    CommandStatus,
    EventCriticality,
    EventStatus,
    ExecutionStatus,
    FailureClass,
    HealthStatus,
    InteractionProjectionStatus,
    InteractionStatus,
    InteractionType,
    LifecyclePhase,
    MutationType,
    OperationType,
    RetrievalRequirement,
    RuntimeOperationStatus,
)

ENUM_TYPES: tuple[type[StrEnum], ...] = (
    LifecyclePhase,
    OperationType,
    RuntimeOperationStatus,
    ExecutionStatus,
    InteractionProjectionStatus,
    InteractionStatus,
    InteractionType,
    HealthStatus,
    MutationType,
    RetrievalRequirement,
    ArtifactRuntimeStatus,
    EventStatus,
    EventCriticality,
    CommandStatus,
    FailureClass,
    ArtifactType,
)


@pytest.mark.parametrize(
    ("member", "persisted"),
    [
        (LifecyclePhase.MANUAL_REVIEW, "manual_review"),
        (OperationType.GENERATE_ANALYSIS, "generate_analysis"),
        (RuntimeOperationStatus.COMMITTING, "committing"),
        (ExecutionStatus.OUTPUT_RECEIVED, "output_received"),
        (InteractionProjectionStatus.NONE, "none"),
        (InteractionStatus.CANCELLED, "cancelled"),
        (InteractionType.EVIDENCE_INVESTIGATION, "evidence_investigation"),
        (HealthStatus.RECOVERABLE_FAILURE, "recoverable_failure"),
        (MutationType.UPSERT_VERSION, "upsert_version"),
        (RetrievalRequirement.REQUIRED, "required"),
        (ArtifactRuntimeStatus.ORPHANED_OUTPUT, "orphaned_output"),
        (EventStatus.DEAD_LETTER, "dead_letter"),
        (EventCriticality.WORKFLOW_CRITICAL, "workflow_critical"),
        (CommandStatus.RETRY_PENDING, "retry_pending"),
        (FailureClass.RUNTIME_INTEGRITY_FAILURE, "runtime_integrity_failure"),
        (ArtifactType.WRITER_CONTENT_MANIFEST, "writer_content_manifest"),
    ],
)
def test_persisted_enum_values_are_stable(member: StrEnum, persisted: str) -> None:
    assert member.value == persisted
    assert str(member) == persisted


@pytest.mark.parametrize("enum_type", ENUM_TYPES)
def test_invalid_persisted_enum_value_is_rejected(enum_type: type[StrEnum]) -> None:
    with pytest.raises(ValueError):
        enum_type("not-a-valid-value")


def test_v01_artifact_type_excludes_deferred_types() -> None:
    values = {item.value for item in ArtifactType}

    assert "information_request" not in values
    assert "information_response" not in values
    assert "target_role" not in values
