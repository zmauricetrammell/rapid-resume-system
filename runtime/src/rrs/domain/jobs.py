"""Canonical immutable RuntimeJob aggregate and supporting state values."""

from dataclasses import dataclass
from datetime import datetime

from rrs.domain.artifacts import ArtifactRef
from rrs.domain.enums import (
    ArtifactType,
    HealthStatus,
    InteractionProjectionStatus,
    InteractionType,
    LifecyclePhase,
    OperationType,
    RuntimeOperationStatus,
)
from rrs.domain.ids import ExecutionId, FailureId, InteractionId, JobId
from rrs.domain.routing import RoutingDecision


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _artifact_sort_key(ref: ArtifactRef) -> tuple[str, int, str, str]:
    return (
        str(ref.artifact_id),
        ref.artifact_version.value,
        ref.artifact_type.value,
        ref.uri,
    )


def _canonical_refs(
    refs: tuple[ArtifactRef, ...],
    field_name: str,
    expected_type: ArtifactType,
) -> tuple[ArtifactRef, ...]:
    if any(ref.artifact_type is not expected_type for ref in refs):
        raise ValueError(f"{field_name} contains an invalid artifact type")
    if len(set(refs)) != len(refs):
        raise ValueError(f"{field_name} contains duplicate exact artifact references")
    return tuple(sorted(refs, key=_artifact_sort_key))


def _require_artifact_type(
    ref: ArtifactRef | None,
    field_name: str,
    expected_type: ArtifactType,
) -> None:
    if ref is not None and ref.artifact_type is not expected_type:
        raise ValueError(f"{field_name} must reference {expected_type.value}")


@dataclass(frozen=True)
class RuntimeJobIdentity:
    """Identity and compare-and-swap revision metadata for a RuntimeJob."""

    job_id: JobId
    revision: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    def __post_init__(self) -> None:
        if not self.job_id:
            raise ValueError("job_id must be nonempty")
        if self.revision < 1:
            raise ValueError("RuntimeJob revision must be >= 1")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.updated_at, "updated_at")
        if self.completed_at is not None:
            _require_aware(self.completed_at, "completed_at")
        if self.created_at > self.updated_at:
            raise ValueError("created_at must be <= updated_at")


@dataclass(frozen=True)
class LifecycleState:
    """Current authoritative lifecycle projection."""

    phase: LifecyclePhase
    entered_at: datetime

    def __post_init__(self) -> None:
        _require_aware(self.entered_at, "entered_at")


@dataclass(frozen=True)
class OperationState:
    """Current professional execution projection on RuntimeJob."""

    status: RuntimeOperationStatus
    operation_type: OperationType | None
    execution_id: ExecutionId | None
    started_at: datetime | None

    def __post_init__(self) -> None:
        if self.started_at is not None:
            _require_aware(self.started_at, "started_at")

        if self.status is RuntimeOperationStatus.IDLE:
            if any(
                value is not None
                for value in (self.operation_type, self.execution_id, self.started_at)
            ):
                raise ValueError("idle operation state cannot contain active metadata")
            return

        if self.operation_type is None:
            raise ValueError("non-idle operation state requires operation_type")

        if self.status is not RuntimeOperationStatus.QUEUED:
            if self.execution_id is None:
                raise ValueError("active operation state requires execution_id")
            if self.started_at is None:
                raise ValueError("active operation state requires started_at")


@dataclass(frozen=True)
class InteractionProjection:
    """Coarse RuntimeJob projection of authoritative Interaction state."""

    status: InteractionProjectionStatus
    interaction_type: InteractionType | None
    interaction_id: InteractionId | None
    started_at: datetime | None
    last_activity_at: datetime | None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("started_at", self.started_at),
            ("last_activity_at", self.last_activity_at),
        ):
            if value is not None:
                _require_aware(value, field_name)

        if self.status is InteractionProjectionStatus.NONE:
            if any(
                value is not None
                for value in (
                    self.interaction_type,
                    self.interaction_id,
                    self.started_at,
                    self.last_activity_at,
                )
            ):
                raise ValueError("none interaction projection cannot contain metadata")
            return

        if self.status in {
            InteractionProjectionStatus.PENDING,
            InteractionProjectionStatus.ACTIVE,
            InteractionProjectionStatus.PAUSED,
        } and self.interaction_id is None:
            raise ValueError("active interaction projection requires interaction_id")


@dataclass(frozen=True)
class HealthState:
    """Current RuntimeJob health projection."""

    status: HealthStatus
    failure_id: FailureId | None
    retry_count: int

    def __post_init__(self) -> None:
        if self.retry_count < 0:
            raise ValueError("retry_count must be >= 0")
        if self.status is HealthStatus.HEALTHY and self.failure_id is not None:
            raise ValueError("healthy RuntimeJob cannot reference a material failure")


@dataclass(frozen=True)
class ProfessionalState:
    """Current authoritative professional artifact references."""

    target_job: ArtifactRef
    jer_set: tuple[ArtifactRef, ...]
    jea: ArtifactRef | None
    active_erqs: tuple[ArtifactRef, ...]
    unintegrated_evidence_responses: tuple[ArtifactRef, ...]
    resume: ArtifactRef | None
    wcm: ArtifactRef | None
    evaluation: ArtifactRef | None

    def __post_init__(self) -> None:
        _require_artifact_type(self.target_job, "target_job", ArtifactType.TARGET_JOB)
        _require_artifact_type(
            self.jea,
            "jea",
            ArtifactType.JOB_EXPERIENCE_ANALYSIS,
        )
        _require_artifact_type(self.resume, "resume", ArtifactType.TARGETED_RESUME)
        _require_artifact_type(
            self.wcm,
            "wcm",
            ArtifactType.WRITER_CONTENT_MANIFEST,
        )
        _require_artifact_type(
            self.evaluation,
            "evaluation",
            ArtifactType.RESUME_EVALUATION,
        )

        object.__setattr__(
            self,
            "jer_set",
            _canonical_refs(
                self.jer_set,
                "jer_set",
                ArtifactType.JOB_EXPERIENCE_RECORD,
            ),
        )
        object.__setattr__(
            self,
            "active_erqs",
            _canonical_refs(
                self.active_erqs,
                "active_erqs",
                ArtifactType.EVIDENCE_REQUEST,
            ),
        )
        object.__setattr__(
            self,
            "unintegrated_evidence_responses",
            _canonical_refs(
                self.unintegrated_evidence_responses,
                "unintegrated_evidence_responses",
                ArtifactType.EVIDENCE_RESPONSE,
            ),
        )


@dataclass(frozen=True)
class RuntimeJob:
    """Canonical persistence-independent aggregate for one RRS runtime job."""

    identity: RuntimeJobIdentity
    lifecycle: LifecycleState
    operation: OperationState
    interaction: InteractionProjection
    health: HealthState
    professional_state: ProfessionalState
    routing_history: tuple[RoutingDecision, ...]

    def __post_init__(self) -> None:
        is_complete = self.lifecycle.phase is LifecyclePhase.COMPLETE
        if is_complete and self.identity.completed_at is None:
            raise ValueError("complete RuntimeJob requires completed_at")
        if not is_complete and self.identity.completed_at is not None:
            raise ValueError("non-complete RuntimeJob cannot have completed_at")


__all__ = [
    "HealthState",
    "InteractionProjection",
    "LifecycleState",
    "OperationState",
    "ProfessionalState",
    "RuntimeJob",
    "RuntimeJobIdentity",
]
