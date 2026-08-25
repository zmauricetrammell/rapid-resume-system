from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from rrs.domain.artifacts import ArtifactMetadata, ArtifactRef, ArtifactVersion
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
from rrs.infrastructure.persistence.migrations import migrate_database
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

NOW = datetime(2026, 8, 25, 20, 0, tzinfo=UTC)


def migrations() -> Path:
    return Path(__file__).resolve().parents[4] / "migrations"


def connection(tmp_path: Path) -> sqlite3.Connection:
    database = tmp_path / "rrs.db"
    migrate_database(database, migrations())
    result = sqlite3.connect(database)
    result.execute("PRAGMA foreign_keys=ON")
    return result


def target_ref() -> ArtifactRef:
    return ArtifactRef(
        ArtifactType.TARGET_JOB,
        ArtifactId("target-1"),
        ArtifactVersion(1),
        "file:///target-1",
    )


def add_target_artifact(db: sqlite3.Connection) -> None:
    SQLiteArtifactRepository(db).add(
        ArtifactMetadata(
            artifact_id=ArtifactId("target-1"),
            artifact_version=ArtifactVersion(1),
            artifact_type=ArtifactType.TARGET_JOB,
            storage_uri="file:///target-1",
            content_hash="sha256:target",
            committed_by_execution_id=None,
            operation_key=None,
            committed_at=NOW,
            runtime_status=ArtifactRuntimeStatus.COMMITTED,
        ),
        created_at=NOW.isoformat(),
    )


def add_runtime_instance(db: sqlite3.Connection) -> RuntimeInstance:
    item = RuntimeInstance(
        runtime_instance_id=RuntimeInstanceId("runtime-1"),
        git_sha="git-sha",
        image_digest="sha256:image",
        operation_registry_hash="registry-hash",
        built_at=NOW,
        started_at=NOW,
        stopped_at=None,
    )
    SQLiteRuntimeInstanceRepository(db).add(item)
    return item


def add_minimal_job(db: sqlite3.Connection) -> RuntimeJob:
    add_target_artifact(db)
    job = RuntimeJob(
        identity=RuntimeJobIdentity(JobId("job-1"), 1, NOW, NOW, None),
        lifecycle=LifecycleState(LifecyclePhase.ANALYSIS, NOW),
        operation=OperationState(RuntimeOperationStatus.IDLE, None, None, None),
        interaction=InteractionProjection(
            InteractionProjectionStatus.NONE,
            None,
            None,
            None,
            None,
        ),
        health=HealthState(HealthStatus.HEALTHY, None, 0),
        professional_state=ProfessionalState(
            target_job=target_ref(),
            jer_set=(),
            jea=None,
            active_erqs=(),
            unintegrated_evidence_responses=(),
            resume=None,
            wcm=None,
            evaluation=None,
        ),
        routing_history=(),
    )
    SQLiteRuntimeJobRepository(db).add(job)
    return job


def test_artifact_repository_round_trip(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        add_target_artifact(db)
        repo = SQLiteArtifactRepository(db)
        item = repo.get(ArtifactId("target-1"), 1)
        assert item is not None
        assert item.artifact_type is ArtifactType.TARGET_JOB
        assert repo.ref(ArtifactId("target-1"), 1) == target_ref()
    finally:
        db.close()


def test_runtime_job_repository_reconstructs_deterministically(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        job = add_minimal_job(db)
        loaded = SQLiteRuntimeJobRepository(db).get(JobId("job-1"))
        assert loaded == job
    finally:
        db.close()


def test_runtime_instance_repository_round_trip(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        item = add_runtime_instance(db)
        loaded = SQLiteRuntimeInstanceRepository(db).get(item.runtime_instance_id)
        assert loaded == item
    finally:
        db.close()


def test_execution_repository_round_trip(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        add_minimal_job(db)
        add_runtime_instance(db)
        item = Execution(
            execution_id=ExecutionId("execution-1"),
            job_id=JobId("job-1"),
            owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
            operation_type=OperationType.GENERATE_ANALYSIS,
            operation_key=OperationKey("operation-1"),
            attempt_number=1,
            status=ExecutionStatus.RUNNING,
            input_snapshot=InputSnapshot(
                identity_dependencies=(
                    DependencyFingerprint("artifact", "target_job", "target-1:1"),
                ),
                freshness_dependencies=(),
            ),
            staged_outputs=(),
            committed_outputs=(),
            failure_id=None,
            created_at=NOW,
            started_at=NOW,
            completed_at=None,
        )
        repo = SQLiteExecutionRepository(db)
        repo.add(item)
        assert repo.get(item.execution_id) == item
    finally:
        db.close()


def test_event_and_command_repositories_round_trip(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        add_minimal_job(db)
        event = Event(
            event_id=EventId("event-1"),
            event_type="job_created",
            job_id=JobId("job-1"),
            payload={"value": 1},
            source=EventSource("runtime", "rrs", None),
            correlation_id="corr",
            causation_id=None,
            criticality=EventCriticality.WORKFLOW_CRITICAL,
            status=EventStatus.RECEIVED,
            attempt_count=0,
            owner_runtime_instance_id=None,
            lease_expires_at=None,
            created_at=NOW,
            processed_at=None,
        )
        events = SQLiteEventRepository(db)
        events.add(event)
        assert events.get(event.event_id) == event

        command = Command(
            command_id=CommandId("command-1"),
            command_type="evaluate_routing",
            job_id=JobId("job-1"),
            payload={"event": "event-1"},
            status=CommandStatus.PENDING,
            dedupe_key="job-1:routing",
            causation_event_id=event.event_id,
            owner_runtime_instance_id=None,
            lease_expires_at=None,
            attempt_count=0,
            created_at=NOW,
            completed_at=None,
        )
        commands = SQLiteCommandRepository(db)
        commands.add(command)
        assert commands.get(command.command_id) == command
    finally:
        db.close()


def test_interaction_and_message_repositories_round_trip(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        add_minimal_job(db)
        interaction = Interaction(
            interaction_id=InteractionId("interaction-1"),
            job_id=JobId("job-1"),
            interaction_type=InteractionType.EVIDENCE_INVESTIGATION,
            provider="discord",
            provider_context={"channel": "1"},
            professional_context={"erq": "1"},
            status=InteractionStatus.ACTIVE,
            created_at=NOW,
            updated_at=NOW,
            completed_at=None,
        )
        interactions = SQLiteInteractionRepository(db)
        interactions.add(interaction)
        assert interactions.get(interaction.interaction_id) == interaction

        message = InteractionMessage(
            message_id=MessageId("message-1"),
            interaction_id=interaction.interaction_id,
            provider="discord",
            provider_message_id="100",
            provider_created_at=NOW,
            direction="inbound",
            message_type="human_message",
            content="hello",
            content_ref=None,
            persisted_at=NOW,
            processed_at=NOW,
            processed_by_continuation_id=InvocationId("invocation-1"),
        )
        messages = SQLiteInteractionMessageRepository(db)
        messages.add(message)
        assert messages.get(message.message_id) == message
    finally:
        db.close()


def test_failure_repository_round_trip(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        add_minimal_job(db)
        item = Failure(
            failure_id=FailureId("failure-1"),
            job_id=JobId("job-1"),
            execution_id=None,
            event_id=None,
            command_id=None,
            interaction_id=None,
            failure_class=FailureClass.PERSISTENCE_FAILURE,
            message="failure",
            details_ref=None,
            created_at=NOW,
            resolved_at=None,
            resolution_message=None,
        )
        repo = SQLiteFailureRepository(db)
        repo.add(item)
        assert repo.get(item.failure_id) == item
    finally:
        db.close()


def test_routing_decision_repository_round_trip(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        add_minimal_job(db)
        item = RoutingDecision(
            decision_id=RoutingDecisionId("decision-1"),
            decided_at=NOW,
            from_phase=LifecyclePhase.ANALYSIS,
            to_phase=LifecyclePhase.EVIDENCE_REQUEST,
            predicate=RoutingPredicateResult("needs_evidence", True),
            basis=(target_ref(),),
            reason="Evidence required",
            execution_id=None,
        )
        repo = SQLiteRoutingDecisionRepository(db)
        repo.add(JobId("job-1"), item)
        assert repo.get(item.decision_id) == item
    finally:
        db.close()


def test_invocation_provenance_repository_round_trip(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        add_minimal_job(db)
        add_runtime_instance(db)
        execution = Execution(
            execution_id=ExecutionId("execution-1"),
            job_id=JobId("job-1"),
            owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
            operation_type=OperationType.GENERATE_ANALYSIS,
            operation_key=OperationKey("operation-1"),
            attempt_number=1,
            status=ExecutionStatus.RUNNING,
            input_snapshot=InputSnapshot((), ()),
            staged_outputs=(),
            committed_outputs=(),
            failure_id=None,
            created_at=NOW,
            started_at=NOW,
            completed_at=None,
        )
        SQLiteExecutionRepository(db).add(execution)

        item = InvocationProvenance(
            invocation_id=InvocationId("invocation-1"),
            execution_id=execution.execution_id,
            operation_type=execution.operation_type,
            operation_specification_hash="spec-hash",
            operation_registry_hash="registry-hash",
            runtime_git_sha="git-sha",
            runtime_image_digest="sha256:image",
            provider="openai",
            model="model",
            provider_request_id="request-1",
            resources={"contract": "hash"},
            usage={"input_tokens": 10},
            latency_ms=100,
            started_at=NOW,
            completed_at=NOW,
        )
        repo = SQLiteInvocationProvenanceRepository(db)
        repo.add(item)
        assert repo.get(item.invocation_id) == item
    finally:
        db.close()


def test_missing_repository_records_return_none(tmp_path: Path) -> None:
    db = connection(tmp_path)
    try:
        assert SQLiteRuntimeJobRepository(db).get(JobId("missing")) is None

        artifact_repo = SQLiteArtifactRepository(db)
        assert artifact_repo.get(ArtifactId("missing"), 1) is None
        assert artifact_repo.ref(ArtifactId("missing"), 1) is None

        assert (
            SQLiteRuntimeInstanceRepository(db).get(
                RuntimeInstanceId("missing")
            )
            is None
        )
        assert (
            SQLiteExecutionRepository(db).get(
                ExecutionId("missing")
            )
            is None
        )
        assert SQLiteEventRepository(db).get(EventId("missing")) is None
        assert SQLiteCommandRepository(db).get(CommandId("missing")) is None

        assert (
            SQLiteInteractionRepository(db).get(
                InteractionId("missing")
            )
            is None
        )
        assert (
            SQLiteInteractionMessageRepository(db).get(
                MessageId("missing")
            )
            is None
        )

        assert SQLiteFailureRepository(db).get(FailureId("missing")) is None

        assert (
            SQLiteRoutingDecisionRepository(db).get(
                RoutingDecisionId("missing")
            )
            is None
        )
        assert (
            SQLiteInvocationProvenanceRepository(db).get(
                InvocationId("missing")
            )
            is None
        )
    finally:
        db.close()

def test_runtime_job_repository_round_trips_collections_and_routing(
    tmp_path: Path,
) -> None:
    db = connection(tmp_path)
    try:
        artifact_repo = SQLiteArtifactRepository(db)

        refs = (
            ArtifactRef(
                ArtifactType.TARGET_JOB,
                ArtifactId("target-1"),
                ArtifactVersion(1),
                "file:///target-1",
            ),
            ArtifactRef(
                ArtifactType.JOB_EXPERIENCE_RECORD,
                ArtifactId("jer-1"),
                ArtifactVersion(2),
                "file:///jer-1-v2",
            ),
            ArtifactRef(
                ArtifactType.EVIDENCE_REQUEST,
                ArtifactId("erq-1"),
                ArtifactVersion(1),
                "file:///erq-1",
            ),
            ArtifactRef(
                ArtifactType.EVIDENCE_RESPONSE,
                ArtifactId("response-1"),
                ArtifactVersion(1),
                "file:///response-1",
            ),
        )

        for ref in refs:
            artifact_repo.add(
                ArtifactMetadata(
                    artifact_id=ref.artifact_id,
                    artifact_version=ref.artifact_version,
                    artifact_type=ref.artifact_type,
                    storage_uri=ref.uri,
                    content_hash=f"sha256:{ref.artifact_id}",
                    committed_by_execution_id=None,
                    operation_key=None,
                    committed_at=NOW,
                    runtime_status=ArtifactRuntimeStatus.COMMITTED,
                ),
                created_at=NOW.isoformat(),
            )

        decision = RoutingDecision(
            decision_id=RoutingDecisionId("decision-1"),
            decided_at=NOW,
            from_phase=LifecyclePhase.ANALYSIS,
            to_phase=LifecyclePhase.EVIDENCE_REQUEST,
            predicate=RoutingPredicateResult(
                "needs_evidence",
                True,
            ),
            basis=(refs[0],),
            reason="Evidence required",
            execution_id=None,
        )

        job = RuntimeJob(
            identity=RuntimeJobIdentity(
                JobId("job-collections"),
                1,
                NOW,
                NOW,
                None,
            ),
            lifecycle=LifecycleState(
                LifecyclePhase.ANALYSIS,
                NOW,
            ),
            operation=OperationState(
                RuntimeOperationStatus.IDLE,
                None,
                None,
                None,
            ),
            interaction=InteractionProjection(
                InteractionProjectionStatus.NONE,
                None,
                None,
                None,
                None,
            ),
            health=HealthState(
                HealthStatus.HEALTHY,
                None,
                0,
            ),
            professional_state=ProfessionalState(
                target_job=refs[0],
                jer_set=(refs[1],),
                jea=None,
                active_erqs=(refs[2],),
                unintegrated_evidence_responses=(refs[3],),
                resume=None,
                wcm=None,
                evaluation=None,
            ),
            routing_history=(decision,),
        )

        repo = SQLiteRuntimeJobRepository(db)
        repo.add(job)

        loaded = repo.get(job.identity.job_id)

        assert loaded == job
        assert loaded is not None
        assert loaded.professional_state.jer_set == (refs[1],)
        assert loaded.professional_state.active_erqs == (refs[2],)
        assert loaded.professional_state.unintegrated_evidence_responses == (
            refs[3],
        )
        assert loaded.routing_history == (decision,)
    finally:
        db.close()