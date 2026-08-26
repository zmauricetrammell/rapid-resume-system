"""Integration tests for the atomic Event-to-Command transaction."""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import Coroutine
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from rrs.application.events import (
    EventProcessor,
    PlannedCommand,
    derive_command_dedupe_key,
)
from rrs.domain.commands import Command
from rrs.domain.enums import (
    CommandStatus,
    EventCriticality,
    EventStatus,
)
from rrs.domain.errors import ConcurrencyConflict
from rrs.domain.events import Event, EventSource
from rrs.domain.ids import (
    CommandId,
    EventId,
    RuntimeInstanceId,
)
from rrs.domain.provenance import RuntimeInstance
from rrs.infrastructure.persistence.migrations import migrate_database
from rrs.infrastructure.persistence.repositories import (
    SQLiteCommandRepository,
    SQLiteEventRepository,
    SQLiteRuntimeInstanceRepository,
)
from rrs.infrastructure.persistence.unit_of_work import (
    SQLiteUnitOfWorkFactory,
)
from rrs.infrastructure.runtime.clock import FakeClock
from rrs.infrastructure.runtime.id_generator import DeterministicIdGenerator

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)
OWNER = RuntimeInstanceId("runtime-1")


class StaticPlanner:
    def __init__(self, *planned: PlannedCommand) -> None:
        self.planned = planned

    def plan(self, event: Event) -> tuple[PlannedCommand, ...]:
        return self.planned


class FailingPlanner:
    def plan(self, event: Event) -> tuple[PlannedCommand, ...]:
        raise RuntimeError("planner failed")


def run[T](coro: Coroutine[Any, Any, T]) -> T:
    return asyncio.run(coro)


def migrated_database(tmp_path: Path) -> Path:
    database = tmp_path / "runtime.db"
    migrations = Path(__file__).resolve().parents[3] / "migrations"
    migrate_database(database, migrations)
    return database


def pending_event() -> Event:
    return Event(
        event_id=EventId("event-1"),
        event_type="artifact_committed",
        job_id=None,
        payload={"artifact_type": "job_experience_analysis"},
        source=EventSource("runtime", "rrs", None),
        correlation_id="correlation-1",
        causation_id=None,
        criticality=EventCriticality.WORKFLOW_CRITICAL,
        status=EventStatus.RECEIVED,
        attempt_count=0,
        owner_runtime_instance_id=None,
        lease_expires_at=None,
        created_at=NOW,
        processed_at=None,
        last_error=None,
    )


def seed_claimed_event(
    database: Path,
    *,
    lease_expires_at: datetime = NOW + timedelta(minutes=5),
) -> Event:
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        SQLiteRuntimeInstanceRepository(connection).add(
            RuntimeInstance(
                runtime_instance_id=OWNER,
                git_sha="git-sha",
                image_digest=None,
                operation_registry_hash="registry-hash",
                built_at=None,
                started_at=NOW,
                stopped_at=None,
            )
        )
        repository = SQLiteEventRepository(connection)
        repository.add(pending_event())
        claimed = repository.claim_next(
            OWNER,
            now=NOW,
            lease_expires_at=lease_expires_at,
        )
        assert claimed is not None
        connection.commit()
        return claimed
    finally:
        connection.close()


def load_event(database: Path) -> Event:
    connection = sqlite3.connect(database)
    try:
        loaded = SQLiteEventRepository(connection).get(EventId("event-1"))
        assert loaded is not None
        return loaded
    finally:
        connection.close()


def load_commands(database: Path) -> tuple[Command, ...]:
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute(
            "SELECT command_id FROM commands ORDER BY command_id"
        ).fetchall()
        repository = SQLiteCommandRepository(connection)
        commands = tuple(
            command
            for row in rows
            if (command := repository.get(CommandId(row[0]))) is not None
        )
        return commands
    finally:
        connection.close()


def processor(
    database: Path,
    planner: StaticPlanner | FailingPlanner,
    clock: FakeClock,
    id_generator: DeterministicIdGenerator | None = None,
) -> EventProcessor:
    return EventProcessor(
        SQLiteUnitOfWorkFactory(database),
        planner,
        clock,
        id_generator or DeterministicIdGenerator(),
    )


def test_event_commands_and_processed_state_commit_together(
    tmp_path: Path,
) -> None:
    database = migrated_database(tmp_path)
    seed_claimed_event(database)
    planner = StaticPlanner(
        PlannedCommand("evaluate_routing", {"reason": "artifact_committed"}),
        PlannedCommand("sync_projection", {"projection": "kanban"}),
    )

    result = run(
        processor(
            database,
            planner,
            FakeClock(NOW + timedelta(minutes=1)),
        ).process(EventId("event-1"), OWNER)
    )

    assert result.final_status is EventStatus.PROCESSED
    assert result.already_terminal is False
    assert result.reused_count == 0
    assert len(result.commands) == 2
    assert load_event(database).status is EventStatus.PROCESSED
    commands = load_commands(database)
    assert len(commands) == 2
    assert all(command.status is CommandStatus.PENDING for command in commands)
    assert all(
        command.causation_event_id == EventId("event-1")
        for command in commands
    )


def test_duplicate_terminal_event_is_a_safe_no_op(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)
    seed_claimed_event(database)
    planner = StaticPlanner(
        PlannedCommand("evaluate_routing", {"reason": "artifact_committed"})
    )
    service = processor(
        database,
        planner,
        FakeClock(NOW + timedelta(minutes=1)),
    )
    first = run(service.process(EventId("event-1"), OWNER))
    second = run(service.process(EventId("event-1"), OWNER))

    assert first.already_terminal is False
    assert second.already_terminal is True
    assert second.final_status is EventStatus.PROCESSED
    assert len(load_commands(database)) == 1


def test_existing_compatible_command_is_reused(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)
    event = seed_claimed_event(database)
    planned = PlannedCommand(
        "evaluate_routing",
        {"reason": "artifact_committed"},
    )
    dedupe_key = derive_command_dedupe_key(event, planned)
    existing = Command(
        command_id=CommandId("command-existing"),
        command_type=planned.command_type,
        job_id=event.job_id,
        payload=planned.payload,
        status=CommandStatus.PENDING,
        dedupe_key=dedupe_key,
        causation_event_id=event.event_id,
        owner_runtime_instance_id=None,
        lease_expires_at=None,
        attempt_count=0,
        created_at=NOW,
        completed_at=None,
        last_error=None,
    )
    connection = sqlite3.connect(database)
    try:
        SQLiteCommandRepository(connection).add(existing)
        connection.commit()
    finally:
        connection.close()
    generator = DeterministicIdGenerator()

    result = run(
        processor(
            database,
            StaticPlanner(planned),
            FakeClock(NOW + timedelta(minutes=1)),
            generator,
        ).process(event.event_id, OWNER)
    )

    assert result.commands == (existing,)
    assert result.reused_count == 1
    assert generator.next_value == 1
    assert len(load_commands(database)) == 1
    assert load_event(database).status is EventStatus.PROCESSED


def test_dedupe_collision_rolls_back_all_new_commands(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)
    event = seed_claimed_event(database)
    first = PlannedCommand("first", {"sequence": 1})
    conflicting = PlannedCommand("second", {"sequence": 2})
    dedupe_key = derive_command_dedupe_key(event, conflicting)
    collision = Command(
        command_id=CommandId("command-collision"),
        command_type="different",
        job_id=event.job_id,
        payload={"sequence": "different"},
        status=CommandStatus.PENDING,
        dedupe_key=dedupe_key,
        causation_event_id=event.event_id,
        owner_runtime_instance_id=None,
        lease_expires_at=None,
        attempt_count=0,
        created_at=NOW,
        completed_at=None,
        last_error=None,
    )
    connection = sqlite3.connect(database)
    try:
        SQLiteCommandRepository(connection).add(collision)
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(ConcurrencyConflict, match="dedupe collision"):
        run(
            processor(
                database,
                StaticPlanner(first, conflicting),
                FakeClock(NOW + timedelta(minutes=1)),
            ).process(event.event_id, OWNER)
        )

    commands = load_commands(database)
    assert commands == (collision,)
    assert load_event(database).status is EventStatus.PROCESSING


def test_lost_lease_rolls_back_commands_and_event_completion(
    tmp_path: Path,
) -> None:
    database = migrated_database(tmp_path)
    event = seed_claimed_event(database)

    with pytest.raises(ConcurrencyConflict, match="claim was lost"):
        run(
            processor(
                database,
                StaticPlanner(PlannedCommand("evaluate_routing", {})),
                FakeClock(NOW + timedelta(minutes=5)),
            ).process(event.event_id, OWNER)
        )

    assert load_commands(database) == ()
    stored_event = load_event(database)
    assert stored_event.status is EventStatus.PROCESSING
    assert stored_event.processed_at is None


def test_planner_failure_leaves_event_and_commands_unchanged(
    tmp_path: Path,
) -> None:
    database = migrated_database(tmp_path)
    event = seed_claimed_event(database)

    with pytest.raises(RuntimeError, match="planner failed"):
        run(
            processor(
                database,
                FailingPlanner(),
                FakeClock(NOW + timedelta(minutes=1)),
            ).process(event.event_id, OWNER)
        )

    assert load_commands(database) == ()
    assert load_event(database).status is EventStatus.PROCESSING


def test_event_with_no_commands_is_marked_ignored(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)
    event = seed_claimed_event(database)

    result = run(
        processor(
            database,
            StaticPlanner(),
            FakeClock(NOW + timedelta(minutes=1)),
        ).process(event.event_id, OWNER)
    )

    assert result.final_status is EventStatus.IGNORED
    assert result.commands == ()
    assert load_event(database).status is EventStatus.IGNORED
