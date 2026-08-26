"""SQLite repository implementations for RRS domain records."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from rrs.domain.artifacts import (
    ArtifactMetadata,
    ArtifactRef,
    ArtifactVersion,
    StagedArtifact,
)
from rrs.domain.commands import Command
from rrs.domain.enums import (
    ArtifactRuntimeStatus,
    ArtifactType,
    CommandStatus,
    EventCriticality,
    EventStatus,
    ExecutionStatus,
    FailureClass,
    HealthStatus,
    InteractionProjectionStatus,
    InteractionStatus,
    InteractionType,
    LifecyclePhase,
    OperationType,
    RuntimeOperationStatus,
)
from rrs.domain.events import Event, EventSource
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
    OperationKey,
    RoutingDecisionId,
    RuntimeInstanceId,
)
from rrs.domain.interactions import Interaction, InteractionMessage
from rrs.domain.jobs import (
    HealthState,
    InteractionProjection,
    LifecycleState,
    OperationState,
    ProfessionalState,
    RuntimeJob,
    RuntimeJobIdentity,
)
from rrs.domain.operations import DependencyFingerprint, InputSnapshot
from rrs.domain.provenance import InvocationProvenance, RuntimeInstance
from rrs.domain.routing import RoutingDecision, RoutingPredicateResult


def _dt(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value)


def _text(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


def _artifact_ref_dict(ref: ArtifactRef) -> dict[str, object]:
    return {
        "artifact_type": ref.artifact_type.value,
        "artifact_id": str(ref.artifact_id),
        "artifact_version": ref.artifact_version.value,
        "uri": ref.uri,
    }


def _artifact_ref(value: dict[str, object]) -> ArtifactRef:
    return ArtifactRef(
        artifact_type=ArtifactType(str(value["artifact_type"])),
        artifact_id=ArtifactId(str(value["artifact_id"])),
        artifact_version=ArtifactVersion(
            int(str(value["artifact_version"]))
        ),
        uri=str(value["uri"]),
    )


def _snapshot_json(snapshot: InputSnapshot) -> str:
    def encode(items: tuple[DependencyFingerprint, ...]) -> list[dict[str, str]]:
        return [
            {
                "dependency_type": item.dependency_type,
                "logical_name": item.logical_name,
                "identity": item.identity,
            }
            for item in items
        ]

    return json.dumps(
        {
            "identity_dependencies": encode(snapshot.identity_dependencies),
            "freshness_dependencies": encode(snapshot.freshness_dependencies),
        },
        sort_keys=True,
    )


def _snapshot(value: str) -> InputSnapshot:
    data = json.loads(value)

    def decode(items: list[dict[str, str]]) -> tuple[DependencyFingerprint, ...]:
        return tuple(
            DependencyFingerprint(
                dependency_type=item["dependency_type"],
                logical_name=item["logical_name"],
                identity=item["identity"],
            )
            for item in items
        )

    return InputSnapshot(
        identity_dependencies=decode(data["identity_dependencies"]),
        freshness_dependencies=decode(data["freshness_dependencies"]),
    )


class SQLiteArtifactRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, metadata: ArtifactMetadata, *, created_at: str) -> None:
        self.connection.execute(
            """
            INSERT INTO artifacts(
                artifact_id, artifact_version, artifact_type, storage_uri,
                content_hash, runtime_status, committed_by_execution_id,
                operation_key, committed_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(metadata.artifact_id),
                metadata.artifact_version.value,
                metadata.artifact_type.value,
                metadata.storage_uri,
                metadata.content_hash,
                metadata.runtime_status.value,
                metadata.committed_by_execution_id,
                metadata.operation_key,
                _text(metadata.committed_at),
                created_at,
            ),
        )

    def get(self, artifact_id: ArtifactId, version: int) -> ArtifactMetadata | None:
        row = self.connection.execute(
            """
            SELECT artifact_id, artifact_version, artifact_type, storage_uri,
                   content_hash, committed_by_execution_id, operation_key,
                   committed_at, runtime_status
            FROM artifacts
            WHERE artifact_id = ? AND artifact_version = ?
            """,
            (str(artifact_id), version),
        ).fetchone()
        if row is None:
            return None
        return ArtifactMetadata(
            artifact_id=ArtifactId(row[0]),
            artifact_version=ArtifactVersion(row[1]),
            artifact_type=ArtifactType(row[2]),
            storage_uri=row[3],
            content_hash=row[4],
            committed_by_execution_id=(
                None if row[5] is None else ExecutionId(row[5])
            ),
            operation_key=None if row[6] is None else OperationKey(row[6]),
            committed_at=_dt(row[7]),
            runtime_status=ArtifactRuntimeStatus(row[8]),
        )

    def ref(self, artifact_id: ArtifactId, version: int) -> ArtifactRef | None:
        row = self.connection.execute(
            """
            SELECT artifact_type, storage_uri
            FROM artifacts
            WHERE artifact_id = ? AND artifact_version = ?
            """,
            (str(artifact_id), version),
        ).fetchone()
        if row is None:
            return None
        return ArtifactRef(
            artifact_type=ArtifactType(row[0]),
            artifact_id=artifact_id,
            artifact_version=ArtifactVersion(version),
            uri=row[1],
        )


class SQLiteRuntimeInstanceRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, item: RuntimeInstance) -> None:
        self.connection.execute(
            """
            INSERT INTO runtime_instances(
                runtime_instance_id, git_sha, image_digest,
                operation_registry_hash, built_at, started_at, stopped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.runtime_instance_id),
                item.git_sha,
                item.image_digest,
                item.operation_registry_hash,
                _text(item.built_at),
                _text(item.started_at),
                _text(item.stopped_at),
            ),
        )

    def get(self, runtime_instance_id: RuntimeInstanceId) -> RuntimeInstance | None:
        row = self.connection.execute(
            """
            SELECT runtime_instance_id, git_sha, image_digest,
                   operation_registry_hash, built_at, started_at, stopped_at
            FROM runtime_instances WHERE runtime_instance_id = ?
            """,
            (str(runtime_instance_id),),
        ).fetchone()
        if row is None:
            return None
        return RuntimeInstance(
            runtime_instance_id=RuntimeInstanceId(row[0]),
            git_sha=row[1],
            image_digest=row[2],
            operation_registry_hash=row[3],
            built_at=_dt(row[4]),
            started_at=_dt(row[5]),  # type: ignore[arg-type]
            stopped_at=_dt(row[6]),
        )


class SQLiteExecutionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, item: Execution) -> None:
        staged = [
            {
                "artifact_type": value.artifact_type.value,
                "execution_id": str(value.execution_id),
                "staged_path": value.staged_path,
                "content_hash": value.content_hash,
                "media_type": value.media_type,
            }
            for value in item.staged_outputs
        ]
        committed = [_artifact_ref_dict(value) for value in item.committed_outputs]
        self.connection.execute(
            """
            INSERT INTO executions(
                execution_id, job_id, owner_runtime_instance_id,
                operation_type, operation_key, attempt_number, status,
                input_snapshot_json, staged_outputs_json, committed_outputs_json,
                failure_id, created_at, started_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.execution_id),
                str(item.job_id),
                str(item.owner_runtime_instance_id),
                item.operation_type.value,
                str(item.operation_key),
                item.attempt_number,
                item.status.value,
                _snapshot_json(item.input_snapshot),  # type: ignore[arg-type]
                json.dumps(staged, sort_keys=True),
                json.dumps(committed, sort_keys=True),
                item.failure_id,
                _text(item.created_at),
                _text(item.started_at),
                _text(item.completed_at),
            ),
        )

    def get(self, execution_id: ExecutionId) -> Execution | None:
        row = self.connection.execute(
            "SELECT * FROM executions WHERE execution_id = ?",
            (str(execution_id),),
        ).fetchone()
        if row is None:
            return None
        staged_data = json.loads(row[8])
        staged = tuple(
            StagedArtifact(
                artifact_type=ArtifactType(value["artifact_type"]),
                execution_id=ExecutionId(value["execution_id"]),
                staged_path=value["staged_path"],
                content_hash=value["content_hash"],
                media_type=value["media_type"],
            )
            for value in staged_data
        )
        committed = tuple(_artifact_ref(value) for value in json.loads(row[9]))
        return Execution(
            execution_id=ExecutionId(row[0]),
            job_id=JobId(row[1]),
            owner_runtime_instance_id=RuntimeInstanceId(row[2]),
            operation_type=OperationType(row[3]),
            operation_key=OperationKey(row[4]),
            attempt_number=row[5],
            status=ExecutionStatus(row[6]),
            input_snapshot=_snapshot(row[7]),
            staged_outputs=staged,
            committed_outputs=committed,
            failure_id=None if row[10] is None else FailureId(row[10]),
            created_at=_dt(row[11]),  # type: ignore[arg-type]
            started_at=_dt(row[12]),
            completed_at=_dt(row[13]),
        )
    
    def get_by_operation_key(
        self,
        operation_key: OperationKey,
        ) -> tuple[Execution, ...]:
        rows = self.connection.execute(
            """
            SELECT execution_id
            FROM executions
            WHERE operation_key = ?
            ORDER BY attempt_number, execution_id
            """,
            (str(operation_key),),
        ).fetchall()

        executions: list[Execution] = []
        for row in rows:
            execution = self.get(ExecutionId(row[0]))
            if execution is not None:
                executions.append(execution)

        return tuple(executions)

    def get_active_by_operation_key(
        self,
        operation_key: OperationKey,
    ) -> Execution | None:
        row = self.connection.execute(
            """
            SELECT execution_id
            FROM executions
            WHERE operation_key = ?
            AND status NOT IN ('stale', 'committed', 'failed', 'cancelled')
            ORDER BY attempt_number DESC, execution_id
            LIMIT 1
            """,
            (str(operation_key),),
        ).fetchone()

        if row is None:
            return None

        return self.get(ExecutionId(row[0]))


class SQLiteEventRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    @staticmethod
    def _validate_lease_window(
        now: datetime,
        lease_expires_at: datetime,
    ) -> None:
        for value, field_name in (
            (now, "now"),
            (lease_expires_at, "lease_expires_at"),
        ):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{field_name} must be timezone-aware")
        if lease_expires_at <= now:
            raise ValueError("lease_expires_at must be later than now")

    @staticmethod
    def _require_aware(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")

    def _event_from_returning(
        self,
        row: tuple[object, ...] | None,
    ) -> Event | None:
        if row is None:
            return None
        return self.get(EventId(str(row[0])))

    def add(self, item: Event) -> None:
        self.connection.execute(
            """
            INSERT INTO events(
                event_id, event_type, job_id, payload_json,
                source_category, source_provider, provider_event_id,
                correlation_id, causation_id, criticality, status,
                attempt_count, last_error, owner_runtime_instance_id,
                lease_expires_at, created_at, processed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.event_id),
                item.event_type,
                item.job_id,
                json.dumps(dict(item.payload), sort_keys=True),
                item.source.category,
                item.source.provider,
                item.source.provider_event_id,
                item.correlation_id,
                item.causation_id,
                item.criticality.value,
                item.status.value,
                item.attempt_count,
                item.last_error,
                item.owner_runtime_instance_id,
                _text(item.lease_expires_at),
                _text(item.created_at),
                _text(item.processed_at),
            ),
        )

    def get(self, event_id: EventId) -> Event | None:
        row = self.connection.execute(
            """
            SELECT event_id, event_type, job_id, payload_json,
                   source_category, source_provider, provider_event_id,
                   correlation_id, causation_id, criticality, status,
                   attempt_count, last_error, owner_runtime_instance_id,
                   lease_expires_at, created_at, processed_at
            FROM events WHERE event_id = ?
            """,
            (str(event_id),),
        ).fetchone()
        if row is None:
            return None
        return Event(
            event_id=EventId(row[0]),
            event_type=row[1],
            job_id=None if row[2] is None else JobId(row[2]),
            payload=json.loads(row[3]),
            source=EventSource(row[4], row[5], row[6]),
            correlation_id=row[7],
            causation_id=None if row[8] is None else EventId(row[8]),
            criticality=EventCriticality(row[9]),
            status=EventStatus(row[10]),
            attempt_count=row[11],
            last_error=row[12],
            owner_runtime_instance_id=(
                None if row[13] is None else RuntimeInstanceId(row[13])
            ),
            lease_expires_at=_dt(row[14]),
            created_at=_dt(row[15]),  # type: ignore[arg-type]
            processed_at=_dt(row[16]),
        )

    def get_by_provider_identity(
        self,
        provider: str,
        provider_event_id: str,
    ) -> Event | None:
        row = self.connection.execute(
            """
            SELECT event_id
            FROM events
            WHERE source_provider = ? AND provider_event_id = ?
            """,
            (provider, provider_event_id),
        ).fetchone()
        if row is None:
            return None
        return self.get(EventId(row[0]))

    def claim_next(
        self,
        owner_runtime_instance_id: RuntimeInstanceId,
        *,
        now: datetime,
        lease_expires_at: datetime,
    ) -> Event | None:
        self._validate_lease_window(now, lease_expires_at)
        row = self.connection.execute(
            """
            UPDATE events
            SET status = ?,
                attempt_count = attempt_count + 1,
                last_error = NULL,
                owner_runtime_instance_id = ?,
                lease_expires_at = ?,
                processed_at = NULL
            WHERE event_id = (
                SELECT event_id
                FROM events
                WHERE status IN (?, ?)
                   OR (
                       status = ?
                       AND lease_expires_at IS NOT NULL
                       AND julianday(lease_expires_at) <= julianday(?)
                   )
                ORDER BY julianday(created_at), event_id
                LIMIT 1
            )
            RETURNING event_id
            """,
            (
                EventStatus.PROCESSING.value,
                str(owner_runtime_instance_id),
                _text(lease_expires_at),
                EventStatus.RECEIVED.value,
                EventStatus.RETRY_PENDING.value,
                EventStatus.PROCESSING.value,
                _text(now),
            ),
        ).fetchone()
        return self._event_from_returning(row)

    def renew_lease(
        self,
        event_id: EventId,
        owner_runtime_instance_id: RuntimeInstanceId,
        *,
        now: datetime,
        lease_expires_at: datetime,
    ) -> Event | None:
        self._validate_lease_window(now, lease_expires_at)
        row = self.connection.execute(
            """
            UPDATE events
            SET lease_expires_at = ?
            WHERE event_id = ?
              AND status = ?
              AND owner_runtime_instance_id = ?
              AND julianday(lease_expires_at) > julianday(?)
            RETURNING event_id
            """,
            (
                _text(lease_expires_at),
                str(event_id),
                EventStatus.PROCESSING.value,
                str(owner_runtime_instance_id),
                _text(now),
            ),
        ).fetchone()
        return self._event_from_returning(row)

    def mark_processed(
        self,
        event_id: EventId,
        owner_runtime_instance_id: RuntimeInstanceId,
        *,
        processed_at: datetime,
    ) -> Event | None:
        return self._mark_terminal(
            event_id,
            owner_runtime_instance_id,
            status=EventStatus.PROCESSED,
            processed_at=processed_at,
            error=None,
        )

    def mark_ignored(
        self,
        event_id: EventId,
        owner_runtime_instance_id: RuntimeInstanceId,
        *,
        processed_at: datetime,
    ) -> Event | None:
        return self._mark_terminal(
            event_id,
            owner_runtime_instance_id,
            status=EventStatus.IGNORED,
            processed_at=processed_at,
            error=None,
        )

    def mark_retry_pending(
        self,
        event_id: EventId,
        owner_runtime_instance_id: RuntimeInstanceId,
        *,
        now: datetime,
        error: str,
    ) -> Event | None:
        self._require_aware(now, "now")
        if not error:
            raise ValueError("error must be nonempty")
        row = self.connection.execute(
            """
            UPDATE events
            SET status = ?,
                last_error = ?,
                owner_runtime_instance_id = NULL,
                lease_expires_at = NULL,
                processed_at = NULL
            WHERE event_id = ?
              AND status = ?
              AND owner_runtime_instance_id = ?
              AND julianday(lease_expires_at) > julianday(?)
            RETURNING event_id
            """,
            (
                EventStatus.RETRY_PENDING.value,
                error,
                str(event_id),
                EventStatus.PROCESSING.value,
                str(owner_runtime_instance_id),
                _text(now),
            ),
        ).fetchone()
        return self._event_from_returning(row)

    def mark_dead_letter(
        self,
        event_id: EventId,
        owner_runtime_instance_id: RuntimeInstanceId,
        *,
        processed_at: datetime,
        error: str,
    ) -> Event | None:
        if not error:
            raise ValueError("error must be nonempty")
        return self._mark_terminal(
            event_id,
            owner_runtime_instance_id,
            status=EventStatus.DEAD_LETTER,
            processed_at=processed_at,
            error=error,
        )

    def _mark_terminal(
        self,
        event_id: EventId,
        owner_runtime_instance_id: RuntimeInstanceId,
        *,
        status: EventStatus,
        processed_at: datetime,
        error: str | None,
    ) -> Event | None:
        self._require_aware(processed_at, "processed_at")
        row = self.connection.execute(
            """
            UPDATE events
            SET status = ?,
                last_error = ?,
                owner_runtime_instance_id = NULL,
                lease_expires_at = NULL,
                processed_at = ?
            WHERE event_id = ?
              AND status = ?
              AND owner_runtime_instance_id = ?
              AND julianday(lease_expires_at) > julianday(?)
            RETURNING event_id
            """,
            (
                status.value,
                error,
                _text(processed_at),
                str(event_id),
                EventStatus.PROCESSING.value,
                str(owner_runtime_instance_id),
                _text(processed_at),
            ),
        ).fetchone()
        return self._event_from_returning(row)


class SQLiteCommandRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, item: Command) -> None:
        self.connection.execute(
            """
            INSERT INTO commands(
                command_id, command_type, job_id, payload_json, status,
                dedupe_key, causation_event_id, attempt_count,
                owner_runtime_instance_id, lease_expires_at, created_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.command_id),
                item.command_type,
                item.job_id,
                json.dumps(dict(item.payload), sort_keys=True),
                item.status.value,
                item.dedupe_key,
                item.causation_event_id,
                item.attempt_count,
                item.owner_runtime_instance_id,
                _text(item.lease_expires_at),
                _text(item.created_at),
                _text(item.completed_at),
            ),
        )

    def get(self, command_id: CommandId) -> Command | None:
        row = self.connection.execute(
            """
            SELECT command_id, command_type, job_id, payload_json, status,
                   dedupe_key, causation_event_id, owner_runtime_instance_id,
                   lease_expires_at, attempt_count, created_at, completed_at
            FROM commands WHERE command_id = ?
            """,
            (str(command_id),),
        ).fetchone()
        if row is None:
            return None
        return Command(
            command_id=CommandId(row[0]),
            command_type=row[1],
            job_id=None if row[2] is None else JobId(row[2]),
            payload=json.loads(row[3]),
            status=CommandStatus(row[4]),
            dedupe_key=row[5],
            causation_event_id=None if row[6] is None else EventId(row[6]),
            owner_runtime_instance_id=(
                None if row[7] is None else RuntimeInstanceId(row[7])
            ),
            lease_expires_at=_dt(row[8]),
            attempt_count=row[9],
            created_at=_dt(row[10]),  # type: ignore[arg-type]
            completed_at=_dt(row[11]),
        )


class SQLiteInteractionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, item: Interaction) -> None:
        self.connection.execute(
            """
            INSERT INTO interactions(
                interaction_id, job_id, interaction_type, provider,
                provider_context_json, professional_context_json, status,
                created_at, updated_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.interaction_id),
                str(item.job_id),
                item.interaction_type.value,
                item.provider,
                json.dumps(dict(item.provider_context), sort_keys=True),
                json.dumps(dict(item.professional_context), sort_keys=True),
                item.status.value,
                _text(item.created_at),
                _text(item.updated_at),
                _text(item.completed_at),
            ),
        )

    def get(self, interaction_id: InteractionId) -> Interaction | None:
        row = self.connection.execute(
            "SELECT * FROM interactions WHERE interaction_id = ?",
            (str(interaction_id),),
        ).fetchone()
        if row is None:
            return None
        return Interaction(
            interaction_id=InteractionId(row[0]),
            job_id=JobId(row[1]),
            interaction_type=InteractionType(row[2]),
            provider=row[3],
            provider_context=json.loads(row[4]),
            professional_context=json.loads(row[5]),
            status=InteractionStatus(row[6]),
            created_at=_dt(row[7]),  # type: ignore[arg-type]
            updated_at=_dt(row[8]),  # type: ignore[arg-type]
            completed_at=_dt(row[9]),
        )


class SQLiteInteractionMessageRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, item: InteractionMessage) -> None:
        self.connection.execute(
            """
            INSERT INTO interaction_messages(
                message_id, interaction_id, provider, provider_message_id,
                provider_created_at, direction, message_type, content_text,
                content_ref, persisted_at, processed_at,
                processed_by_continuation_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.message_id),
                str(item.interaction_id),
                item.provider,
                item.provider_message_id,
                _text(item.provider_created_at),
                item.direction,
                item.message_type,
                item.content,
                item.content_ref,
                _text(item.persisted_at),
                _text(item.processed_at),
                item.processed_by_continuation_id,
            ),
        )

    def get(self, message_id: MessageId) -> InteractionMessage | None:
        row = self.connection.execute(
            "SELECT * FROM interaction_messages WHERE message_id = ?",
            (str(message_id),),
        ).fetchone()
        if row is None:
            return None
        return InteractionMessage(
            message_id=MessageId(row[0]),
            interaction_id=InteractionId(row[1]),
            provider=row[2],
            provider_message_id=row[3],
            provider_created_at=_dt(row[4]),
            direction=row[5],
            message_type=row[6],
            content=row[7],
            content_ref=row[8],
            persisted_at=_dt(row[9]),  # type: ignore[arg-type]
            processed_at=_dt(row[10]),
            processed_by_continuation_id=(
                None if row[11] is None else InvocationId(row[11])
            ),
        )


class SQLiteFailureRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, item: Failure) -> None:
        self.connection.execute(
            """
            INSERT INTO failures(
                failure_id, job_id, execution_id, event_id, command_id,
                interaction_id, failure_class, message, details_ref,
                created_at, resolved_at, resolution_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.failure_id),
                str(item.job_id),
                item.execution_id,
                item.event_id,
                item.command_id,
                item.interaction_id,
                item.failure_class.value,
                item.message,
                item.details_ref,
                _text(item.created_at),
                _text(item.resolved_at),
                item.resolution_message,
            ),
        )

    def get(self, failure_id: FailureId) -> Failure | None:
        row = self.connection.execute(
            "SELECT * FROM failures WHERE failure_id = ?",
            (str(failure_id),),
        ).fetchone()
        if row is None:
            return None
        return Failure(
            failure_id=FailureId(row[0]),
            job_id=JobId(row[1]),
            execution_id=None if row[2] is None else ExecutionId(row[2]),
            event_id=None if row[3] is None else EventId(row[3]),
            command_id=None if row[4] is None else CommandId(row[4]),
            interaction_id=None if row[5] is None else InteractionId(row[5]),
            failure_class=FailureClass(row[6]),
            message=row[7],
            details_ref=row[8],
            created_at=_dt(row[9]),  # type: ignore[arg-type]
            resolved_at=_dt(row[10]),
            resolution_message=row[11],
        )


class SQLiteRoutingDecisionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, job_id: JobId, item: RoutingDecision) -> None:
        self.connection.execute(
            """
            INSERT INTO routing_decisions(
                decision_id, job_id, decided_at, from_phase, to_phase,
                predicate_name, predicate_result, reason, execution_id, basis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.decision_id),
                str(job_id),
                _text(item.decided_at),
                item.from_phase.value,
                item.to_phase.value,
                item.predicate.name,
                int(item.predicate.result),
                item.reason,
                item.execution_id,
                json.dumps([_artifact_ref_dict(x) for x in item.basis], sort_keys=True),
            ),
        )

    def get(self, decision_id: RoutingDecisionId) -> RoutingDecision | None:
        row = self.connection.execute(
            """
            SELECT decision_id, decided_at, from_phase, to_phase,
                   predicate_name, predicate_result, reason, execution_id, basis_json
            FROM routing_decisions WHERE decision_id = ?
            """,
            (str(decision_id),),
        ).fetchone()
        if row is None:
            return None
        return RoutingDecision(
            decision_id=RoutingDecisionId(row[0]),
            decided_at=_dt(row[1]),  # type: ignore[arg-type]
            from_phase=LifecyclePhase(row[2]),
            to_phase=LifecyclePhase(row[3]),
            predicate=RoutingPredicateResult(row[4], bool(row[5])),
            basis=tuple(_artifact_ref(x) for x in json.loads(row[8])),
            reason=row[6],
            execution_id=None if row[7] is None else ExecutionId(row[7]),
        )


class SQLiteInvocationProvenanceRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add(self, item: InvocationProvenance) -> None:
        self.connection.execute(
            """
            INSERT INTO invocation_provenance(
                invocation_id, execution_id, operation_type,
                operation_specification_hash, operation_registry_hash,
                runtime_git_sha, runtime_image_digest, provider, model,
                provider_request_id, resources_json, usage_json, latency_ms,
                started_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(item.invocation_id),
                str(item.execution_id),
                item.operation_type.value,
                item.operation_specification_hash,
                item.operation_registry_hash,
                item.runtime_git_sha,
                item.runtime_image_digest,
                item.provider,
                item.model,
                item.provider_request_id,
                json.dumps(dict(item.resources), sort_keys=True),
                None if item.usage is None else json.dumps(dict(item.usage), sort_keys=True),
                item.latency_ms,
                _text(item.started_at),
                _text(item.completed_at),
            ),
        )

    def get(self, invocation_id: InvocationId) -> InvocationProvenance | None:
        row = self.connection.execute(
            "SELECT * FROM invocation_provenance WHERE invocation_id = ?",
            (str(invocation_id),),
        ).fetchone()
        if row is None:
            return None
        return InvocationProvenance(
            invocation_id=InvocationId(row[0]),
            execution_id=ExecutionId(row[1]),
            operation_type=OperationType(row[2]),
            operation_specification_hash=row[3],
            operation_registry_hash=row[4],
            runtime_git_sha=row[5],
            runtime_image_digest=row[6],
            provider=row[7],
            model=row[8],
            provider_request_id=row[9],
            resources=json.loads(row[10]),
            usage=None if row[11] is None else json.loads(row[11]),
            latency_ms=row[12],
            started_at=_dt(row[13]),  # type: ignore[arg-type]
            completed_at=_dt(row[14]),
        )


class SQLiteRuntimeJobRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.artifacts = SQLiteArtifactRepository(connection)

    def add(self, job: RuntimeJob) -> None:
        self.connection.execute(
            """
            INSERT INTO runtime_jobs(
                job_id, revision, lifecycle_phase, lifecycle_entered_at,
                operation_status, operation_type, operation_execution_id,
                operation_started_at, interaction_status, interaction_type,
                interaction_id, interaction_started_at,
                interaction_last_activity_at, health_status, health_failure_id,
                health_retry_count, created_at, updated_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(job.identity.job_id),
                job.identity.revision,
                job.lifecycle.phase.value,
                _text(job.lifecycle.entered_at),
                job.operation.status.value,
                (
                    None
                    if job.operation.operation_type is None
                    else job.operation.operation_type.value
                ),
                job.operation.execution_id,
                _text(job.operation.started_at),
                job.interaction.status.value,
                (
                    None
                    if job.interaction.interaction_type is None
                    else job.interaction.interaction_type.value
                ),
                job.interaction.interaction_id,
                _text(job.interaction.started_at),
                _text(job.interaction.last_activity_at),
                job.health.status.value,
                job.health.failure_id,
                job.health.retry_count,
                _text(job.identity.created_at),
                _text(job.identity.updated_at),
                _text(job.identity.completed_at),
            ),
        )
        scalar = {
            "target_job": job.professional_state.target_job,
            "jea": job.professional_state.jea,
            "resume": job.professional_state.resume,
            "wcm": job.professional_state.wcm,
            "evaluation": job.professional_state.evaluation,
        }
        for pointer_type, ref in scalar.items():
            if ref is not None:
                self.connection.execute(
                    """
                    INSERT INTO job_artifact_pointers(
                        job_id, pointer_type, artifact_id, artifact_version
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        str(job.identity.job_id),
                        pointer_type,
                        str(ref.artifact_id),
                        ref.artifact_version.value,
                    ),
                )
        collections = {
            "jer_set": job.professional_state.jer_set,
            "active_erqs": job.professional_state.active_erqs,
            "unintegrated_evidence_responses": (
                job.professional_state.unintegrated_evidence_responses
            ),
        }
        for collection_type, refs in collections.items():
            for ref in refs:
                self.connection.execute(
                    """
                    INSERT INTO job_artifact_collection_members(
                        job_id, collection_type, artifact_id, artifact_version
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        str(job.identity.job_id),
                        collection_type,
                        str(ref.artifact_id),
                        ref.artifact_version.value,
                    ),
                )
        routing = SQLiteRoutingDecisionRepository(self.connection)
        for decision in job.routing_history:
            routing.add(job.identity.job_id, decision)

    def get(self, job_id: JobId) -> RuntimeJob | None:
        row = self.connection.execute(
            "SELECT * FROM runtime_jobs WHERE job_id = ?",
            (str(job_id),),
        ).fetchone()
        if row is None:
            return None

        pointer_rows = self.connection.execute(
            """
            SELECT pointer_type, artifact_id, artifact_version
            FROM job_artifact_pointers WHERE job_id = ?
            """,
            (str(job_id),),
        ).fetchall()
        pointers = {
            item[0]: self.artifacts.ref(ArtifactId(item[1]), item[2])
            for item in pointer_rows
        }
        collection_rows = self.connection.execute(
            """
            SELECT collection_type, artifact_id, artifact_version
            FROM job_artifact_collection_members
            WHERE job_id = ?
            ORDER BY collection_type, artifact_id, artifact_version
            """,
            (str(job_id),),
        ).fetchall()
        collections: dict[str, list[ArtifactRef]] = {
            "jer_set": [],
            "active_erqs": [],
            "unintegrated_evidence_responses": [],
        }
        for collection_type, artifact_id, version in collection_rows:
            ref = self.artifacts.ref(ArtifactId(artifact_id), version)
            if ref is not None:
                collections[collection_type].append(ref)

        routing_rows = self.connection.execute(
            """
            SELECT decision_id FROM routing_decisions
            WHERE job_id = ? ORDER BY decided_at, decision_id
            """,
            (str(job_id),),
        ).fetchall()
        routing_repo = SQLiteRoutingDecisionRepository(self.connection)
        decisions = tuple(
            decision
            for decision_id, in routing_rows
            if (decision := routing_repo.get(RoutingDecisionId(decision_id))) is not None
        )

        return RuntimeJob(
            identity=RuntimeJobIdentity(
                job_id=JobId(row[0]),
                revision=row[1],
                created_at=_dt(row[16]),  # type: ignore[arg-type]
                updated_at=_dt(row[17]),  # type: ignore[arg-type]
                completed_at=_dt(row[18]),
            ),
            lifecycle=LifecycleState(
                phase=LifecyclePhase(row[2]),
                entered_at=_dt(row[3]),  # type: ignore[arg-type]
            ),
            operation=OperationState(
                status=RuntimeOperationStatus(row[4]),
                operation_type=None if row[5] is None else OperationType(row[5]),
                execution_id=None if row[6] is None else ExecutionId(row[6]),
                started_at=_dt(row[7]),
            ),
            interaction=InteractionProjection(
                status=InteractionProjectionStatus(row[8]),
                interaction_type=None if row[9] is None else InteractionType(row[9]),
                interaction_id=None if row[10] is None else InteractionId(row[10]),
                started_at=_dt(row[11]),
                last_activity_at=_dt(row[12]),
            ),
            health=HealthState(
                status=HealthStatus(row[13]),
                failure_id=None if row[14] is None else FailureId(row[14]),
                retry_count=row[15],
            ),
            professional_state=ProfessionalState(
                target_job=pointers["target_job"],  # type: ignore[arg-type]
                jer_set=tuple(collections["jer_set"]),
                jea=pointers.get("jea"),
                active_erqs=tuple(collections["active_erqs"]),
                unintegrated_evidence_responses=tuple(
                    collections["unintegrated_evidence_responses"]
                ),
                resume=pointers.get("resume"),
                wcm=pointers.get("wcm"),
                evaluation=pointers.get("evaluation"),
            ),
            routing_history=decisions,
        )


__all__ = [
    "SQLiteArtifactRepository",
    "SQLiteCommandRepository",
    "SQLiteEventRepository",
    "SQLiteExecutionRepository",
    "SQLiteFailureRepository",
    "SQLiteInteractionMessageRepository",
    "SQLiteInteractionRepository",
    "SQLiteInvocationProvenanceRepository",
    "SQLiteRoutingDecisionRepository",
    "SQLiteRuntimeInstanceRepository",
    "SQLiteRuntimeJobRepository",
]
