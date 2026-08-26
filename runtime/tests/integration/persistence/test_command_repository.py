"""Integration tests for durable Command claim and dedupe semantics."""

import sqlite3
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from rrs.domain.commands import Command
from rrs.domain.enums import CommandStatus
from rrs.domain.ids import CommandId, RuntimeInstanceId
from rrs.domain.provenance import RuntimeInstance
from rrs.infrastructure.persistence.migrations import migrate_database
from rrs.infrastructure.persistence.repositories import (
    SQLiteCommandRepository,
    SQLiteRuntimeInstanceRepository,
)

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)
OWNER_ONE = RuntimeInstanceId("runtime-1")
OWNER_TWO = RuntimeInstanceId("runtime-2")


def migrated_connection(tmp_path: Path) -> sqlite3.Connection:
    database_path = tmp_path / "runtime.db"
    migrations = Path(__file__).resolve().parents[3] / "migrations"
    migrate_database(database_path, migrations)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys=ON")
    runtime_instances = SQLiteRuntimeInstanceRepository(connection)
    for runtime_instance_id in (OWNER_ONE, OWNER_TWO):
        runtime_instances.add(
            RuntimeInstance(
                runtime_instance_id=runtime_instance_id,
                git_sha="git-sha",
                image_digest=None,
                operation_registry_hash="registry-hash",
                built_at=None,
                started_at=NOW,
                stopped_at=None,
            )
        )
    connection.commit()
    return connection


def command(
    command_id: str,
    *,
    created_at: datetime = NOW,
    dedupe_key: str | None = None,
) -> Command:
    return Command(
        command_id=CommandId(command_id),
        command_type="schedule_operation",
        job_id=None,
        payload={"command_id": command_id},
        status=CommandStatus.PENDING,
        dedupe_key=dedupe_key,
        causation_event_id=None,
        owner_runtime_instance_id=None,
        lease_expires_at=None,
        attempt_count=0,
        created_at=created_at,
        completed_at=None,
    )


def test_dedupe_lookup_and_duplicate_constraint(tmp_path: Path) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        original = command("command-1", dedupe_key="schedule:job-1")
        repository.add(original)

        assert repository.get_by_dedupe_key("schedule:job-1") == original
        assert repository.get_by_dedupe_key("missing") is None

        with pytest.raises(sqlite3.IntegrityError):
            repository.add(
                command("command-2", dedupe_key="schedule:job-1")
            )
    finally:
        connection.close()


def test_claim_is_atomic_and_uses_deterministic_order(tmp_path: Path) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        repository.add(command("command-b", created_at=NOW))
        repository.add(command("command-a", created_at=NOW))

        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        next_claim = repository.claim_next(
            OWNER_TWO,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )

        assert claimed is not None
        assert claimed.command_id == CommandId("command-a")
        assert claimed.status is CommandStatus.PROCESSING
        assert claimed.attempt_count == 1
        assert claimed.owner_runtime_instance_id == OWNER_ONE
        assert next_claim is not None
        assert next_claim.command_id == CommandId("command-b")
    finally:
        connection.close()


def test_unexpired_lease_is_renewable_but_not_reclaimable(tmp_path: Path) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        repository.add(command("command-1"))
        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )

        assert claimed is not None
        assert (
            repository.claim_next(
                OWNER_TWO,
                now=NOW + timedelta(minutes=1),
                lease_expires_at=NOW + timedelta(minutes=6),
            )
            is None
        )

        renewed = repository.renew_lease(
            claimed.command_id,
            OWNER_ONE,
            now=NOW + timedelta(minutes=1),
            lease_expires_at=NOW + timedelta(minutes=10),
        )
        assert renewed is not None
        assert renewed.lease_expires_at == NOW + timedelta(minutes=10)
        assert (
            repository.renew_lease(
                claimed.command_id,
                OWNER_TWO,
                now=NOW + timedelta(minutes=2),
                lease_expires_at=NOW + timedelta(minutes=11),
            )
            is None
        )
    finally:
        connection.close()


def test_expired_lease_is_reclaimed_and_attempt_is_incremented(
    tmp_path: Path,
) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        repository.add(command("command-1"))
        first = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        reclaimed = repository.claim_next(
            OWNER_TWO,
            now=NOW + timedelta(minutes=5),
            lease_expires_at=NOW + timedelta(minutes=10),
        )

        assert first is not None
        assert reclaimed is not None
        assert reclaimed.command_id == first.command_id
        assert reclaimed.owner_runtime_instance_id == OWNER_TWO
        assert reclaimed.attempt_count == 2
    finally:
        connection.close()


def test_lease_comparison_uses_absolute_time_across_offsets(
    tmp_path: Path,
) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        repository.add(command("command-1"))
        pacific = timezone(timedelta(hours=-7))
        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=(NOW + timedelta(minutes=5)).astimezone(pacific),
        )

        assert claimed is not None
        assert (
            repository.claim_next(
                OWNER_TWO,
                now=NOW + timedelta(minutes=1),
                lease_expires_at=NOW + timedelta(minutes=6),
            )
            is None
        )
    finally:
        connection.close()


def test_retry_persists_error_and_returns_command_to_claim_queue(
    tmp_path: Path,
) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        repository.add(command("command-1"))
        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        assert claimed is not None

        retry = repository.mark_retry_pending(
            claimed.command_id,
            OWNER_ONE,
            now=NOW + timedelta(minutes=1),
            error="temporary provider failure",
        )
        assert retry is not None
        assert retry.status is CommandStatus.RETRY_PENDING
        assert retry.last_error == "temporary provider failure"
        assert retry.owner_runtime_instance_id is None
        assert retry.lease_expires_at is None

        reclaimed = repository.claim_next(
            OWNER_TWO,
            now=NOW + timedelta(minutes=2),
            lease_expires_at=NOW + timedelta(minutes=7),
        )
        assert reclaimed is not None
        assert reclaimed.attempt_count == 2
        assert reclaimed.last_error is None
    finally:
        connection.close()


@pytest.mark.parametrize(
    ("transition", "expected_status", "error"),
    (
        ("completed", CommandStatus.COMPLETED, None),
        ("failed", CommandStatus.FAILED, "permanent failure"),
        ("cancelled", CommandStatus.CANCELLED, None),
    ),
)
def test_terminal_transitions_release_claim_and_are_not_reclaimable(
    tmp_path: Path,
    transition: str,
    expected_status: CommandStatus,
    error: str | None,
) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        repository.add(command("command-1"))
        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        assert claimed is not None
        completed_at = NOW + timedelta(minutes=1)

        if transition == "completed":
            terminal = repository.mark_completed(
                claimed.command_id,
                OWNER_ONE,
                completed_at=completed_at,
            )
        elif transition == "failed":
            terminal = repository.mark_failed(
                claimed.command_id,
                OWNER_ONE,
                completed_at=completed_at,
                error="permanent failure",
            )
        else:
            terminal = repository.mark_cancelled(
                claimed.command_id,
                OWNER_ONE,
                completed_at=completed_at,
            )

        assert terminal is not None
        assert terminal.status is expected_status
        assert terminal.completed_at == completed_at
        assert terminal.last_error == error
        assert terminal.owner_runtime_instance_id is None
        assert terminal.lease_expires_at is None
        assert (
            repository.claim_next(
                OWNER_TWO,
                now=NOW + timedelta(minutes=2),
                lease_expires_at=NOW + timedelta(minutes=7),
            )
            is None
        )
    finally:
        connection.close()


def test_expired_or_wrong_owner_cannot_finish_claim(tmp_path: Path) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        repository.add(command("command-1"))
        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        assert claimed is not None

        assert (
            repository.mark_completed(
                claimed.command_id,
                OWNER_TWO,
                completed_at=NOW + timedelta(minutes=1),
            )
            is None
        )
        assert (
            repository.mark_completed(
                claimed.command_id,
                OWNER_ONE,
                completed_at=NOW + timedelta(minutes=5),
            )
            is None
        )
    finally:
        connection.close()


def test_claim_and_transition_validate_time_and_error_inputs(
    tmp_path: Path,
) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteCommandRepository(connection)
        repository.add(command("command-1"))
        with pytest.raises(ValueError, match="timezone-aware"):
            repository.claim_next(
                OWNER_ONE,
                now=datetime(2026, 8, 25, 12, 0),
                lease_expires_at=NOW + timedelta(minutes=5),
            )
        with pytest.raises(ValueError, match="later than now"):
            repository.claim_next(
                OWNER_ONE,
                now=NOW,
                lease_expires_at=NOW,
            )

        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        assert claimed is not None
        with pytest.raises(ValueError, match="nonempty"):
            repository.mark_retry_pending(
                claimed.command_id,
                OWNER_ONE,
                now=NOW + timedelta(minutes=1),
                error="",
            )
    finally:
        connection.close()

