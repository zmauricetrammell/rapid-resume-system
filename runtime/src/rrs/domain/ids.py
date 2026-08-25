"""Strongly typed opaque identifiers for the RRS runtime."""

from typing import NewType

JobId = NewType("JobId", str)
ExecutionId = NewType("ExecutionId", str)
CommandId = NewType("CommandId", str)
EventId = NewType("EventId", str)
InteractionId = NewType("InteractionId", str)
MessageId = NewType("MessageId", str)
FailureId = NewType("FailureId", str)
ArtifactId = NewType("ArtifactId", str)
OperationKey = NewType("OperationKey", str)
RuntimeInstanceId = NewType("RuntimeInstanceId", str)
InvocationId = NewType("InvocationId", str)
RoutingDecisionId = NewType("RoutingDecisionId", str)
CommitGroupId = NewType("CommitGroupId", str)

__all__ = [
    "ArtifactId", "CommandId", "CommitGroupId", "EventId", "ExecutionId",
    "FailureId", "InteractionId", "InvocationId", "JobId", "MessageId",
    "OperationKey", "RoutingDecisionId", "RuntimeInstanceId",
]
