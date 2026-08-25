"""Durable runtime build and invocation provenance records."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType

from rrs.domain.enums import OperationType
from rrs.domain.ids import ExecutionId, InvocationId, RuntimeInstanceId


@dataclass(frozen=True)
class RuntimeInstance:
    runtime_instance_id: RuntimeInstanceId
    git_sha: str
    image_digest: str | None
    operation_registry_hash: str
    built_at: datetime | None
    started_at: datetime
    stopped_at: datetime | None

    def __post_init__(self) -> None:
        if not self.runtime_instance_id:
            raise ValueError("runtime_instance_id must be nonempty")
        if not self.git_sha or not self.operation_registry_hash:
            raise ValueError("runtime build identity fields must be nonempty")


@dataclass(frozen=True)
class InvocationProvenance:
    invocation_id: InvocationId
    execution_id: ExecutionId
    operation_type: OperationType
    operation_specification_hash: str
    operation_registry_hash: str
    runtime_git_sha: str
    runtime_image_digest: str | None
    provider: str
    model: str
    provider_request_id: str | None
    resources: Mapping[str, object]
    usage: Mapping[str, object] | None
    latency_ms: int | None
    started_at: datetime
    completed_at: datetime | None

    def __post_init__(self) -> None:
        if not self.invocation_id or not self.execution_id:
            raise ValueError("invocation identifiers must be nonempty")
        if not self.operation_specification_hash or not self.operation_registry_hash:
            raise ValueError("operation provenance hashes must be nonempty")
        if not self.runtime_git_sha or not self.provider or not self.model:
            raise ValueError("runtime/provider provenance fields must be nonempty")
        object.__setattr__(self, "resources", MappingProxyType(dict(self.resources)))
        if self.usage is not None:
            object.__setattr__(self, "usage", MappingProxyType(dict(self.usage)))


__all__ = ["InvocationProvenance", "RuntimeInstance"]
