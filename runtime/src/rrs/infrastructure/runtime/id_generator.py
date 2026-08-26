"""Production and deterministic identifier generators."""

from dataclasses import dataclass
from uuid import uuid4

from rrs.domain.ids import (
    CommandId,
    EventId,
    ExecutionId,
    FailureId,
    InteractionId,
    JobId,
    MessageId,
)


def _uuid_value(prefix: str) -> str:
    return f"{prefix}-{uuid4()}"


class UuidIdGenerator:
    def new_job_id(self) -> JobId:
        return JobId(_uuid_value("job"))

    def new_execution_id(self) -> ExecutionId:
        return ExecutionId(_uuid_value("execution"))

    def new_command_id(self) -> CommandId:
        return CommandId(_uuid_value("command"))

    def new_event_id(self) -> EventId:
        return EventId(_uuid_value("event"))

    def new_interaction_id(self) -> InteractionId:
        return InteractionId(_uuid_value("interaction"))

    def new_message_id(self) -> MessageId:
        return MessageId(_uuid_value("message"))

    def new_failure_id(self) -> FailureId:
        return FailureId(_uuid_value("failure"))


@dataclass
class DeterministicIdGenerator:
    next_value: int = 1

    def __post_init__(self) -> None:
        if self.next_value < 1:
            raise ValueError("next_value must be >= 1")

    def _new(self, prefix: str) -> str:
        value = f"{prefix}-{self.next_value:06d}"
        self.next_value += 1
        return value

    def new_job_id(self) -> JobId:
        return JobId(self._new("job"))

    def new_execution_id(self) -> ExecutionId:
        return ExecutionId(self._new("execution"))

    def new_command_id(self) -> CommandId:
        return CommandId(self._new("command"))

    def new_event_id(self) -> EventId:
        return EventId(self._new("event"))

    def new_interaction_id(self) -> InteractionId:
        return InteractionId(self._new("interaction"))

    def new_message_id(self) -> MessageId:
        return MessageId(self._new("message"))

    def new_failure_id(self) -> FailureId:
        return FailureId(self._new("failure"))


__all__ = ["DeterministicIdGenerator", "UuidIdGenerator"]
