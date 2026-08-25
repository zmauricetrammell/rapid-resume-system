"""Persistent Failure history domain records."""

from dataclasses import dataclass
from datetime import datetime

from rrs.domain.enums import FailureClass
from rrs.domain.ids import (
    CommandId,
    EventId,
    ExecutionId,
    FailureId,
    InteractionId,
    JobId,
)


def _require_aware(value: datetime | None, field_name: str) -> None:
    if value is not None and value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True)
class Failure:
    failure_id: FailureId
    job_id: JobId
    execution_id: ExecutionId | None
    event_id: EventId | None
    command_id: CommandId | None
    interaction_id: InteractionId | None
    failure_class: FailureClass
    message: str
    details_ref: str | None
    created_at: datetime
    resolved_at: datetime | None
    resolution_message: str | None

    def __post_init__(self) -> None:
        if not self.failure_id or not self.job_id or not self.message:
            raise ValueError("failure_id, job_id, and message must be nonempty")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.resolved_at, "resolved_at")
        if self.resolved_at is not None and self.resolved_at < self.created_at:
            raise ValueError("resolved_at cannot precede created_at")
        if self.resolved_at is None and self.resolution_message is not None:
            raise ValueError("unresolved Failure cannot have resolution_message")


__all__ = ["Failure"]
