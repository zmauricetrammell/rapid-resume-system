from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from rrs.domain.artifacts import ArtifactRef, ArtifactVersion
from rrs.domain.enums import (
    ArtifactType,
    HealthStatus,
    InteractionProjectionStatus,
    InteractionType,
    LifecyclePhase,
    OperationType,
    RuntimeOperationStatus,
)
from rrs.domain.ids import ArtifactId, ExecutionId, FailureId, InteractionId, JobId
from rrs.domain.jobs import (
    HealthState,
    InteractionProjection,
    LifecycleState,
    OperationState,
    ProfessionalState,
    RuntimeJob,
    RuntimeJobIdentity,
)

NOW = datetime(2026, 8, 24, 12, 0, tzinfo=UTC)


def artifact_ref(
    artifact_type: ArtifactType,
    artifact_id: str,
    version: int = 1,
) -> ArtifactRef:
    return ArtifactRef(
        artifact_type=artifact_type,
        artifact_id=ArtifactId(artifact_id),
        artifact_version=ArtifactVersion(version),
        uri=f"file:///data/{artifact_id}/v{version}",
    )


def valid_identity(
    *,
    revision: int = 1,
    completed_at: datetime | None = None,
) -> RuntimeJobIdentity:
    return RuntimeJobIdentity(
        job_id=JobId("job-1"),
        revision=revision,
        created_at=NOW,
        updated_at=NOW,
        completed_at=completed_at,
    )


def valid_professional_state() -> ProfessionalState:
    return ProfessionalState(
        target_job=artifact_ref(ArtifactType.TARGET_JOB, "target-job"),
        jer_set=(
            artifact_ref(ArtifactType.JOB_EXPERIENCE_RECORD, "jer-b"),
            artifact_ref(ArtifactType.JOB_EXPERIENCE_RECORD, "jer-a", 2),
        ),
        jea=None,
        active_erqs=(),
        unintegrated_evidence_responses=(),
        resume=None,
        wcm=None,
        evaluation=None,
    )


def valid_runtime_job(
    *,
    phase: LifecyclePhase = LifecyclePhase.NEW,
    completed_at: datetime | None = None,
) -> RuntimeJob:
    return RuntimeJob(
        identity=valid_identity(completed_at=completed_at),
        lifecycle=LifecycleState(phase=phase, entered_at=NOW),
        operation=OperationState(
            status=RuntimeOperationStatus.IDLE,
            operation_type=None,
            execution_id=None,
            started_at=None,
        ),
        interaction=InteractionProjection(
            status=InteractionProjectionStatus.NONE,
            interaction_type=None,
            interaction_id=None,
            started_at=None,
            last_activity_at=None,
        ),
        health=HealthState(
            status=HealthStatus.HEALTHY,
            failure_id=None,
            retry_count=0,
        ),
        professional_state=valid_professional_state(),
        routing_history=(),
    )


@pytest.mark.parametrize("revision", [0, -1])
def test_runtime_job_identity_rejects_invalid_revision(revision: int) -> None:
    with pytest.raises(ValueError, match="revision"):
        valid_identity(revision=revision)


def test_runtime_job_identity_rejects_created_after_updated() -> None:
    with pytest.raises(ValueError, match="created_at"):
        RuntimeJobIdentity(
            job_id=JobId("job-1"),
            revision=1,
            created_at=datetime(2026, 8, 25, tzinfo=UTC),
            updated_at=datetime(2026, 8, 24, tzinfo=UTC),
            completed_at=None,
        )


def test_runtime_job_identity_requires_timezone_aware_timestamps() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        RuntimeJobIdentity(
            job_id=JobId("job-1"),
            revision=1,
            created_at=datetime(2026, 8, 24),
            updated_at=datetime(2026, 8, 24),
            completed_at=None,
        )


def test_idle_operation_state_rejects_active_metadata() -> None:
    with pytest.raises(ValueError, match="idle"):
        OperationState(
            status=RuntimeOperationStatus.IDLE,
            operation_type=OperationType.GENERATE_ANALYSIS,
            execution_id=None,
            started_at=None,
        )


def test_queued_operation_may_exist_before_execution_id() -> None:
    state = OperationState(
        status=RuntimeOperationStatus.QUEUED,
        operation_type=OperationType.GENERATE_ANALYSIS,
        execution_id=None,
        started_at=None,
    )
    assert state.execution_id is None


def test_running_operation_requires_execution_and_started_at() -> None:
    with pytest.raises(ValueError, match="execution_id"):
        OperationState(
            status=RuntimeOperationStatus.RUNNING,
            operation_type=OperationType.GENERATE_ANALYSIS,
            execution_id=None,
            started_at=NOW,
        )

    with pytest.raises(ValueError, match="started_at"):
        OperationState(
            status=RuntimeOperationStatus.RUNNING,
            operation_type=OperationType.GENERATE_ANALYSIS,
            execution_id=ExecutionId("execution-1"),
            started_at=None,
        )


def test_none_interaction_projection_rejects_metadata() -> None:
    with pytest.raises(ValueError, match="none interaction"):
        InteractionProjection(
            status=InteractionProjectionStatus.NONE,
            interaction_type=InteractionType.EVIDENCE_INVESTIGATION,
            interaction_id=None,
            started_at=None,
            last_activity_at=None,
        )


@pytest.mark.parametrize(
    "status",
    [
        InteractionProjectionStatus.PENDING,
        InteractionProjectionStatus.ACTIVE,
        InteractionProjectionStatus.PAUSED,
    ],
)
def test_active_interaction_projection_requires_interaction_id(
    status: InteractionProjectionStatus,
) -> None:
    with pytest.raises(ValueError, match="interaction_id"):
        InteractionProjection(
            status=status,
            interaction_type=InteractionType.EVIDENCE_INVESTIGATION,
            interaction_id=None,
            started_at=NOW,
            last_activity_at=NOW,
        )


def test_valid_active_interaction_projection() -> None:
    projection = InteractionProjection(
        status=InteractionProjectionStatus.ACTIVE,
        interaction_type=InteractionType.EVIDENCE_INVESTIGATION,
        interaction_id=InteractionId("interaction-1"),
        started_at=NOW,
        last_activity_at=NOW,
    )
    assert projection.interaction_id == "interaction-1"


def test_health_state_rejects_negative_retry_count() -> None:
    with pytest.raises(ValueError, match="retry_count"):
        HealthState(
            status=HealthStatus.DEGRADED,
            failure_id=None,
            retry_count=-1,
        )


def test_healthy_state_rejects_failure_pointer() -> None:
    with pytest.raises(ValueError, match="healthy"):
        HealthState(
            status=HealthStatus.HEALTHY,
            failure_id=FailureId("failure-1"),
            retry_count=0,
        )


def test_nonhealthy_state_can_reference_material_failure() -> None:
    state = HealthState(
        status=HealthStatus.BLOCKED,
        failure_id=FailureId("failure-1"),
        retry_count=2,
    )
    assert state.failure_id == "failure-1"


def test_professional_state_canonicalizes_collection_order() -> None:
    state = valid_professional_state()
    assert [str(ref.artifact_id) for ref in state.jer_set] == ["jer-a", "jer-b"]


def test_professional_state_rejects_duplicate_exact_refs() -> None:
    ref = artifact_ref(ArtifactType.JOB_EXPERIENCE_RECORD, "jer-a")
    with pytest.raises(ValueError, match="duplicate"):
        ProfessionalState(
            target_job=artifact_ref(ArtifactType.TARGET_JOB, "target-job"),
            jer_set=(ref, ref),
            jea=None,
            active_erqs=(),
            unintegrated_evidence_responses=(),
            resume=None,
            wcm=None,
            evaluation=None,
        )


def test_professional_state_rejects_wrong_artifact_type() -> None:
    with pytest.raises(ValueError, match="jea"):
        ProfessionalState(
            target_job=artifact_ref(ArtifactType.TARGET_JOB, "target-job"),
            jer_set=(),
            jea=artifact_ref(ArtifactType.RESUME_EVALUATION, "wrong"),
            active_erqs=(),
            unintegrated_evidence_responses=(),
            resume=None,
            wcm=None,
            evaluation=None,
        )


def test_runtime_job_complete_requires_completed_at() -> None:
    with pytest.raises(ValueError, match="completed_at"):
        valid_runtime_job(phase=LifecyclePhase.COMPLETE, completed_at=None)


def test_runtime_job_noncomplete_rejects_completed_at() -> None:
    with pytest.raises(ValueError, match="non-complete"):
        valid_runtime_job(phase=LifecyclePhase.ANALYSIS, completed_at=NOW)


def test_valid_complete_runtime_job() -> None:
    job = valid_runtime_job(
        phase=LifecyclePhase.COMPLETE,
        completed_at=NOW,
    )
    assert job.lifecycle.phase is LifecyclePhase.COMPLETE


def test_runtime_job_is_immutable() -> None:
    job = valid_runtime_job()

    with pytest.raises(FrozenInstanceError):
        job.routing_history = ()  # type: ignore[misc]

def test_runtime_job_identity_rejects_empty_job_id() -> None:
    with pytest.raises(ValueError, match="job_id"):
        RuntimeJobIdentity(
            job_id=JobId(""),
            revision=1,
            created_at=NOW,
            updated_at=NOW,
            completed_at=None,
        )


def test_nonidle_operation_requires_operation_type() -> None:
    with pytest.raises(ValueError, match="operation_type"):
        OperationState(
            status=RuntimeOperationStatus.QUEUED,
            operation_type=None,
            execution_id=None,
            started_at=None,
        )


def test_professional_collection_rejects_wrong_artifact_type() -> None:
    with pytest.raises(ValueError, match="jer_set"):
        ProfessionalState(
            target_job=artifact_ref(ArtifactType.TARGET_JOB, "target-job"),
            jer_set=(
                artifact_ref(
                    ArtifactType.EVIDENCE_REQUEST,
                    "not-a-jer",
                ),
            ),
            jea=None,
            active_erqs=(),
            unintegrated_evidence_responses=(),
            resume=None,
            wcm=None,
            evaluation=None,
        )