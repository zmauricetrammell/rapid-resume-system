from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from rrs.infrastructure.persistence.migrations import (
    MigrationError,
    discover_migrations,
    migrate_database,
    validate_database_pragmas,
)


def repo_migrations() -> Path:
    return Path(__file__).resolve().parents[4] / "migrations"


def test_discover_migrations_are_strictly_ordered() -> None:
    items = discover_migrations(repo_migrations())
    assert [item.version for item in items] == ["0001", "0002", "0003"]


def test_empty_database_migrates_and_records_history(tmp_path: Path) -> None:
    database = tmp_path / "rrs.db"

    applied = migrate_database(database, repo_migrations())

    assert applied == ("0001", "0002", "0003")

    connection = sqlite3.connect(database)
    try:
        versions = [
            row[0]
            for row in connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            )
        ]
        assert versions == ["0001", "0002", "0003"]

        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {
            "runtime_instances",
            "runtime_jobs",
            "artifacts",
            "executions",
            "events",
            "commands",
            "interactions",
            "interaction_messages",
            "failures",
            "invocation_provenance",
        }.issubset(tables)
    finally:
        connection.close()


def test_migration_runner_is_idempotent(tmp_path: Path) -> None:
    database = tmp_path / "rrs.db"

    assert migrate_database(database, repo_migrations()) == (
        "0001",
        "0002",
        "0003",
    )
    assert migrate_database(database, repo_migrations()) == ()


def test_wal_and_foreign_keys_are_effective(tmp_path: Path) -> None:
    database = tmp_path / "rrs.db"
    migrate_database(database, repo_migrations())

    validate_database_pragmas(database)


def test_foreign_key_enforcement_is_available_on_runtime_connection(
    tmp_path: Path,
) -> None:
    database = tmp_path / "rrs.db"
    migrate_database(database, repo_migrations())

    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO job_artifact_pointers(
                    job_id, pointer_type, artifact_id, artifact_version
                ) VALUES ('missing-job', 'jea', 'missing-artifact', 1)
                """
            )
    finally:
        connection.close()


def test_partial_unique_active_execution_index_is_enforced(tmp_path: Path) -> None:
    database = tmp_path / "rrs.db"
    migrate_database(database, repo_migrations())

    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        connection.execute(
            """
            INSERT INTO runtime_instances(
                runtime_instance_id, git_sha, operation_registry_hash, started_at
            ) VALUES ('runtime-1', 'git', 'registry', '2026-08-25T00:00:00+00:00')
            """
        )
        connection.execute(
            """
            INSERT INTO runtime_jobs(
                job_id, revision, lifecycle_phase, lifecycle_entered_at,
                operation_status, interaction_status, health_status,
                health_retry_count, created_at, updated_at
            ) VALUES (
                'job-1', 1, 'analysis', '2026-08-25T00:00:00+00:00',
                'idle', 'none', 'healthy', 0,
                '2026-08-25T00:00:00+00:00',
                '2026-08-25T00:00:00+00:00'
            )
            """
        )
        statement = """
            INSERT INTO executions(
                execution_id, job_id, owner_runtime_instance_id,
                operation_type, operation_key, attempt_number, status,
                input_snapshot_json, created_at
            ) VALUES (?, 'job-1', 'runtime-1', 'generate_analysis',
                      'same-operation', ?, ?, '{}',
                      '2026-08-25T00:00:00+00:00')
        """
        connection.execute(statement, ("execution-1", 1, "running"))
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(statement, ("execution-2", 2, "queued"))
    finally:
        connection.close()


def test_interaction_one_active_per_job_index_is_enforced(tmp_path: Path) -> None:
    database = tmp_path / "rrs.db"
    migrate_database(database, repo_migrations())

    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        connection.execute(
            """
            INSERT INTO runtime_jobs(
                job_id, revision, lifecycle_phase, lifecycle_entered_at,
                operation_status, interaction_status, health_status,
                health_retry_count, created_at, updated_at
            ) VALUES (
                'job-1', 1, 'investigation', '2026-08-25T00:00:00+00:00',
                'idle', 'none', 'healthy', 0,
                '2026-08-25T00:00:00+00:00',
                '2026-08-25T00:00:00+00:00'
            )
            """
        )
        statement = """
            INSERT INTO interactions(
                interaction_id, job_id, interaction_type, provider,
                provider_context_json, professional_context_json,
                status, created_at, updated_at
            ) VALUES (?, 'job-1', 'evidence_investigation', 'discord',
                      '{}', '{}', ?, '2026-08-25T00:00:00+00:00',
                      '2026-08-25T00:00:00+00:00')
        """
        connection.execute(statement, ("interaction-1", "active"))
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(statement, ("interaction-2", "pending"))
    finally:
        connection.close()


def test_failed_migration_rolls_back_and_blocks_readiness(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "0001_good.sql").write_text(
        "CREATE TABLE good_table(id TEXT PRIMARY KEY);",
        encoding="utf-8",
    )
    (migrations / "0002_bad.sql").write_text(
        "CREATE TABLE partial_table(id TEXT); THIS IS INVALID SQL;",
        encoding="utf-8",
    )
    database = tmp_path / "rrs.db"

    with pytest.raises(MigrationError, match="0002"):
        migrate_database(database, migrations)

    connection = sqlite3.connect(database)
    try:
        versions = {
            row[0]
            for row in connection.execute("SELECT version FROM schema_migrations")
        }
        assert versions == {"0001"}
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "partial_table" not in tables
    finally:
        connection.close()


def test_missing_or_invalid_migration_directory_fails(tmp_path: Path) -> None:
    with pytest.raises(MigrationError, match="does not exist"):
        discover_migrations(tmp_path / "missing")

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(MigrationError, match="no SQL migrations"):
        discover_migrations(empty)

def test_non_numeric_migration_version_is_rejected(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "alpha_bad.sql").write_text(
        "CREATE TABLE example(id TEXT);",
        encoding="utf-8",
    )

    with pytest.raises(MigrationError, match="numeric"):
        discover_migrations(migrations)


def test_duplicate_migration_version_is_rejected(tmp_path: Path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "0001_first.sql").write_text(
        "CREATE TABLE first_table(id TEXT);",
        encoding="utf-8",
    )
    (migrations / "0001_second.sql").write_text(
        "CREATE TABLE second_table(id TEXT);",
        encoding="utf-8",
    )

    with pytest.raises(MigrationError, match="duplicate"):
        discover_migrations(migrations)


def test_database_open_failure_is_normalized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_connect(*args: object, **kwargs: object) -> sqlite3.Connection:
        raise sqlite3.OperationalError("cannot open")

    monkeypatch.setattr(sqlite3, "connect", fail_connect)

    with pytest.raises(MigrationError, match="cannot open database"):
        migrate_database(
            tmp_path / "rrs.db",
            repo_migrations(),
        )