"""Integration tests for durable Event claim and recovery semantics."""

import sqlite3
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from rrs.domain.enums import EventCriticality, EventStatus
from rrs.domain.events import Event, EventSource
from rrs.domain.ids import EventId, RuntimeInstanceId
from rrs.domain.provenance import RuntimeInstance
from rrs.infrastructure.persistence.migrations import migrate_database
from rrs.infrastructure.persistence.repositories import (
    SQLiteEventRepository,
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


def event(
    event_id: str,
    *,
    created_at: datetime = NOW,
    provider_event_id: str | None = None,
) -> Event:
    return Event(
        event_id=EventId(event_id),
        event_type="provider.message",
        job_id=None,
        payload={"event_id": event_id},
        source=EventSource("provider", "discord", provider_event_id),
        correlation_id=None,
        causation_id=None,
        criticality=EventCriticality.WORKFLOW_CRITICAL,
        status=EventStatus.RECEIVED,
        attempt_count=0,
        owner_runtime_instance_id=None,
        lease_expires_at=None,
        created_at=created_at,
        processed_at=None,
    )


def test_provider_identity_lookup_and_duplicate_constraint(tmp_path: Path) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteEventRepository(connection)
        original = event("event-1", provider_event_id="delivery-1")
        repository.add(original)

        assert (
            repository.get_by_provider_identity("discord", "delivery-1")
            == original
        )
        assert (
            repository.get_by_provider_identity("discord", "missing")
            is None
        )

        with pytest.raises(sqlite3.IntegrityError):
            repository.add(event("event-2", provider_event_id="delivery-1"))
    finally:
        connection.close()


def test_claim_is_atomic_and_uses_deterministic_order(tmp_path: Path) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteEventRepository(connection)
        repository.add(event("event-b", created_at=NOW))
        repository.add(event("event-a", created_at=NOW))

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
        assert claimed.event_id == EventId("event-a")
        assert claimed.status is EventStatus.PROCESSING
        assert claimed.attempt_count == 1
        assert claimed.owner_runtime_instance_id == OWNER_ONE
        assert next_claim is not None
        assert next_claim.event_id == EventId("event-b")
    finally:
        connection.close()


def test_unexpired_lease_is_renewable_but_not_reclaimable(tmp_path: Path) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteEventRepository(connection)
        repository.add(event("event-1"))
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
            claimed.event_id,
            OWNER_ONE,
            now=NOW + timedelta(minutes=1),
            lease_expires_at=NOW + timedelta(minutes=10),
        )
        assert renewed is not None
        assert renewed.lease_expires_at == NOW + timedelta(minutes=10)
        assert (
            repository.renew_lease(
                claimed.event_id,
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
        repository = SQLiteEventRepository(connection)
        repository.add(event("event-1"))
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
        assert reclaimed.event_id == first.event_id
        assert reclaimed.owner_runtime_instance_id == OWNER_TWO
        assert reclaimed.attempt_count == 2
    finally:
        connection.close()


def test_lease_comparison_uses_absolute_time_across_offsets(
    tmp_path: Path,
) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteEventRepository(connection)
        repository.add(event("event-1"))
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


def test_retry_persists_error_and_returns_event_to_claim_queue(
    tmp_path: Path,
) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteEventRepository(connection)
        repository.add(event("event-1"))
        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        assert claimed is not None

        retry = repository.mark_retry_pending(
            claimed.event_id,
            OWNER_ONE,
            now=NOW + timedelta(minutes=1),
            error="temporary provider failure",
        )
        assert retry is not None
        assert retry.status is EventStatus.RETRY_PENDING
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
        ("processed", EventStatus.PROCESSED, None),
        ("ignored", EventStatus.IGNORED, None),
        ("dead_letter", EventStatus.DEAD_LETTER, "invalid payload"),
    ),
)
def test_terminal_transitions_release_claim_and_are_not_reclaimable(
    tmp_path: Path,
    transition: str,
    expected_status: EventStatus,
    error: str | None,
) -> None:
    connection = migrated_connection(tmp_path)
    try:
        repository = SQLiteEventRepository(connection)
        repository.add(event("event-1"))
        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        assert claimed is not None
        processed_at = NOW + timedelta(minutes=1)

        if transition == "processed":
            terminal = repository.mark_processed(
                claimed.event_id,
                OWNER_ONE,
                processed_at=processed_at,
            )
        elif transition == "ignored":
            terminal = repository.mark_ignored(
                claimed.event_id,
                OWNER_ONE,
                processed_at=processed_at,
            )
        else:
            terminal = repository.mark_dead_letter(
                claimed.event_id,
                OWNER_ONE,
                processed_at=processed_at,
                error="invalid payload",
            )

        assert terminal is not None
        assert terminal.status is expected_status
        assert terminal.processed_at == processed_at
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
        repository = SQLiteEventRepository(connection)
        repository.add(event("event-1"))
        claimed = repository.claim_next(
            OWNER_ONE,
            now=NOW,
            lease_expires_at=NOW + timedelta(minutes=5),
        )
        assert claimed is not None

        assert (
            repository.mark_processed(
                claimed.event_id,
                OWNER_TWO,
                processed_at=NOW + timedelta(minutes=1),
            )
            is None
        )
        assert (
            repository.mark_processed(
                claimed.event_id,
                OWNER_ONE,
                processed_at=NOW + timedelta(minutes=5),
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
        repository = SQLiteEventRepository(connection)
        repository.add(event("event-1"))
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
                claimed.event_id,
                OWNER_ONE,
                now=NOW + timedelta(minutes=1),
                error="",
            )
    finally:
        connection.close()
