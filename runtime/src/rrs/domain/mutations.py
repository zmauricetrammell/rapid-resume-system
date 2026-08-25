"""Typed RuntimeJob mutation contracts.

These immutable values describe requested state changes. They do not authorize,
persist, apply, revision, or emit events for those changes.
"""

from dataclasses import dataclass, field
from enum import StrEnum

from rrs.domain.artifacts import ArtifactRef
from rrs.domain.enums import ArtifactType, MutationType
from rrs.domain.jobs import (
    HealthState,
    InteractionProjection,
    LifecycleState,
    OperationState,
)


class PointerTarget(StrEnum):
    """Canonical scalar professional-state pointer targets."""

    TARGET_JOB = "target_job"
    JEA = "jea"
    RESUME = "resume"
    WCM = "wcm"
    EVALUATION = "evaluation"


class CollectionTarget(StrEnum):
    """Canonical professional-state collection targets."""

    JER_SET = "jer_set"
    ACTIVE_ERQS = "active_erqs"
    UNINTEGRATED_EVIDENCE_RESPONSES = "unintegrated_evidence_responses"


_POINTER_ARTIFACT_TYPES: dict[PointerTarget, ArtifactType] = {
    PointerTarget.TARGET_JOB: ArtifactType.TARGET_JOB,
    PointerTarget.JEA: ArtifactType.JOB_EXPERIENCE_ANALYSIS,
    PointerTarget.RESUME: ArtifactType.TARGETED_RESUME,
    PointerTarget.WCM: ArtifactType.WRITER_CONTENT_MANIFEST,
    PointerTarget.EVALUATION: ArtifactType.RESUME_EVALUATION,
}

_COLLECTION_ARTIFACT_TYPES: dict[CollectionTarget, ArtifactType] = {
    CollectionTarget.JER_SET: ArtifactType.JOB_EXPERIENCE_RECORD,
    CollectionTarget.ACTIVE_ERQS: ArtifactType.EVIDENCE_REQUEST,
    CollectionTarget.UNINTEGRATED_EVIDENCE_RESPONSES: ArtifactType.EVIDENCE_RESPONSE,
}


def _validate_pointer_value(
    target: PointerTarget,
    value: ArtifactRef | None,
) -> None:
    if target is PointerTarget.TARGET_JOB and value is None:
        raise ValueError("target_job cannot be cleared")

    if value is not None and value.artifact_type is not _POINTER_ARTIFACT_TYPES[target]:
        expected = _POINTER_ARTIFACT_TYPES[target].value
        raise ValueError(f"{target.value} must reference {expected}")


def _validate_collection_ref(target: CollectionTarget, value: ArtifactRef) -> None:
    if value.artifact_type is not _COLLECTION_ARTIFACT_TYPES[target]:
        expected = _COLLECTION_ARTIFACT_TYPES[target].value
        raise ValueError(f"{target.value} must contain {expected}")


def _canonical_collection(
    target: CollectionTarget,
    values: tuple[ArtifactRef, ...],
) -> tuple[ArtifactRef, ...]:
    for value in values:
        _validate_collection_ref(target, value)

    if len(set(values)) != len(values):
        raise ValueError(f"{target.value} replacement contains duplicate exact references")

    return tuple(
        sorted(
            values,
            key=lambda ref: (
                str(ref.artifact_id),
                ref.artifact_version.value,
                ref.uri,
            ),
        )
    )


@dataclass(frozen=True)
class SetPointerMutation:
    """Request SET of one scalar professional-state pointer."""

    target: PointerTarget
    value: ArtifactRef | None
    mutation_type: MutationType = field(
        default=MutationType.SET,
        init=False,
    )

    def __post_init__(self) -> None:
        _validate_pointer_value(self.target, self.value)


@dataclass(frozen=True)
class CollectionAddMutation:
    """Request ADD of one exact artifact reference to a collection."""

    target: CollectionTarget
    value: ArtifactRef
    mutation_type: MutationType = field(
        default=MutationType.ADD,
        init=False,
    )

    def __post_init__(self) -> None:
        _validate_collection_ref(self.target, self.value)


@dataclass(frozen=True)
class CollectionRemoveMutation:
    """Request REMOVE of one exact artifact reference from a collection."""

    target: CollectionTarget
    value: ArtifactRef
    mutation_type: MutationType = field(
        default=MutationType.REMOVE,
        init=False,
    )

    def __post_init__(self) -> None:
        _validate_collection_ref(self.target, self.value)


@dataclass(frozen=True)
class CollectionReplaceMutation:
    """Request deterministic replacement of a professional collection."""

    target: CollectionTarget
    values: tuple[ArtifactRef, ...]
    mutation_type: MutationType = field(
        default=MutationType.REPLACE,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "values",
            _canonical_collection(self.target, self.values),
        )


@dataclass(frozen=True)
class CollectionUpsertVersionMutation:
    """Request current-version upsert for one logical artifact identity."""

    target: CollectionTarget
    value: ArtifactRef
    mutation_type: MutationType = field(
        default=MutationType.UPSERT_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        _validate_collection_ref(self.target, self.value)


@dataclass(frozen=True)
class LifecycleTransitionMutation:
    """Request replacement of the RuntimeJob lifecycle projection."""

    state: LifecycleState


@dataclass(frozen=True)
class OperationStateMutation:
    """Request replacement of the RuntimeJob operation projection."""

    state: OperationState


@dataclass(frozen=True)
class InteractionProjectionMutation:
    """Request replacement of the RuntimeJob Interaction projection."""

    state: InteractionProjection


@dataclass(frozen=True)
class HealthMutation:
    """Request replacement of the RuntimeJob health projection."""

    state: HealthState


type RuntimeJobMutation = (
    SetPointerMutation
    | CollectionAddMutation
    | CollectionRemoveMutation
    | CollectionReplaceMutation
    | CollectionUpsertVersionMutation
    | LifecycleTransitionMutation
    | OperationStateMutation
    | InteractionProjectionMutation
    | HealthMutation
)


__all__ = [
    "CollectionAddMutation",
    "CollectionRemoveMutation",
    "CollectionReplaceMutation",
    "CollectionTarget",
    "CollectionUpsertVersionMutation",
    "HealthMutation",
    "InteractionProjectionMutation",
    "LifecycleTransitionMutation",
    "OperationStateMutation",
    "PointerTarget",
    "RuntimeJobMutation",
    "SetPointerMutation",
]
