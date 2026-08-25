"""Operation Specification domain model."""

from dataclasses import dataclass
from hashlib import sha256

from rrs.domain.artifacts import ArtifactRef, ResourceRef, SchemaRef
from rrs.domain.enums import (
    ArtifactType,
    LifecyclePhase,
    MutationType,
    OperationType,
    RetrievalRequirement,
)
from rrs.domain.mutations import CollectionTarget, PointerTarget

type MutationTarget = PointerTarget | CollectionTarget


def _require_nonempty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} must be nonempty")


def _require_unique(values: tuple[str, ...], field_name: str) -> None:
    if len(set(values)) != len(values):
        raise ValueError(f"{field_name} must not contain duplicates")


@dataclass(frozen=True, order=True)
class DependencyFingerprint:
    dependency_type: str
    logical_name: str
    identity: str

    def __post_init__(self) -> None:
        _require_nonempty(self.dependency_type, "dependency_type")
        _require_nonempty(self.logical_name, "logical_name")
        _require_nonempty(self.identity, "identity")


@dataclass(frozen=True)
class InputSnapshot:
    identity_dependencies: tuple[DependencyFingerprint, ...]
    freshness_dependencies: tuple[DependencyFingerprint, ...]

    def __post_init__(self) -> None:
        if len(set(self.identity_dependencies)) != len(self.identity_dependencies):
            raise ValueError("identity_dependencies contain duplicates")
        if len(set(self.freshness_dependencies)) != len(self.freshness_dependencies):
            raise ValueError("freshness_dependencies contain duplicates")


@dataclass(frozen=True)
class ProfessionalBinding:
    professional_role: str
    contract: ResourceRef
    task: ResourceRef

    def __post_init__(self) -> None:
        _require_nonempty(self.professional_role, "professional_role")


@dataclass(frozen=True)
class RetrievalSpecification:
    requirement: RetrievalRequirement
    evidence_source_key: str | None

    def __post_init__(self) -> None:
        if self.requirement is RetrievalRequirement.NONE:
            if self.evidence_source_key is not None:
                raise ValueError("retrieval requirement none cannot specify evidence_source_key")
        elif not self.evidence_source_key:
            raise ValueError("retrieval requirement requires evidence_source_key")


@dataclass(frozen=True)
class OutputContract:
    required_artifact_types: tuple[ArtifactType, ...]
    coupled_groups: tuple[tuple[ArtifactType, ...], ...]
    schemas: tuple[SchemaRef, ...]

    def __post_init__(self) -> None:
        if len(set(self.required_artifact_types)) != len(self.required_artifact_types):
            raise ValueError("required_artifact_types contain duplicates")

        required = set(self.required_artifact_types)
        for group in self.coupled_groups:
            if not group:
                raise ValueError("coupled output group cannot be empty")
            if len(set(group)) != len(group):
                raise ValueError("coupled output group contains duplicates")
            if not set(group).issubset(required):
                raise ValueError("coupled output group must reference required outputs")

        if len(set(self.schemas)) != len(self.schemas):
            raise ValueError("schemas contain duplicate exact references")


@dataclass(frozen=True, order=True)
class PointerMutationAuthority:
    target: MutationTarget
    mutation_type: MutationType

    def __post_init__(self) -> None:
        if isinstance(self.target, PointerTarget):
            if self.mutation_type is not MutationType.SET:
                raise ValueError("scalar pointer authority supports only SET")
        elif isinstance(self.target, CollectionTarget):
            if self.mutation_type is MutationType.SET:
                raise ValueError("collection authority cannot use SET")


@dataclass(frozen=True)
class OperationSpecification:
    operation_type: OperationType
    handler_key: str
    allowed_lifecycle_phases: frozenset[LifecyclePhase]
    professional_binding: ProfessionalBinding
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    identity_dependencies: tuple[str, ...]
    freshness_dependencies: tuple[str, ...]
    retrieval: RetrievalSpecification
    output_contract: OutputContract
    pointer_authority: frozenset[PointerMutationAuthority]
    deterministic_reconciliation: tuple[str, ...]
    retry_policy_ref: str
    specification_hash: str

    def __post_init__(self) -> None:
        _require_nonempty(self.handler_key, "handler_key")
        _require_nonempty(self.retry_policy_ref, "retry_policy_ref")
        _require_nonempty(self.specification_hash, "specification_hash")

        if not self.allowed_lifecycle_phases:
            raise ValueError("allowed_lifecycle_phases must not be empty")

        for values, field_name in (
            (self.required_inputs, "required_inputs"),
            (self.optional_inputs, "optional_inputs"),
            (self.identity_dependencies, "identity_dependencies"),
            (self.freshness_dependencies, "freshness_dependencies"),
            (self.deterministic_reconciliation, "deterministic_reconciliation"),
        ):
            _require_unique(values, field_name)
            if any(not value for value in values):
                raise ValueError(f"{field_name} must not contain empty values")

        overlap = set(self.required_inputs) & set(self.optional_inputs)
        if overlap:
            raise ValueError("required_inputs and optional_inputs must not overlap")


def artifact_dependency(ref: ArtifactRef) -> DependencyFingerprint:
    """Build semantic dependency identity from an exact artifact reference."""
    identity = f"{ref.artifact_type.value}:{ref.artifact_id}:{ref.artifact_version.value}"
    return DependencyFingerprint(
        dependency_type="artifact",
        logical_name=ref.artifact_type.value,
        identity=identity,
    )


def resource_dependency(ref: ResourceRef) -> DependencyFingerprint:
    """Build semantic dependency identity from resource content, excluding Git provenance."""
    return DependencyFingerprint(
        dependency_type="resource",
        logical_name=ref.path,
        identity=ref.content_hash,
    )


def schema_dependency(ref: SchemaRef) -> DependencyFingerprint:
    """Build semantic dependency identity from schema content, excluding Git provenance."""
    return DependencyFingerprint(
        dependency_type="schema",
        logical_name=ref.path,
        identity=ref.content_hash,
    )


def semantic_fingerprint(dependencies: tuple[DependencyFingerprint, ...]) -> str:
    """Create a deterministic hash from ordered semantic dependency fingerprints."""
    payload = "\n".join(
        f"{item.dependency_type}\0{item.logical_name}\0{item.identity}"
        for item in dependencies
    )
    return sha256(payload.encode("utf-8")).hexdigest()


__all__ = [
    "DependencyFingerprint",
    "InputSnapshot",
    "MutationTarget",
    "OperationSpecification",
    "OutputContract",
    "PointerMutationAuthority",
    "ProfessionalBinding",
    "RetrievalSpecification",
    "artifact_dependency",
    "resource_dependency",
    "schema_dependency",
    "semantic_fingerprint",
]
