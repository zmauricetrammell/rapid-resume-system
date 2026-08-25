from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from rrs.domain.artifacts import ArtifactRef, ArtifactVersion
from rrs.domain.enums import (
    ArtifactType,
    HealthStatus,
    InteractionProjectionStatus,
    LifecyclePhase,
    MutationType,
    OperationType,
    RuntimeOperationStatus,
)
from rrs.domain.ids import ArtifactId, ExecutionId, FailureId
from rrs.domain.jobs import (
    HealthState,
    InteractionProjection,
    LifecycleState,
    OperationState,
)
from rrs.domain.mutations import (
    CollectionAddMutation,
    CollectionRemoveMutation,
    CollectionReplaceMutation,
    CollectionTarget,
    CollectionUpsertVersionMutation,
    HealthMutation,
    InteractionProjectionMutation,
    LifecycleTransitionMutation,
    OperationStateMutation,
    PointerTarget,
    SetPointerMutation,
)

NOW = datetime(2026, 8, 24, 12, 0, tzinfo=UTC)


def ref(
    artifact_type: ArtifactType,
    artifact_id: str,
    version: int = 1,
) -> ArtifactRef:
    return ArtifactRef(
        artifact_type=artifact_type,
        artifact_id=ArtifactId(artifact_id),
        artifact_version=ArtifactVersion(version),
        uri=f"file:///data/{artifact_id}/v{version}",
    )


def test_set_pointer_mutation_preserves_exact_ref() -> None:
    value = ref(ArtifactType.JOB_EXPERIENCE_ANALYSIS, "jea-1", 2)
    mutation = SetPointerMutation(PointerTarget.JEA, value)

    assert mutation.target is PointerTarget.JEA
    assert mutation.value == value
    assert mutation.mutation_type is MutationType.SET


def test_optional_scalar_pointer_can_be_cleared() -> None:
    mutation = SetPointerMutation(PointerTarget.EVALUATION, None)
    assert mutation.value is None


def test_target_job_cannot_be_cleared() -> None:
    with pytest.raises(ValueError, match="cannot be cleared"):
        SetPointerMutation(PointerTarget.TARGET_JOB, None)


def test_set_pointer_rejects_wrong_artifact_type() -> None:
    with pytest.raises(ValueError, match="jea"):
        SetPointerMutation(
            PointerTarget.JEA,
            ref(ArtifactType.RESUME_EVALUATION, "wrong"),
        )


@pytest.mark.parametrize(
    ("mutation_type", "expected"),
    [
        (CollectionAddMutation, MutationType.ADD),
        (CollectionRemoveMutation, MutationType.REMOVE),
        (CollectionUpsertVersionMutation, MutationType.UPSERT_VERSION),
    ],
)
def test_single_ref_collection_mutations_preserve_type(
    mutation_type: type[
        CollectionAddMutation
        | CollectionRemoveMutation
        | CollectionUpsertVersionMutation
    ],
    expected: MutationType,
) -> None:
    value = ref(ArtifactType.EVIDENCE_REQUEST, "erq-1")
    mutation = mutation_type(CollectionTarget.ACTIVE_ERQS, value)

    assert mutation.value == value
    assert mutation.mutation_type is expected


@pytest.mark.parametrize(
    "mutation_type",
    [
        CollectionAddMutation,
        CollectionRemoveMutation,
        CollectionUpsertVersionMutation,
    ],
)
def test_collection_mutations_reject_wrong_artifact_type(
    mutation_type: type[
        CollectionAddMutation
        | CollectionRemoveMutation
        | CollectionUpsertVersionMutation
    ],
) -> None:
    with pytest.raises(ValueError, match="active_erqs"):
        mutation_type(
            CollectionTarget.ACTIVE_ERQS,
            ref(ArtifactType.EVIDENCE_RESPONSE, "response-1"),
        )


def test_collection_replace_is_deterministic() -> None:
    mutation = CollectionReplaceMutation(
        CollectionTarget.JER_SET,
        (
            ref(ArtifactType.JOB_EXPERIENCE_RECORD, "jer-b"),
            ref(ArtifactType.JOB_EXPERIENCE_RECORD, "jer-a", 2),
        ),
    )

    assert [str(item.artifact_id) for item in mutation.values] == ["jer-a", "jer-b"]
    assert mutation.mutation_type is MutationType.REPLACE


def test_collection_replace_rejects_duplicate_exact_refs() -> None:
    value = ref(ArtifactType.EVIDENCE_RESPONSE, "response-1")

    with pytest.raises(ValueError, match="duplicate"):
        CollectionReplaceMutation(
            CollectionTarget.UNINTEGRATED_EVIDENCE_RESPONSES,
            (value, value),
        )


def test_upsert_version_preserves_one_logical_artifact_identity() -> None:
    mutation = CollectionUpsertVersionMutation(
        CollectionTarget.JER_SET,
        ref(ArtifactType.JOB_EXPERIENCE_RECORD, "jer-1", 4),
    )

    assert mutation.value.artifact_id == "jer-1"
    assert mutation.value.artifact_version == ArtifactVersion(4)


def test_lifecycle_transition_mutation_wraps_canonical_state() -> None:
    state = LifecycleState(
        phase=LifecyclePhase.ANALYSIS,
        entered_at=NOW,
    )
    assert LifecycleTransitionMutation(state).state == state


def test_operation_state_mutation_wraps_canonical_state() -> None:
    state = OperationState(
        status=RuntimeOperationStatus.RUNNING,
        operation_type=OperationType.GENERATE_ANALYSIS,
        execution_id=ExecutionId("execution-1"),
        started_at=NOW,
    )
    assert OperationStateMutation(state).state == state


def test_interaction_projection_mutation_wraps_canonical_state() -> None:
    state = InteractionProjection(
        status=InteractionProjectionStatus.NONE,
        interaction_type=None,
        interaction_id=None,
        started_at=None,
        last_activity_at=None,
    )
    assert InteractionProjectionMutation(state).state == state


def test_health_mutation_wraps_canonical_state() -> None:
    state = HealthState(
        status=HealthStatus.BLOCKED,
        failure_id=FailureId("failure-1"),
        retry_count=1,
    )
    assert HealthMutation(state).state == state


def test_mutation_objects_are_immutable() -> None:
    mutation = SetPointerMutation(
        PointerTarget.RESUME,
        ref(ArtifactType.TARGETED_RESUME, "resume-1"),
    )

    with pytest.raises(FrozenInstanceError):
        mutation.value = None  # type: ignore[misc]


def test_pointer_and_collection_targets_are_distinct_types() -> None:
    assert PointerTarget.JEA != CollectionTarget.JER_SET
    assert isinstance(PointerTarget.JEA, PointerTarget)
    assert isinstance(CollectionTarget.JER_SET, CollectionTarget)
