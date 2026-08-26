"""Identifier generation boundary for runtime services."""

from typing import Protocol

from rrs.domain.ids import (
    CommandId,
    EventId,
    ExecutionId,
    FailureId,
    InteractionId,
    JobId,
    MessageId,
)


class IdGenerator(Protocol):
    def new_job_id(self) -> JobId: ...

    def new_execution_id(self) -> ExecutionId: ...

    def new_command_id(self) -> CommandId: ...

    def new_event_id(self) -> EventId: ...

    def new_interaction_id(self) -> InteractionId: ...

    def new_message_id(self) -> MessageId: ...

    def new_failure_id(self) -> FailureId: ...


__all__ = ["IdGenerator"]
