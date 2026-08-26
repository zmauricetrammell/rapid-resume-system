"""Atomic Event-to-Command application service."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol

from rrs.domain.commands import Command
from rrs.domain.enums import CommandStatus, EventStatus
from rrs.domain.errors import ConcurrencyConflict, PersistenceFailure
from rrs.domain.events import Event
from rrs.domain.ids import EventId, RuntimeInstanceId
from rrs.ports.clock import Clock
from rrs.ports.id_generator import IdGenerator
from rrs.ports.unit_of_work import UnitOfWork, UnitOfWorkFactory


@dataclass(frozen=True)
class PlannedCommand:
    command_type: str
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.command_type:
            raise ValueError("command_type must be nonempty")
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


class EventCommandPlanner(Protocol):
    def plan(self, event: Event) -> tuple[PlannedCommand, ...]: ...


@dataclass(frozen=True)
class EventProcessingResult:
    event_id: EventId
    final_status: EventStatus
    commands: tuple[Command, ...]
    reused_count: int
    already_terminal: bool


def derive_command_dedupe_key(
    event: Event,
    planned: PlannedCommand,
) -> str:
    identity = json.dumps(
        {
            "causation_event_id": str(event.event_id),
            "command_type": planned.command_type,
            "payload": dict(planned.payload),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"event-command:{digest}"


class EventProcessor:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        planner: EventCommandPlanner,
        clock: Clock,
        id_generator: IdGenerator,
    ) -> None:
        self.uow_factory = uow_factory
        self.planner = planner
        self.clock = clock
        self.id_generator = id_generator

    async def process(
        self,
        event_id: EventId,
        owner_runtime_instance_id: RuntimeInstanceId,
    ) -> EventProcessingResult:
        async with self.uow_factory() as uow:
            event = uow.events.get(event_id)
            if event is None:
                raise PersistenceFailure(f"Event {event_id} does not exist")

            if event.status in (EventStatus.PROCESSED, EventStatus.IGNORED):
                return EventProcessingResult(
                    event_id=event.event_id,
                    final_status=event.status,
                    commands=(),
                    reused_count=0,
                    already_terminal=True,
                )

            self._require_claim(event, owner_runtime_instance_id)
            planned_commands = self.planner.plan(event)
            commands, reused_count = self._persist_planned_commands(
                uow,
                event,
                planned_commands,
            )
            completed_at = self.clock.now()

            if commands:
                completed = uow.events.mark_processed(
                    event.event_id,
                    owner_runtime_instance_id,
                    processed_at=completed_at,
                )
                final_status = EventStatus.PROCESSED
            else:
                completed = uow.events.mark_ignored(
                    event.event_id,
                    owner_runtime_instance_id,
                    processed_at=completed_at,
                )
                final_status = EventStatus.IGNORED

            if completed is None:
                raise ConcurrencyConflict(
                    f"Event {event.event_id} claim was lost before completion"
                )

            await uow.commit()
            return EventProcessingResult(
                event_id=event.event_id,
                final_status=final_status,
                commands=commands,
                reused_count=reused_count,
                already_terminal=False,
            )

    @staticmethod
    def _require_claim(
        event: Event,
        owner_runtime_instance_id: RuntimeInstanceId,
    ) -> None:
        if event.status is not EventStatus.PROCESSING:
            raise ConcurrencyConflict(
                f"Event {event.event_id} is not in processing state"
            )
        if event.owner_runtime_instance_id != owner_runtime_instance_id:
            raise ConcurrencyConflict(
                f"Event {event.event_id} is owned by another runtime instance"
            )

    def _persist_planned_commands(
        self,
        uow: UnitOfWork,
        event: Event,
        planned_commands: tuple[PlannedCommand, ...],
    ) -> tuple[tuple[Command, ...], int]:
        commands: list[Command] = []
        reused_count = 0
        dedupe_keys: set[str] = set()

        for planned in planned_commands:
            dedupe_key = derive_command_dedupe_key(event, planned)
            if dedupe_key in dedupe_keys:
                raise ConcurrencyConflict(
                    f"Event {event.event_id} planned duplicate Command identity"
                )
            dedupe_keys.add(dedupe_key)

            existing = uow.commands.get_by_dedupe_key(dedupe_key)
            if existing is not None:
                self._require_compatible(existing, event, planned)
                commands.append(existing)
                reused_count += 1
                continue

            command = Command(
                command_id=self.id_generator.new_command_id(),
                command_type=planned.command_type,
                job_id=event.job_id,
                payload=planned.payload,
                status=CommandStatus.PENDING,
                dedupe_key=dedupe_key,
                causation_event_id=event.event_id,
                owner_runtime_instance_id=None,
                lease_expires_at=None,
                attempt_count=0,
                created_at=self.clock.now(),
                completed_at=None,
                last_error=None,
            )
            uow.commands.add(command)
            commands.append(command)

        return tuple(commands), reused_count

    @staticmethod
    def _require_compatible(
        existing: Command,
        event: Event,
        planned: PlannedCommand,
    ) -> None:
        if (
            existing.command_type != planned.command_type
            or existing.job_id != event.job_id
            or dict(existing.payload) != dict(planned.payload)
            or existing.causation_event_id != event.event_id
        ):
            raise ConcurrencyConflict(
                f"Command dedupe collision for Event {event.event_id}"
            )


__all__ = [
    "EventCommandPlanner",
    "EventProcessingResult",
    "EventProcessor",
    "PlannedCommand",
    "derive_command_dedupe_key",
]

