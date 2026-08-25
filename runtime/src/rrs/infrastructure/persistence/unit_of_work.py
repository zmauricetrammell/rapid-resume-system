"""SQLite UnitOfWork implementation."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from types import TracebackType

from rrs.domain.errors import ConcurrencyConflict, PersistenceFailure
from rrs.domain.ids import JobId
from rrs.infrastructure.persistence.repositories import (
    SQLiteArtifactRepository,
    SQLiteCommandRepository,
    SQLiteEventRepository,
    SQLiteExecutionRepository,
    SQLiteFailureRepository,
    SQLiteInteractionMessageRepository,
    SQLiteInteractionRepository,
    SQLiteInvocationProvenanceRepository,
    SQLiteRoutingDecisionRepository,
    SQLiteRuntimeInstanceRepository,
    SQLiteRuntimeJobRepository,
)


class SQLiteUnitOfWork:
    """Own one SQLite connection and transaction across all repositories."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.connection: sqlite3.Connection | None = None

    async def __aenter__(self) -> SQLiteUnitOfWork:
        try:
            connection = sqlite3.connect(self.database_path)
            connection.execute("PRAGMA foreign_keys=ON;")
            connection.execute("PRAGMA busy_timeout=5000;")
            connection.execute("BEGIN IMMEDIATE;")
        except sqlite3.Error as exc:
            raise PersistenceFailure(
                f"failed to begin SQLite unit of work: {self.database_path}"
            ) from exc

        self.connection = connection
        self.jobs = SQLiteRuntimeJobRepository(connection)
        self.artifacts = SQLiteArtifactRepository(connection)
        self.executions = SQLiteExecutionRepository(connection)
        self.events = SQLiteEventRepository(connection)
        self.commands = SQLiteCommandRepository(connection)
        self.interactions = SQLiteInteractionRepository(connection)
        self.messages = SQLiteInteractionMessageRepository(connection)
        self.failures = SQLiteFailureRepository(connection)
        self.provenance = SQLiteInvocationProvenanceRepository(connection)
        self.runtime_instances = SQLiteRuntimeInstanceRepository(connection)
        self.routing = SQLiteRoutingDecisionRepository(connection)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        try:
            if self.connection is not None and self.connection.in_transaction:
                await self.rollback()
        finally:
            if self.connection is not None:
                self.connection.close()
                self.connection = None

    async def commit(self) -> None:
        connection = self._require_connection()
        try:
            connection.commit()
        except sqlite3.Error as exc:
            raise PersistenceFailure("SQLite commit failed") from exc

    async def rollback(self) -> None:
        connection = self._require_connection()
        try:
            connection.rollback()
        except sqlite3.Error as exc:
            raise PersistenceFailure("SQLite rollback failed") from exc

    def advance_job_revision(
        self,
        job_id: JobId,
        expected_revision: int,
        updated_at: datetime,
    ) -> int:
        """Advance one RuntimeJob revision with compare-and-swap semantics."""
        connection = self._require_connection()
        try:
            cursor = connection.execute(
                """
                UPDATE runtime_jobs
                SET revision = revision + 1,
                    updated_at = ?
                WHERE job_id = ?
                  AND revision = ?
                """,
                (updated_at.isoformat(), str(job_id), expected_revision),
            )
        except sqlite3.Error as exc:
            raise PersistenceFailure("RuntimeJob revision update failed") from exc

        if cursor.rowcount != 1:
            raise ConcurrencyConflict(
                f"RuntimeJob {job_id} revision conflict; "
                f"expected {expected_revision}"
            )
        return expected_revision + 1

    def _require_connection(self) -> sqlite3.Connection:
        if self.connection is None:
            raise PersistenceFailure("UnitOfWork is not active")
        return self.connection


__all__ = ["SQLiteUnitOfWork"]
