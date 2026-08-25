from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rrs.domain.artifacts import ArtifactRef, ArtifactVersion, ResourceRef, SchemaRef
from rrs.domain.enums import (
    ArtifactType,
    LifecyclePhase,
    MutationType,
    OperationType,
    RetrievalRequirement,
)
from rrs.domain.ids import ArtifactId
from rrs.domain.mutations import CollectionTarget, PointerTarget
from rrs.domain.operations import (
    DependencyFingerprint,
    InputSnapshot,
    OperationSpecification,
    OutputContract,
    PointerMutationAuthority,
    ProfessionalBinding,
    RetrievalSpecification,
    artifact_dependency,
    resource_dependency,
    schema_dependency,
    semantic_fingerprint,
)


def resource(path: str, content_hash: str, git_commit: str | None = None) -> ResourceRef:
    return ResourceRef(path=path, content_hash=content_hash, git_commit=git_commit)


def schema(path: str, content_hash: str, git_commit: str | None = None) -> SchemaRef:
    return SchemaRef(path=path, content_hash=content_hash, git_commit=git_commit)


def binding() -> ProfessionalBinding:
    return ProfessionalBinding(
        professional_role="researcher",
        contract=resource("agents/researcher/contract.md", "sha256:contract"),
        task=resource("agents/researcher/tasks/generate-analysis.md", "sha256:task"),
    )


def output_contract() -> OutputContract:
    return OutputContract(
        required_artifact_types=(ArtifactType.JOB_EXPERIENCE_ANALYSIS,),
        coupled_groups=(),
        schemas=(schema("schemas/job-experience-analysis.yaml", "sha256:jea-schema"),),
    )


def operation_spec() -> OperationSpecification:
    return OperationSpecification(
        operation_type=OperationType.GENERATE_ANALYSIS,
        handler_key="generate_analysis",
        allowed_lifecycle_phases=frozenset({LifecyclePhase.ANALYSIS}),
        professional_binding=binding(),
        required_inputs=("target_job", "jer_set"),
        optional_inputs=("resume_evaluation",),
        identity_dependencies=("target_job", "jer_set", "researcher_contract"),
        freshness_dependencies=("target_job", "jer_set"),
        retrieval=RetrievalSpecification(
            requirement=RetrievalRequirement.REQUIRED,
            evidence_source_key="professional_evidence",
        ),
        output_contract=output_contract(),
        pointer_authority=frozenset(
            {
                PointerMutationAuthority(
                    target=PointerTarget.JEA,
                    mutation_type=MutationType.SET,
                )
            }
        ),
        deterministic_reconciliation=("reconcile_active_erqs_from_jea",),
        retry_policy_ref="professional_evidence_required",
        specification_hash="sha256:spec",
    )


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    [
        ("dependency_type", {"dependency_type": "", "logical_name": "x", "identity": "y"}),
        ("logical_name", {"dependency_type": "artifact", "logical_name": "", "identity": "y"}),
        ("identity", {"dependency_type": "artifact", "logical_name": "x", "identity": ""}),
    ],
)
def test_dependency_fingerprint_requires_nonempty_fields(
    field_name: str,
    kwargs: dict[str, str],
) -> None:
    with pytest.raises(ValueError, match=field_name):
        DependencyFingerprint(**kwargs)


def test_input_snapshot_keeps_identity_and_freshness_separate() -> None:
    identity = DependencyFingerprint("artifact", "target_job", "artifact:1")
    freshness = DependencyFingerprint("artifact", "jer_set", "jer:7")

    snapshot = InputSnapshot(
        identity_dependencies=(identity,),
        freshness_dependencies=(freshness,),
    )

    assert snapshot.identity_dependencies == (identity,)
    assert snapshot.freshness_dependencies == (freshness,)


def test_input_snapshot_rejects_duplicate_dependencies() -> None:
    dep = DependencyFingerprint("artifact", "target_job", "artifact:1")

    with pytest.raises(ValueError, match="identity_dependencies"):
        InputSnapshot(
            identity_dependencies=(dep, dep),
            freshness_dependencies=(),
        )

    with pytest.raises(ValueError, match="freshness_dependencies"):
        InputSnapshot(
            identity_dependencies=(),
            freshness_dependencies=(dep, dep),
        )


def test_professional_binding_requires_role() -> None:
    with pytest.raises(ValueError, match="professional_role"):
        ProfessionalBinding(
            professional_role="",
            contract=resource("contract.md", "hash"),
            task=resource("task.md", "hash"),
        )


def test_retrieval_none_rejects_source() -> None:
    with pytest.raises(ValueError, match="none"):
        RetrievalSpecification(
            requirement=RetrievalRequirement.NONE,
            evidence_source_key="should-not-exist",
        )


@pytest.mark.parametrize(
    "requirement",
    [RetrievalRequirement.OPTIONAL, RetrievalRequirement.REQUIRED],
)
def test_retrieval_enabled_requires_source(requirement: RetrievalRequirement) -> None:
    with pytest.raises(ValueError, match="evidence_source_key"):
        RetrievalSpecification(requirement=requirement, evidence_source_key=None)


def test_output_contract_validates_coupled_groups() -> None:
    contract = OutputContract(
        required_artifact_types=(
            ArtifactType.TARGETED_RESUME,
            ArtifactType.WRITER_CONTENT_MANIFEST,
        ),
        coupled_groups=(
            (
                ArtifactType.TARGETED_RESUME,
                ArtifactType.WRITER_CONTENT_MANIFEST,
            ),
        ),
        schemas=(),
    )

    assert len(contract.coupled_groups) == 1


def test_output_contract_rejects_invalid_groups_and_duplicates() -> None:
    with pytest.raises(ValueError, match="required_artifact_types"):
        OutputContract(
            required_artifact_types=(
                ArtifactType.TARGETED_RESUME,
                ArtifactType.TARGETED_RESUME,
            ),
            coupled_groups=(),
            schemas=(),
        )

    with pytest.raises(ValueError, match="cannot be empty"):
        OutputContract(
            required_artifact_types=(ArtifactType.TARGETED_RESUME,),
            coupled_groups=((),),
            schemas=(),
        )

    with pytest.raises(ValueError, match="required outputs"):
        OutputContract(
            required_artifact_types=(ArtifactType.TARGETED_RESUME,),
            coupled_groups=((ArtifactType.WRITER_CONTENT_MANIFEST,),),
            schemas=(),
        )


def test_pointer_authority_rejects_invalid_target_mutation_pairs() -> None:
    with pytest.raises(ValueError, match="only SET"):
        PointerMutationAuthority(
            target=PointerTarget.JEA,
            mutation_type=MutationType.REPLACE,
        )

    with pytest.raises(ValueError, match="cannot use SET"):
        PointerMutationAuthority(
            target=CollectionTarget.JER_SET,
            mutation_type=MutationType.SET,
        )


def test_operation_specification_represents_effective_semantics() -> None:
    spec = operation_spec()

    assert spec.operation_type is OperationType.GENERATE_ANALYSIS
    assert spec.allowed_lifecycle_phases == frozenset({LifecyclePhase.ANALYSIS})
    assert spec.output_contract.required_artifact_types == (
        ArtifactType.JOB_EXPERIENCE_ANALYSIS,
    )


def test_operation_specification_rejects_empty_required_fields() -> None:
    spec = operation_spec()

    with pytest.raises(ValueError, match="handler_key"):
        OperationSpecification(**{**spec.__dict__, "handler_key": ""})

    with pytest.raises(ValueError, match="allowed_lifecycle_phases"):
        OperationSpecification(**{**spec.__dict__, "allowed_lifecycle_phases": frozenset()})

    with pytest.raises(ValueError, match="overlap"):
        OperationSpecification(
            **{
                **spec.__dict__,
                "required_inputs": ("target_job",),
                "optional_inputs": ("target_job",),
            }
        )


def test_semantic_resource_identity_ignores_git_only_change() -> None:
    first = resource("agents/researcher/contract.md", "sha256:same", "commit-a")
    second = resource("agents/researcher/contract.md", "sha256:same", "commit-b")

    assert resource_dependency(first) == resource_dependency(second)


def test_semantic_schema_identity_ignores_git_only_change() -> None:
    first = schema("schemas/jea.yaml", "sha256:same", "commit-a")
    second = schema("schemas/jea.yaml", "sha256:same", "commit-b")

    assert schema_dependency(first) == schema_dependency(second)


def test_artifact_dependency_uses_exact_version() -> None:
    first = ArtifactRef(
        artifact_type=ArtifactType.TARGET_JOB,
        artifact_id=ArtifactId("target-job"),
        artifact_version=ArtifactVersion(1),
        uri="file:///target/v1",
    )
    second = ArtifactRef(
        artifact_type=ArtifactType.TARGET_JOB,
        artifact_id=ArtifactId("target-job"),
        artifact_version=ArtifactVersion(2),
        uri="file:///target/v2",
    )

    assert artifact_dependency(first) != artifact_dependency(second)


def test_semantic_fingerprint_is_deterministic_and_order_sensitive() -> None:
    first = DependencyFingerprint("artifact", "target_job", "a")
    second = DependencyFingerprint("resource", "contract", "b")

    assert semantic_fingerprint((first, second)) == semantic_fingerprint((first, second))
    assert semantic_fingerprint((first, second)) != semantic_fingerprint((second, first))


def test_operation_specification_is_immutable() -> None:
    spec = operation_spec()

    with pytest.raises(FrozenInstanceError):
        spec.handler_key = "changed"  # type: ignore[misc]

def test_output_contract_rejects_duplicate_group_members_and_duplicate_schemas() -> None:
    with pytest.raises(ValueError, match="contains duplicates"):
        OutputContract(
            required_artifact_types=(
                ArtifactType.TARGETED_RESUME,
                ArtifactType.WRITER_CONTENT_MANIFEST,
            ),
            coupled_groups=(
                (
                    ArtifactType.TARGETED_RESUME,
                    ArtifactType.TARGETED_RESUME,
                ),
            ),
            schemas=(),
        )

    duplicate_schema = schema("schemas/resume.yaml", "sha256:resume")

    with pytest.raises(ValueError, match="schemas contain duplicate"):
        OutputContract(
            required_artifact_types=(ArtifactType.TARGETED_RESUME,),
            coupled_groups=(),
            schemas=(duplicate_schema, duplicate_schema),
        )


def test_operation_specification_rejects_empty_and_duplicate_semantic_lists() -> None:
    spec = operation_spec()

    with pytest.raises(ValueError, match="retry_policy_ref"):
        OperationSpecification(
            **{
                **spec.__dict__,
                "retry_policy_ref": "",
            }
        )

    with pytest.raises(ValueError, match="specification_hash"):
        OperationSpecification(
            **{
                **spec.__dict__,
                "specification_hash": "",
            }
        )

    with pytest.raises(ValueError, match="required_inputs"):
        OperationSpecification(
            **{
                **spec.__dict__,
                "required_inputs": ("target_job", "target_job"),
            }
        )

    with pytest.raises(ValueError, match="must not contain empty"):
        OperationSpecification(
            **{
                **spec.__dict__,
                "identity_dependencies": ("target_job", ""),
            }
        )