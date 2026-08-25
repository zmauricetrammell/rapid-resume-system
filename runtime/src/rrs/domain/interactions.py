"""Interaction and InteractionMessage domain records."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType

from rrs.domain.enums import InteractionStatus, InteractionType
from rrs.domain.ids import InteractionId, InvocationId, JobId, MessageId


def _require_aware(value: datetime | None, field_name: str) -> None:
    if value is not None and value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True)
class Interaction:
    interaction_id: InteractionId
    job_id: JobId
    interaction_type: InteractionType
    provider: str
    provider_context: Mapping[str, object]
    professional_context: Mapping[str, object]
    status: InteractionStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    def __post_init__(self) -> None:
        if not self.interaction_id or not self.job_id or not self.provider:
            raise ValueError("Interaction IDs and provider must be nonempty")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.updated_at, "updated_at")
        _require_aware(self.completed_at, "completed_at")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot precede created_at")
        if self.completed_at is not None and self.completed_at < self.created_at:
            raise ValueError("completed_at cannot precede created_at")
        object.__setattr__(
            self,
            "provider_context",
            MappingProxyType(dict(self.provider_context)),
        )
        object.__setattr__(
            self,
            "professional_context",
            MappingProxyType(dict(self.professional_context)),
        )


@dataclass(frozen=True)
class InteractionMessage:
    message_id: MessageId
    interaction_id: InteractionId
    provider: str
    provider_message_id: str | None
    provider_created_at: datetime | None
    direction: str
    message_type: str
    content: str | None
    content_ref: str | None
    persisted_at: datetime
    processed_at: datetime | None
    processed_by_continuation_id: InvocationId | None

    def __post_init__(self) -> None:
        if not self.message_id or not self.interaction_id:
            raise ValueError("Message IDs must be nonempty")
        if not self.provider or not self.direction or not self.message_type:
            raise ValueError("provider, direction, and message_type must be nonempty")
        if self.content is None and self.content_ref is None:
            raise ValueError("InteractionMessage requires content or content_ref")
        _require_aware(self.provider_created_at, "provider_created_at")
        _require_aware(self.persisted_at, "persisted_at")
        _require_aware(self.processed_at, "processed_at")
        if self.processed_by_continuation_id is not None and self.processed_at is None:
            raise ValueError("processed continuation requires processed_at")


__all__ = ["Interaction", "InteractionMessage"]
