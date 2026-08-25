from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import Coroutine
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from rrs.domain.artifacts import ArtifactMetadata, ArtifactVersion
from rrs.domain.enums import ArtifactRuntimeStatus, ArtifactType
from rrs.domain.errors import ConcurrencyConflict, PersistenceFailure
from rrs.domain.ids import ArtifactId, JobId
from rrs.infrastructure.persistence.migrations import migrate_database
from rrs.infrastructure.persistence.unit_of_work import SQLiteUnitOfWork

NOW = datetime(2026, 8, 25, 21, 0, tzinfo=UTC)

def migrations() -> Path:
    return Path(__file__).resolve().parents[4] / "migrations"


def migrated_database(tmp_path: Path) -> Path:
    database = tmp_path / "rrs.db"
    migrate_database(database, migrations())
    return database


def run(coro: Coroutine[Any, Any, object]) -> object:
    return asyncio.run(coro)


def insert_minimal_job(database: Path, revision: int = 1) -> None:
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            """
            INSERT INTO runtime_jobs(
                job_id, revision, lifecycle_phase, lifecycle_entered_at,
                operation_status, interaction_status, health_status,
                health_retry_count, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "job-1",
                revision,
                "analysis",
                NOW.isoformat(),
                "idle",
                "none",
                "healthy",
                0,
                NOW.isoformat(),
                NOW.isoformat(),
            ),
        )
        connection.commit()
    finally:
        connection.close()


class FailingTransactionConnection(sqlite3.Connection):
    fail_commit = False
    fail_rollback = False

    def commit(self) -> None:
        if self.fail_commit:
            raise sqlite3.OperationalError("commit failed")
        super().commit()

    def rollback(self) -> None:
        if self.fail_rollback:
            raise sqlite3.OperationalError("rollback failed")
        super().rollback()


def test_all_repositories_share_one_transaction_connection(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)

    async def scenario() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            assert uow.connection is not None
            assert uow.jobs.connection is uow.connection
            assert uow.artifacts.connection is uow.connection
            assert uow.executions.connection is uow.connection
            assert uow.events.connection is uow.connection
            assert uow.commands.connection is uow.connection
            assert uow.interactions.connection is uow.connection
            assert uow.messages.connection is uow.connection
            assert uow.failures.connection is uow.connection
            assert uow.provenance.connection is uow.connection
            assert uow.runtime_instances.connection is uow.connection
            assert uow.routing.connection is uow.connection

    run(scenario())


def test_multiple_repository_writes_commit_together(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)

    async def scenario() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            assert uow.connection is not None
            uow.artifacts.add(
                ArtifactMetadata(
                    artifact_id=ArtifactId("artifact-1"),
                    artifact_version=ArtifactVersion(1),
                    artifact_type=ArtifactType.TARGET_JOB,
                    storage_uri="file:///artifact-1",
                    content_hash="sha256:artifact-1",
                    committed_by_execution_id=None,
                    operation_key=None,
                    committed_at=NOW,
                    runtime_status=ArtifactRuntimeStatus.COMMITTED,
                ),
                created_at=NOW.isoformat(),
            )
            uow.connection.execute(
                """
                INSERT INTO runtime_jobs(
                    job_id, revision, lifecycle_phase, lifecycle_entered_at,
                    operation_status, interaction_status, health_status,
                    health_retry_count, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "job-1",
                    1,
                    "analysis",
                    NOW.isoformat(),
                    "idle",
                    "none",
                    "healthy",
                    0,
                    NOW.isoformat(),
                    NOW.isoformat(),
                ),
            )
            await uow.commit()

    run(scenario())

    observer = sqlite3.connect(database)
    try:
        assert observer.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0] == 1
        assert observer.execute("SELECT COUNT(*) FROM runtime_jobs").fetchone()[0] == 1
    finally:
        observer.close()


def test_rollback_restores_all_repository_writes(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)

    async def scenario() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            assert uow.connection is not None
            uow.artifacts.add(
                ArtifactMetadata(
                    artifact_id=ArtifactId("artifact-1"),
                    artifact_version=ArtifactVersion(1),
                    artifact_type=ArtifactType.TARGET_JOB,
                    storage_uri="file:///artifact-1",
                    content_hash="sha256:artifact-1",
                    committed_by_execution_id=None,
                    operation_key=None,
                    committed_at=NOW,
                    runtime_status=ArtifactRuntimeStatus.COMMITTED,
                ),
                created_at=NOW.isoformat(),
            )
            await uow.rollback()

    run(scenario())

    observer = sqlite3.connect(database)
    try:
        assert observer.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0] == 0
    finally:
        observer.close()


def test_context_exit_rolls_back_uncommitted_work(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)

    async def scenario() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            uow.connection.execute(
                """
                INSERT INTO runtime_jobs(
                    job_id, revision, lifecycle_phase, lifecycle_entered_at,
                    operation_status, interaction_status, health_status,
                    health_retry_count, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "job-1",
                    1,
                    "analysis",
                    NOW.isoformat(),
                    "idle",
                    "none",
                    "healthy",
                    0,
                    NOW.isoformat(),
                    NOW.isoformat(),
                ),
            )

    run(scenario())

    observer = sqlite3.connect(database)
    try:
        assert observer.execute("SELECT COUNT(*) FROM runtime_jobs").fetchone()[0] == 0
    finally:
        observer.close()


def test_repository_write_is_not_autocommitted(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)

    async def scenario() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            assert uow.connection is not None
            uow.artifacts.add(
                ArtifactMetadata(
                    artifact_id=ArtifactId("artifact-1"),
                    artifact_version=ArtifactVersion(1),
                    artifact_type=ArtifactType.TARGET_JOB,
                    storage_uri="file:///artifact-1",
                    content_hash="sha256:artifact-1",
                    committed_by_execution_id=None,
                    operation_key=None,
                    committed_at=NOW,
                    runtime_status=ArtifactRuntimeStatus.COMMITTED,
                ),
                created_at=NOW.isoformat(),
            )
            observer = sqlite3.connect(database)
            try:
                assert observer.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0] == 0
            finally:
                observer.close()
            await uow.commit()

    run(scenario())


def test_compare_and_swap_maps_stale_revision_to_conflict(tmp_path: Path) -> None:
    database = migrated_database(tmp_path)
    insert_minimal_job(database)

    async def first_update() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            assert uow.advance_job_revision(JobId("job-1"), 1, NOW) == 2
            await uow.commit()

    async def stale_update() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            with pytest.raises(ConcurrencyConflict, match="expected 1"):
                uow.advance_job_revision(JobId("job-1"), 1, NOW)

    run(first_update())
    run(stale_update())


def test_inactive_unit_of_work_rejects_transaction_methods(tmp_path: Path) -> None:
    uow = SQLiteUnitOfWork(tmp_path / "rrs.db")

    with pytest.raises(PersistenceFailure, match="not active"):
        run(uow.commit())

    with pytest.raises(PersistenceFailure, match="not active"):
        uow.advance_job_revision(JobId("job-1"), 1, NOW)

def test_begin_failure_is_normalized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_connect(*args: object, **kwargs: object) -> sqlite3.Connection:
        raise sqlite3.OperationalError("open failed")

    monkeypatch.setattr(sqlite3, "connect", fail_connect)

    async def scenario() -> None:
        with pytest.raises(
            PersistenceFailure,
            match="failed to begin SQLite unit of work",
        ):
            async with SQLiteUnitOfWork(tmp_path / "rrs.db"):
                pass

    run(scenario())


def test_commit_failure_is_normalized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = migrated_database(tmp_path)
    real_connect = sqlite3.connect

    def connect_with_failing_connection(
        *args: object,
        **kwargs: object,
    ) -> sqlite3.Connection:
        kwargs["factory"] = FailingTransactionConnection
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", connect_with_failing_connection)

    async def scenario() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            assert isinstance(uow.connection, FailingTransactionConnection)
            uow.connection.fail_commit = True

            with pytest.raises(
                PersistenceFailure,
                match="SQLite commit failed",
            ):
                await uow.commit()

    run(scenario())


def test_rollback_failure_is_normalized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = migrated_database(tmp_path)
    real_connect = sqlite3.connect

    def connect_with_failing_connection(
        *args: object,
        **kwargs: object,
    ) -> sqlite3.Connection:
        kwargs["factory"] = FailingTransactionConnection
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", connect_with_failing_connection)

    async def scenario() -> None:
        uow = SQLiteUnitOfWork(database)
        await uow.__aenter__()

        assert isinstance(uow.connection, FailingTransactionConnection)
        uow.connection.fail_rollback = True

        with pytest.raises(
            PersistenceFailure,
            match="SQLite rollback failed",
        ):
            await uow.rollback()

        uow.connection.close()
        uow.connection = None

    run(scenario())


def test_revision_update_sql_error_is_normalized(
    tmp_path: Path,
) -> None:
    database = migrated_database(tmp_path)
    insert_minimal_job(database)

    async def scenario() -> None:
        async with SQLiteUnitOfWork(database) as uow:
            assert uow.connection is not None

            uow.connection.execute("DROP TABLE runtime_jobs")

            with pytest.raises(
                PersistenceFailure,
                match="RuntimeJob revision update failed",
            ):
                uow.advance_job_revision(
                    JobId("job-1"),
                    1,
                    NOW,
                )

    run(scenario())

