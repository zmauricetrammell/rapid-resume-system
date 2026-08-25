"""SQLite migration runner for the RRS runtime."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


class MigrationError(RuntimeError):
    """Raised when migration discovery or application fails."""


@dataclass(frozen=True, order=True)
class Migration:
    version: str
    path: Path


def discover_migrations(directory: Path) -> tuple[Migration, ...]:
    if not directory.exists() or not directory.is_dir():
        raise MigrationError(f"migration directory does not exist: {directory}")
    items = tuple(
        Migration(path.name.split("_", 1)[0], path)
        for path in sorted(directory.glob("*.sql"))
    )
    if not items:
        raise MigrationError("no SQL migrations found")
    versions = [item.version for item in items]
    if any(not version.isdigit() for version in versions):
        raise MigrationError("migration versions must be numeric")
    if len(set(versions)) != len(versions):
        raise MigrationError("duplicate migration version")
    return items


def _configure_connection(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA foreign_keys=ON;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    connection.execute("PRAGMA busy_timeout=5000;")


def _ensure_history_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )


def _applied_versions(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT version FROM schema_migrations ORDER BY version"
    ).fetchall()
    return {str(row[0]) for row in rows}


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _apply_migration(connection: sqlite3.Connection, migration: Migration) -> None:
    sql = migration.path.read_text(encoding="utf-8")
    applied_at = datetime.now(UTC).isoformat()
    script = (
        "BEGIN IMMEDIATE;\n"
        + sql
        + "\nINSERT INTO schema_migrations(version, applied_at) VALUES ("
        + _sql_literal(migration.version)
        + ", "
        + _sql_literal(applied_at)
        + ");\nCOMMIT;"
    )
    try:
        connection.executescript(script)
    except Exception as exc:
        connection.rollback()
        raise MigrationError(
            f"migration {migration.version} failed: {migration.path.name}"
        ) from exc


def migrate_database(
    database_path: Path,
    migrations_directory: Path,
) -> tuple[str, ...]:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    migrations = discover_migrations(migrations_directory)
    try:
        connection = sqlite3.connect(database_path)
    except sqlite3.Error as exc:
        raise MigrationError(f"cannot open database: {database_path}") from exc
    try:
        _configure_connection(connection)
        _ensure_history_table(connection)
        connection.commit()
        applied = _applied_versions(connection)
        newly_applied: list[str] = []
        for migration in migrations:
            if migration.version in applied:
                continue
            _apply_migration(connection, migration)
            newly_applied.append(migration.version)
        return tuple(newly_applied)
    finally:
        connection.close()


def validate_database_pragmas(database_path: Path) -> None:
    connection = sqlite3.connect(database_path)
    try:
        journal_mode = str(
            connection.execute("PRAGMA journal_mode").fetchone()[0]
        ).lower()
        connection.execute("PRAGMA foreign_keys=ON;")
        foreign_keys = int(connection.execute("PRAGMA foreign_keys").fetchone()[0])
        if journal_mode != "wal":
            raise MigrationError("SQLite WAL mode is not enabled")
        if foreign_keys != 1:
            raise MigrationError("SQLite foreign keys are not enabled")
    finally:
        connection.close()


__all__ = [
    "Migration",
    "MigrationError",
    "discover_migrations",
    "migrate_database",
    "validate_database_pragmas",
]
