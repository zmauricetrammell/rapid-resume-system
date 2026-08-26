"""Durable Command domain records."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType

from rrs.domain.enums import CommandStatus
from rrs.domain.ids import CommandId, EventId, JobId, RuntimeInstanceId


def _require_aware(value: datetime | None, field_name: str) -> None:
    if value is not None and value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True)
class Command:
    command_id: CommandId
    command_type: str
    job_id: JobId | None
    payload: Mapping[str, object]
    status: CommandStatus
    dedupe_key: str | None
    causation_event_id: EventId | None
    owner_runtime_instance_id: RuntimeInstanceId | None
    lease_expires_at: datetime | None
    attempt_count: int
    created_at: datetime
    completed_at: datetime | None
    last_error: str | None = None

    def __post_init__(self) -> None:
        if not self.command_id or not self.command_type:
            raise ValueError("command_id and command_type must be nonempty")
        if self.attempt_count < 0:
            raise ValueError("attempt_count must be >= 0")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.lease_expires_at, "lease_expires_at")
        _require_aware(self.completed_at, "completed_at")
        if (self.owner_runtime_instance_id is None) != (self.lease_expires_at is None):
            raise ValueError("Command claim owner and lease must be set together")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


__all__ = ["Command"]

