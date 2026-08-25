"""Repository protocols for durable RRS runtime records."""

from typing import Protocol

from rrs.domain.artifacts import ArtifactMetadata, ArtifactRef
from rrs.domain.commands import Command
from rrs.domain.events import Event
from rrs.domain.executions import Execution
from rrs.domain.failures import Failure
from rrs.domain.ids import (
    ArtifactId,
    CommandId,
    EventId,
    ExecutionId,
    FailureId,
    InteractionId,
    InvocationId,
    JobId,
    MessageId,
    RoutingDecisionId,
    RuntimeInstanceId,
)
from rrs.domain.interactions import Interaction, InteractionMessage
from rrs.domain.jobs import RuntimeJob
from rrs.domain.provenance import InvocationProvenance, RuntimeInstance
from rrs.domain.routing import RoutingDecision


class RuntimeJobRepository(Protocol):
    def get(self, job_id: JobId) -> RuntimeJob | None: ...
    def add(self, job: RuntimeJob) -> None: ...


class ArtifactRepository(Protocol):
    def get(self, artifact_id: ArtifactId, version: int) -> ArtifactMetadata | None: ...
    def add(self, metadata: ArtifactMetadata, *, created_at: str) -> None: ...
    def ref(self, artifact_id: ArtifactId, version: int) -> ArtifactRef | None: ...


class ExecutionRepository(Protocol):
    def get(self, execution_id: ExecutionId) -> Execution | None: ...
    def add(self, execution: Execution) -> None: ...


class EventRepository(Protocol):
    def get(self, event_id: EventId) -> Event | None: ...
    def add(self, event: Event) -> None: ...


class CommandRepository(Protocol):
    def get(self, command_id: CommandId) -> Command | None: ...
    def add(self, command: Command) -> None: ...


class InteractionRepository(Protocol):
    def get(self, interaction_id: InteractionId) -> Interaction | None: ...
    def add(self, interaction: Interaction) -> None: ...


class InteractionMessageRepository(Protocol):
    def get(self, message_id: MessageId) -> InteractionMessage | None: ...
    def add(self, message: InteractionMessage) -> None: ...


class FailureRepository(Protocol):
    def get(self, failure_id: FailureId) -> Failure | None: ...
    def add(self, failure: Failure) -> None: ...


class InvocationProvenanceRepository(Protocol):
    def get(self, invocation_id: InvocationId) -> InvocationProvenance | None: ...
    def add(self, provenance: InvocationProvenance) -> None: ...


class RuntimeInstanceRepository(Protocol):
    def get(self, runtime_instance_id: RuntimeInstanceId) -> RuntimeInstance | None: ...
    def add(self, runtime_instance: RuntimeInstance) -> None: ...


class RoutingDecisionRepository(Protocol):
    def get(self, decision_id: RoutingDecisionId) -> RoutingDecision | None: ...
    def add(self, job_id: JobId, decision: RoutingDecision) -> None: ...


__all__ = [
    "ArtifactRepository",
    "CommandRepository",
    "EventRepository",
    "ExecutionRepository",
    "FailureRepository",
    "InteractionMessageRepository",
    "InteractionRepository",
    "InvocationProvenanceRepository",
    "RoutingDecisionRepository",
    "RuntimeInstanceRepository",
    "RuntimeJobRepository",
]
