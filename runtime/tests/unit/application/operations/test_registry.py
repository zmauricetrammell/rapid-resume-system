from __future__ import annotations

from dataclasses import replace

import pytest

from rrs.application.operations.registry import (
    OperationRegistryHasher,
    OperationRegistryValidationError,
    OperationSpecificationHasher,
    OperationSpecificationRegistry,
    RegistryValidationContext,
    RegistryValidator,
)
from rrs.domain.artifacts import ResourceRef, SchemaRef
from rrs.domain.enums import (
    ArtifactType,
    LifecyclePhase,
    MutationType,
    OperationType,
    RetrievalRequirement,
)
from rrs.domain.mutations import PointerTarget
from rrs.domain.operations import (
    OperationSpecification,
    OutputContract,
    PointerMutationAuthority,
    ProfessionalBinding,
    RetrievalSpecification,
)


def spec(
    *,
    operation_type: OperationType = OperationType.GENERATE_ANALYSIS,
    git_commit: str = "commit-a",
) -> OperationSpecification:
    return OperationSpecification(
        operation_type=operation_type,
        handler_key=operation_type.value,
        allowed_lifecycle_phases=frozenset({LifecyclePhase.ANALYSIS}),
        professional_binding=ProfessionalBinding(
            professional_role="researcher",
            contract=ResourceRef("agents/researcher/contract.md", "hash:contract", git_commit),
            task=ResourceRef(
                "agents/researcher/tasks/generate-analysis.md", 
                "hash:task", 
                git_commit
            ),
        ),
        required_inputs=("target_job", "jer_set"),
        optional_inputs=(),
        identity_dependencies=("target_job", "jer_set", "professional_binding", "output_contract"),
        freshness_dependencies=("target_job", "jer_set"),
        retrieval=RetrievalSpecification(RetrievalRequirement.REQUIRED, "professional_evidence"),
        output_contract=OutputContract(
            required_artifact_types=(ArtifactType.JOB_EXPERIENCE_ANALYSIS,),
            coupled_groups=(),
            schemas=(SchemaRef("schemas/job-experience-analysis.yaml", "hash:schema", git_commit),),
        ),
        pointer_authority=frozenset(
            {PointerMutationAuthority(PointerTarget.JEA, MutationType.SET)}
        ),
        deterministic_reconciliation=("reconcile_active_erqs_from_jea",),
        retry_policy_ref="professional_evidence_required",
        specification_hash="unfinalized",
    )


def context() -> RegistryValidationContext:
    return RegistryValidationContext(
        handler_keys=frozenset(x.value for x in OperationType),
        resource_paths=frozenset(
            {
                "agents/researcher/contract.md",
                "agents/researcher/tasks/generate-analysis.md",
            }
        ),
        schema_paths=frozenset({"schemas/job-experience-analysis.yaml"}),
        professional_roles=frozenset({"researcher"}),
        reconciliation_keys=frozenset({"reconcile_active_erqs_from_jea"}),
        retry_policy_refs=frozenset({"professional_evidence_required"}),
        evidence_source_keys=frozenset({"professional_evidence"}),
        dependency_names=frozenset({"professional_binding", "output_contract"}),
    )


def test_registry_build_validates_finalizes_and_orders() -> None:
    second = replace(
        spec(operation_type=OperationType.EVALUATE_RESUME), 
        handler_key="evaluate_resume"
    )
    registry = OperationSpecificationRegistry.build((second, spec()), context())

    assert [x.operation_type for x in registry.all()] == [
        OperationType.EVALUATE_RESUME,
        OperationType.GENERATE_ANALYSIS,
    ]
    assert registry.get(OperationType.GENERATE_ANALYSIS).specification_hash != "unfinalized"
    assert len(registry.registry_hash) == 64


def test_registry_rejects_empty_and_duplicate_operation_types() -> None:
    with pytest.raises(OperationRegistryValidationError, match="must not be empty"):
        RegistryValidator.validate((), context())

    duplicate = spec()
    with pytest.raises(OperationRegistryValidationError, match="duplicate operation_type"):
        RegistryValidator.validate((duplicate, duplicate), context())


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"handler_key": "missing"}, "missing handler"),
        (
            {
                "professional_binding": ProfessionalBinding(
                    "researcher",
                    ResourceRef("missing-contract", "h"),
                    ResourceRef(
                        "agents/researcher/tasks/generate-analysis.md",
                        "h",
                    ),
                )
            },
            "missing contract resource",
        ),
        (
            {
                "professional_binding": ProfessionalBinding(
                    "researcher",
                    ResourceRef(
                        "agents/researcher/contract.md",
                        "h",
                    ),
                    ResourceRef("missing-task", "h"),
                )
            },
            "missing task resource",
        ),
        (
            {
                "professional_binding": ProfessionalBinding(
                    "unknown-role",
                    ResourceRef(
                        "agents/researcher/contract.md",
                        "h",
                    ),
                    ResourceRef(
                        "agents/researcher/tasks/generate-analysis.md",
                        "h",
                    ),
                )
            },
            "unknown professional role",
        ),
        (
            {
                "output_contract": OutputContract(
                    (ArtifactType.JOB_EXPERIENCE_ANALYSIS,),
                    (),
                    (SchemaRef("missing-schema", "h"),),
                )
            },
            "missing schema resource",
        ),
        (
            {"deterministic_reconciliation": ("missing-hook",)},
            "unknown deterministic reconciliation",
        ),
        (
            {"retry_policy_ref": "missing-policy"},
            "unknown retry policy",
        ),
        (
            {
                "retrieval": RetrievalSpecification(
                    RetrievalRequirement.REQUIRED,
                    "missing-source",
                )
            },
            "unresolved evidence source",
        ),
        (
            {"identity_dependencies": ("unknown-dependency",)},
            "invalid identity dependency",
        ),
        (
            {"freshness_dependencies": ("unknown-dependency",)},
            "invalid freshness dependency",
        ),
    ],
)

def test_registry_reference_and_semantic_validation(
    change: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(OperationRegistryValidationError, match=message):
        RegistryValidator.validate((replace(spec(), **change),), context())


def test_specification_hash_ignores_git_only_provenance() -> None:
    assert OperationSpecificationHasher.hash(spec(git_commit="commit-a")) == (
        OperationSpecificationHasher.hash(spec(git_commit="commit-b"))
    )


def test_specification_hash_changes_with_semantic_content() -> None:
    original = spec()
    changed = replace(original, handler_key="evaluate_resume")
    assert OperationSpecificationHasher.hash(original) != OperationSpecificationHasher.hash(changed)


def test_registry_hash_is_order_independent_and_semantic() -> None:
    first = OperationSpecificationHasher.finalize(spec())
    second = OperationSpecificationHasher.finalize(
        replace(spec(operation_type=OperationType.EVALUATE_RESUME), handler_key="evaluate_resume")
    )
    assert OperationRegistryHasher.hash(
        (first, second)
        ) == OperationRegistryHasher.hash(
        (second, first)
    )


def test_registry_get_unknown_operation_raises() -> None:
    registry = OperationSpecificationRegistry.build((spec(),), context())
    with pytest.raises(KeyError, match="unknown operation_type"):
        registry.get(OperationType.EVALUATE_RESUME)


def test_registry_constructor_rejects_duplicates() -> None:
    item = OperationSpecificationHasher.finalize(spec())
    with pytest.raises(OperationRegistryValidationError, match="duplicate operation_type"):
        OperationSpecificationRegistry((item, item))

def test_registry_constructor_rejects_empty_registry() -> None:
    with pytest.raises(
        OperationRegistryValidationError,
        match="must not be empty",
    ):
        OperationSpecificationRegistry(())


def test_registry_constructor_rejects_unfinalized_specification_hash() -> None:
    with pytest.raises(
        OperationRegistryValidationError,
        match="finalized specification hashes",
    ):
        OperationSpecificationRegistry((spec(),))