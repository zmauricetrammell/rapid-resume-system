"""Transaction boundary protocol for RRS persistence."""

from __future__ import annotations

from types import TracebackType
from typing import Protocol

from rrs.ports.repositories import (
    ArtifactRepository,
    CommandRepository,
    EventRepository,
    ExecutionRepository,
    FailureRepository,
    InteractionMessageRepository,
    InteractionRepository,
    InvocationProvenanceRepository,
    RoutingDecisionRepository,
    RuntimeInstanceRepository,
    RuntimeJobRepository,
)


class UnitOfWork(Protocol):
    jobs: RuntimeJobRepository
    artifacts: ArtifactRepository
    executions: ExecutionRepository
    events: EventRepository
    commands: CommandRepository
    interactions: InteractionRepository
    messages: InteractionMessageRepository
    failures: FailureRepository
    provenance: InvocationProvenanceRepository
    runtime_instances: RuntimeInstanceRepository
    routing: RoutingDecisionRepository

    async def __aenter__(self) -> UnitOfWork: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


__all__ = ["UnitOfWork"]
