from __future__ import annotations

from rrs.domain.ids import (
    ArtifactId,
    CommandId,
    CommitGroupId,
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


def test_id_values_serialize_to_canonical_strings() -> None:
    assert JobId("job-1") == "job-1"
    assert ExecutionId("exec-1") == "exec-1"
    assert CommandId("cmd-1") == "cmd-1"
    assert EventId("evt-1") == "evt-1"
    assert InteractionId("int-1") == "int-1"
    assert MessageId("msg-1") == "msg-1"
    assert FailureId("fail-1") == "fail-1"
    assert ArtifactId("artifact-1") == "artifact-1"
    assert OperationKey("op-key") == "op-key"
    assert RuntimeInstanceId("runtime-1") == "runtime-1"
    assert InvocationId("inv-1") == "inv-1"
    assert RoutingDecisionId("route-1") == "route-1"
    assert CommitGroupId("commit-1") == "commit-1"


def test_newtype_ids_are_runtime_strings() -> None:
    job_id = JobId("same-value")
    execution_id = ExecutionId("same-value")

    assert isinstance(job_id, str)
    assert isinstance(execution_id, str)
