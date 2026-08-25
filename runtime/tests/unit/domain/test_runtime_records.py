from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

import pytest

from rrs.domain.artifacts import StagedArtifact
from rrs.domain.commands import Command
from rrs.domain.enums import (
    ArtifactType,
    CommandStatus,
    EventCriticality,
    EventStatus,
    ExecutionStatus,
    FailureClass,
    InteractionStatus,
    InteractionType,
    OperationType,
)
from rrs.domain.events import Event, EventSource
from rrs.domain.executions import Execution
from rrs.domain.failures import Failure
from rrs.domain.ids import (
    CommandId,
    EventId,
    ExecutionId,
    FailureId,
    InteractionId,
    InvocationId,
    JobId,
    MessageId,
    OperationKey,
    RuntimeInstanceId,
)
from rrs.domain.interactions import Interaction, InteractionMessage

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)


def execution(
    *,
    attempt_number: int = 1,
    status: ExecutionStatus = ExecutionStatus.CREATED,
    completed_at: datetime | None = None,
    failure_id: FailureId | None = None,
    staged_outputs: tuple[StagedArtifact, ...] = (),
) -> Execution:
    return Execution(
        execution_id=ExecutionId("execution-1"),
        job_id=JobId("job-1"),
        owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
        operation_type=OperationType.GENERATE_ANALYSIS,
        operation_key=OperationKey("operation-key-1"),
        attempt_number=attempt_number,
        status=status,
        input_snapshot=object(),  # ISSUE-007 provides the concrete InputSnapshot type.
        staged_outputs=staged_outputs,
        committed_outputs=(),
        failure_id=failure_id,
        created_at=NOW,
        started_at=None,
        completed_at=completed_at,
    )


@pytest.mark.parametrize("attempt_number", [0, -1])
def test_execution_rejects_invalid_attempt_number(attempt_number: int) -> None:
    with pytest.raises(ValueError, match="attempt_number"):
        execution(attempt_number=attempt_number)


def test_terminal_execution_requires_completed_at() -> None:
    with pytest.raises(ValueError, match="completed_at"):
        execution(status=ExecutionStatus.FAILED)


def test_nonterminal_execution_rejects_completed_at() -> None:
    with pytest.raises(ValueError, match="nonterminal"):
        execution(status=ExecutionStatus.RUNNING, completed_at=NOW)


def test_committed_execution_rejects_failure_pointer() -> None:
    with pytest.raises(ValueError, match="failure_id"):
        execution(
            status=ExecutionStatus.COMMITTED,
            completed_at=NOW,
            failure_id=FailureId("failure-1"),
        )


def test_execution_preserves_staged_outputs() -> None:
    staged = StagedArtifact(
        artifact_type=ArtifactType.JOB_EXPERIENCE_ANALYSIS,
        execution_id=ExecutionId("execution-1"),
        staged_path="/data/staging/execution-1/jea.yaml",
        content_hash="sha256:jea",
        media_type="application/yaml",
    )
    item = execution(staged_outputs=(staged,))
    assert item.staged_outputs == (staged,)


def test_event_source_and_event_are_provider_neutral() -> None:
    source = EventSource(
        category="integration",
        provider="discord",
        provider_event_id="provider-event-1",
    )
    event = Event(
        event_id=EventId("event-1"),
        event_type="human_message_received",
        job_id=JobId("job-1"),
        payload={"message_id": "m1"},
        source=source,
        correlation_id="correlation-1",
        causation_id=None,
        criticality=EventCriticality.WORKFLOW_CRITICAL,
        status=EventStatus.RECEIVED,
        attempt_count=0,
        owner_runtime_instance_id=None,
        lease_expires_at=None,
        created_at=NOW,
        processed_at=None,
    )

    assert event.source.provider_event_id == "provider-event-1"
    with pytest.raises(TypeError):
        event.payload["message_id"] = "changed"  # type: ignore[index]


def test_event_claim_owner_and_lease_must_be_paired() -> None:
    with pytest.raises(ValueError, match="owner and lease"):
        Event(
            event_id=EventId("event-1"),
            event_type="test",
            job_id=None,
            payload={},
            source=EventSource("runtime", "rrs", None),
            correlation_id=None,
            causation_id=None,
            criticality=EventCriticality.INTEGRATION_ONLY,
            status=EventStatus.PROCESSING,
            attempt_count=1,
            owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
            lease_expires_at=None,
            created_at=NOW,
            processed_at=None,
        )


def test_command_preserves_dedupe_and_causation() -> None:
    command = Command(
        command_id=CommandId("command-1"),
        command_type="evaluate_routing",
        job_id=JobId("job-1"),
        payload={"reason": "event"},
        status=CommandStatus.PENDING,
        dedupe_key="job-1:evaluate",
        causation_event_id=EventId("event-1"),
        owner_runtime_instance_id=None,
        lease_expires_at=None,
        attempt_count=0,
        created_at=NOW,
        completed_at=None,
    )
    assert command.dedupe_key == "job-1:evaluate"
    assert command.causation_event_id == "event-1"


def test_command_rejects_negative_attempt_count() -> None:
    with pytest.raises(ValueError, match="attempt_count"):
        Command(
            command_id=CommandId("command-1"),
            command_type="test",
            job_id=None,
            payload={},
            status=CommandStatus.PENDING,
            dedupe_key=None,
            causation_event_id=None,
            owner_runtime_instance_id=None,
            lease_expires_at=None,
            attempt_count=-1,
            created_at=NOW,
            completed_at=None,
        )


def test_interaction_preserves_context_and_authoritative_status() -> None:
    interaction = Interaction(
        interaction_id=InteractionId("interaction-1"),
        job_id=JobId("job-1"),
        interaction_type=InteractionType.EVIDENCE_INVESTIGATION,
        provider="discord",
        provider_context={"channel_id": "channel-1"},
        professional_context={"erq_id": "erq-1"},
        status=InteractionStatus.ACTIVE,
        created_at=NOW,
        updated_at=NOW,
        completed_at=None,
    )
    assert interaction.status is InteractionStatus.ACTIVE
    with pytest.raises(TypeError):
        interaction.provider_context["channel_id"] = "changed"  # type: ignore[index]


def test_interaction_rejects_backwards_updated_at() -> None:
    with pytest.raises(ValueError, match="updated_at"):
        Interaction(
            interaction_id=InteractionId("interaction-1"),
            job_id=JobId("job-1"),
            interaction_type=InteractionType.MANUAL_REVIEW,
            provider="discord",
            provider_context={},
            professional_context={},
            status=InteractionStatus.PENDING,
            created_at=NOW,
            updated_at=NOW - timedelta(seconds=1),
            completed_at=None,
        )


def test_interaction_message_preserves_provider_chronology() -> None:
    message = InteractionMessage(
        message_id=MessageId("message-1"),
        interaction_id=InteractionId("interaction-1"),
        provider="discord",
        provider_message_id="100",
        provider_created_at=NOW,
        direction="inbound",
        message_type="human_message",
        content="Evidence details",
        content_ref=None,
        persisted_at=NOW + timedelta(seconds=1),
        processed_at=NOW + timedelta(seconds=2),
        processed_by_continuation_id=InvocationId("invocation-1"),
    )

    assert message.provider_created_at == NOW
    assert message.provider_message_id == "100"
    assert message.processed_by_continuation_id == "invocation-1"


def test_interaction_message_requires_content_or_ref() -> None:
    with pytest.raises(ValueError, match="content"):
        InteractionMessage(
            message_id=MessageId("message-1"),
            interaction_id=InteractionId("interaction-1"),
            provider="discord",
            provider_message_id=None,
            provider_created_at=None,
            direction="outbound",
            message_type="prompt",
            content=None,
            content_ref=None,
            persisted_at=NOW,
            processed_at=None,
            processed_by_continuation_id=None,
        )


def test_continuation_consumer_requires_processed_at() -> None:
    with pytest.raises(ValueError, match="processed_at"):
        InteractionMessage(
            message_id=MessageId("message-1"),
            interaction_id=InteractionId("interaction-1"),
            provider="discord",
            provider_message_id=None,
            provider_created_at=None,
            direction="inbound",
            message_type="human_message",
            content="hello",
            content_ref=None,
            persisted_at=NOW,
            processed_at=None,
            processed_by_continuation_id=InvocationId("invocation-1"),
        )


def test_failure_preserves_history_after_resolution() -> None:
    failure = Failure(
        failure_id=FailureId("failure-1"),
        job_id=JobId("job-1"),
        execution_id=ExecutionId("execution-1"),
        event_id=None,
        command_id=None,
        interaction_id=None,
        failure_class=FailureClass.INVOCATION_FAILURE,
        message="provider timeout",
        details_ref="file:///diagnostics/failure-1.json",
        created_at=NOW,
        resolved_at=NOW + timedelta(minutes=5),
        resolution_message="retry succeeded",
    )

    assert failure.message == "provider timeout"
    assert failure.resolution_message == "retry succeeded"


def test_unresolved_failure_cannot_have_resolution_message() -> None:
    with pytest.raises(ValueError, match="resolution_message"):
        Failure(
            failure_id=FailureId("failure-1"),
            job_id=JobId("job-1"),
            execution_id=None,
            event_id=None,
            command_id=None,
            interaction_id=None,
            failure_class=FailureClass.PERSISTENCE_FAILURE,
            message="database unavailable",
            details_ref=None,
            created_at=NOW,
            resolved_at=None,
            resolution_message="not actually resolved",
        )


def test_domain_records_are_immutable() -> None:
    source = EventSource("runtime", "rrs", None)

    with pytest.raises(FrozenInstanceError):
        source.provider = "changed"  # type: ignore[misc]

def test_execution_rejects_empty_ids_and_operation_key() -> None:
    with pytest.raises(ValueError, match="Execution IDs"):
        Execution(
            execution_id=ExecutionId(""),
            job_id=JobId("job-1"),
            owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
            operation_type=OperationType.GENERATE_ANALYSIS,
            operation_key=OperationKey("operation-key-1"),
            attempt_number=1,
            status=ExecutionStatus.CREATED,
            input_snapshot=object(),
            staged_outputs=(),
            committed_outputs=(),
            failure_id=None,
            created_at=NOW,
            started_at=None,
            completed_at=None,
        )

    with pytest.raises(ValueError, match="operation_key"):
        Execution(
            execution_id=ExecutionId("execution-1"),
            job_id=JobId("job-1"),
            owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
            operation_type=OperationType.GENERATE_ANALYSIS,
            operation_key=OperationKey(""),
            attempt_number=1,
            status=ExecutionStatus.CREATED,
            input_snapshot=object(),
            staged_outputs=(),
            committed_outputs=(),
            failure_id=None,
            created_at=NOW,
            started_at=None,
            completed_at=None,
        )


def test_execution_rejects_naive_and_backwards_timestamps() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        Execution(
            execution_id=ExecutionId("execution-1"),
            job_id=JobId("job-1"),
            owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
            operation_type=OperationType.GENERATE_ANALYSIS,
            operation_key=OperationKey("operation-key-1"),
            attempt_number=1,
            status=ExecutionStatus.CREATED,
            input_snapshot=object(),
            staged_outputs=(),
            committed_outputs=(),
            failure_id=None,
            created_at=datetime(2026, 8, 25, 12, 0),
            started_at=None,
            completed_at=None,
        )

    with pytest.raises(ValueError, match="started_at"):
        Execution(
            execution_id=ExecutionId("execution-1"),
            job_id=JobId("job-1"),
            owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
            operation_type=OperationType.GENERATE_ANALYSIS,
            operation_key=OperationKey("operation-key-1"),
            attempt_number=1,
            status=ExecutionStatus.RUNNING,
            input_snapshot=object(),
            staged_outputs=(),
            committed_outputs=(),
            failure_id=None,
            created_at=NOW,
            started_at=NOW - timedelta(seconds=1),
            completed_at=None,
        )

    with pytest.raises(ValueError, match="completed_at"):
        Execution(
            execution_id=ExecutionId("execution-1"),
            job_id=JobId("job-1"),
            owner_runtime_instance_id=RuntimeInstanceId("runtime-1"),
            operation_type=OperationType.GENERATE_ANALYSIS,
            operation_key=OperationKey("operation-key-1"),
            attempt_number=1,
            status=ExecutionStatus.FAILED,
            input_snapshot=object(),
            staged_outputs=(),
            committed_outputs=(),
            failure_id=FailureId("failure-1"),
            created_at=NOW,
            started_at=None,
            completed_at=NOW - timedelta(seconds=1),
        )


def test_event_source_requires_category_and_provider() -> None:
    with pytest.raises(ValueError, match="category and provider"):
        EventSource("", "rrs", None)

    with pytest.raises(ValueError, match="category and provider"):
        EventSource("runtime", "", None)


def test_event_rejects_empty_identity_negative_attempts_and_bad_claim() -> None:
    with pytest.raises(ValueError, match="event_id and event_type"):
        Event(
            event_id=EventId(""),
            event_type="test",
            job_id=None,
            payload={},
            source=EventSource("runtime", "rrs", None),
            correlation_id=None,
            causation_id=None,
            criticality=EventCriticality.INTEGRATION_ONLY,
            status=EventStatus.RECEIVED,
            attempt_count=0,
            owner_runtime_instance_id=None,
            lease_expires_at=None,
            created_at=NOW,
            processed_at=None,
        )

    with pytest.raises(ValueError, match="attempt_count"):
        Event(
            event_id=EventId("event-1"),
            event_type="test",
            job_id=None,
            payload={},
            source=EventSource("runtime", "rrs", None),
            correlation_id=None,
            causation_id=None,
            criticality=EventCriticality.INTEGRATION_ONLY,
            status=EventStatus.RECEIVED,
            attempt_count=-1,
            owner_runtime_instance_id=None,
            lease_expires_at=None,
            created_at=NOW,
            processed_at=None,
        )

    with pytest.raises(ValueError, match="owner and lease"):
        Event(
            event_id=EventId("event-1"),
            event_type="test",
            job_id=None,
            payload={},
            source=EventSource("runtime", "rrs", None),
            correlation_id=None,
            causation_id=None,
            criticality=EventCriticality.INTEGRATION_ONLY,
            status=EventStatus.PROCESSING,
            attempt_count=1,
            owner_runtime_instance_id=None,
            lease_expires_at=NOW + timedelta(minutes=1),
            created_at=NOW,
            processed_at=None,
        )


def test_command_rejects_empty_identity_and_bad_claim() -> None:
    with pytest.raises(ValueError, match="command_id and command_type"):
        Command(
            command_id=CommandId(""),
            command_type="test",
            job_id=None,
            payload={},
            status=CommandStatus.PENDING,
            dedupe_key=None,
            causation_event_id=None,
            owner_runtime_instance_id=None,
            lease_expires_at=None,
            attempt_count=0,
            created_at=NOW,
            completed_at=None,
        )

    with pytest.raises(ValueError, match="owner and lease"):
        Command(
            command_id=CommandId("command-1"),
            command_type="test",
            job_id=None,
            payload={},
            status=CommandStatus.PROCESSING,
            dedupe_key=None,
            causation_event_id=None,
            owner_runtime_instance_id=None,
            lease_expires_at=NOW + timedelta(minutes=1),
            attempt_count=1,
            created_at=NOW,
            completed_at=None,
        )


def test_interaction_rejects_empty_identity_and_backwards_completion() -> None:
    with pytest.raises(ValueError, match="IDs and provider"):
        Interaction(
            interaction_id=InteractionId(""),
            job_id=JobId("job-1"),
            interaction_type=InteractionType.MANUAL_REVIEW,
            provider="discord",
            provider_context={},
            professional_context={},
            status=InteractionStatus.PENDING,
            created_at=NOW,
            updated_at=NOW,
            completed_at=None,
        )

    with pytest.raises(ValueError, match="completed_at"):
        Interaction(
            interaction_id=InteractionId("interaction-1"),
            job_id=JobId("job-1"),
            interaction_type=InteractionType.MANUAL_REVIEW,
            provider="discord",
            provider_context={},
            professional_context={},
            status=InteractionStatus.COMPLETED,
            created_at=NOW,
            updated_at=NOW,
            completed_at=NOW - timedelta(seconds=1),
        )


def test_interaction_message_rejects_empty_identity_and_metadata() -> None:
    with pytest.raises(ValueError, match="Message IDs"):
        InteractionMessage(
            message_id=MessageId(""),
            interaction_id=InteractionId("interaction-1"),
            provider="discord",
            provider_message_id=None,
            provider_created_at=None,
            direction="inbound",
            message_type="human_message",
            content="hello",
            content_ref=None,
            persisted_at=NOW,
            processed_at=None,
            processed_by_continuation_id=None,
        )

    with pytest.raises(ValueError, match="provider, direction, and message_type"):
        InteractionMessage(
            message_id=MessageId("message-1"),
            interaction_id=InteractionId("interaction-1"),
            provider="",
            provider_message_id=None,
            provider_created_at=None,
            direction="inbound",
            message_type="human_message",
            content="hello",
            content_ref=None,
            persisted_at=NOW,
            processed_at=None,
            processed_by_continuation_id=None,
        )


def test_failure_rejects_empty_identity_and_backwards_resolution() -> None:
    with pytest.raises(ValueError, match="failure_id, job_id, and message"):
        Failure(
            failure_id=FailureId(""),
            job_id=JobId("job-1"),
            execution_id=None,
            event_id=None,
            command_id=None,
            interaction_id=None,
            failure_class=FailureClass.PERSISTENCE_FAILURE,
            message="database unavailable",
            details_ref=None,
            created_at=NOW,
            resolved_at=None,
            resolution_message=None,
        )

    with pytest.raises(ValueError, match="resolved_at"):
        Failure(
            failure_id=FailureId("failure-1"),
            job_id=JobId("job-1"),
            execution_id=None,
            event_id=None,
            command_id=None,
            interaction_id=None,
            failure_class=FailureClass.PERSISTENCE_FAILURE,
            message="database unavailable",
            details_ref=None,
            created_at=NOW,
            resolved_at=NOW - timedelta(seconds=1),
            resolution_message="resolved",
        )