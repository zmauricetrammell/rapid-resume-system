"""Durable Event domain records."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType

from rrs.domain.enums import EventCriticality, EventStatus
from rrs.domain.ids import (
    CommandId,
    EventId,
    ExecutionId,
    JobId,
    RuntimeInstanceId,
)


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(value))


def _require_aware(value: datetime | None, field_name: str) -> None:
    if value is not None and value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True)
class EventSource:
    category: str
    provider: str
    provider_event_id: str | None

    def __post_init__(self) -> None:
        if not self.category or not self.provider:
            raise ValueError("Event source category and provider must be nonempty")


@dataclass(frozen=True)
class Event:
    event_id: EventId
    event_type: str
    job_id: JobId | None
    payload: Mapping[str, object]
    source: EventSource
    correlation_id: str | None
    causation_id: EventId | CommandId | ExecutionId | None
    criticality: EventCriticality
    status: EventStatus
    attempt_count: int
    owner_runtime_instance_id: RuntimeInstanceId | None
    lease_expires_at: datetime | None
    created_at: datetime
    processed_at: datetime | None

    def __post_init__(self) -> None:
        if not self.event_id or not self.event_type:
            raise ValueError("event_id and event_type must be nonempty")
        if self.attempt_count < 0:
            raise ValueError("attempt_count must be >= 0")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.lease_expires_at, "lease_expires_at")
        _require_aware(self.processed_at, "processed_at")
        if (self.owner_runtime_instance_id is None) != (self.lease_expires_at is None):
            raise ValueError("Event claim owner and lease must be set together")
        object.__setattr__(self, "payload", _freeze_mapping(self.payload))


__all__ = ["Event", "EventSource"]
