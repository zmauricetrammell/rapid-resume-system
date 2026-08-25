"""Execution domain records."""

from dataclasses import dataclass
from datetime import datetime

from rrs.domain.artifacts import ArtifactRef, StagedArtifact
from rrs.domain.enums import ExecutionStatus, OperationType
from rrs.domain.ids import (
    ExecutionId,
    FailureId,
    JobId,
    OperationKey,
    RuntimeInstanceId,
)


def _require_aware(value: datetime | None, field_name: str) -> None:
    if value is not None and value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")


_TERMINAL = {
    ExecutionStatus.STALE,
    ExecutionStatus.COMMITTED,
    ExecutionStatus.FAILED,
    ExecutionStatus.CANCELLED,
}


@dataclass(frozen=True)
class Execution:
    execution_id: ExecutionId
    job_id: JobId
    owner_runtime_instance_id: RuntimeInstanceId
    operation_type: OperationType
    operation_key: OperationKey
    attempt_number: int
    status: ExecutionStatus
    input_snapshot: object
    staged_outputs: tuple[StagedArtifact, ...]
    committed_outputs: tuple[ArtifactRef, ...]
    failure_id: FailureId | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    def __post_init__(self) -> None:
        if not self.execution_id or not self.job_id or not self.owner_runtime_instance_id:
            raise ValueError("Execution IDs must be nonempty")
        if not self.operation_key:
            raise ValueError("operation_key must be nonempty")
        if self.attempt_number < 1:
            raise ValueError("attempt_number must be >= 1")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.started_at, "started_at")
        _require_aware(self.completed_at, "completed_at")
        if self.started_at is not None and self.started_at < self.created_at:
            raise ValueError("started_at cannot precede created_at")
        if self.completed_at is not None and self.completed_at < self.created_at:
            raise ValueError("completed_at cannot precede created_at")
        if self.status in _TERMINAL and self.completed_at is None:
            raise ValueError("terminal Execution requires completed_at")
        if self.status not in _TERMINAL and self.completed_at is not None:
            raise ValueError("nonterminal Execution cannot have completed_at")
        if self.status is ExecutionStatus.COMMITTED and self.failure_id is not None:
            raise ValueError("committed Execution cannot reference failure_id")


__all__ = ["Execution"]
