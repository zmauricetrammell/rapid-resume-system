from __future__ import annotations

from rrs.application.operations.registry import (
    OperationSpecificationRegistry,
    RegistryValidationContext,
)
from rrs.application.operations.v01_specs import (
    INTEGRATE_EVIDENCE_TASK_BINDING_NOTE,
    INTEGRATE_EVIDENCE_TASK_BINDING_RESOLVED,
    V01OperationResources,
    build_v01_operation_specifications,
)
from rrs.domain.artifacts import ResourceRef, SchemaRef
from rrs.domain.enums import (
    ArtifactType,
    LifecyclePhase,
    MutationType,
    OperationType,
    RetrievalRequirement,
)
from rrs.domain.mutations import CollectionTarget, PointerTarget
from rrs.domain.operations import PointerMutationAuthority


def resource(path: str) -> ResourceRef:
    return ResourceRef(
        path=path,
        content_hash=f"sha256:{path}",
        git_commit="test-commit",
    )


def schema(path: str) -> SchemaRef:
    return SchemaRef(
        path=path,
        content_hash=f"sha256:{path}",
        git_commit="test-commit",
    )


def resources() -> V01OperationResources:
    return V01OperationResources(
        researcher_contract=resource("agents/researcher/contract.md"),
        generate_analysis_task=resource(
            "agents/researcher/tasks/generate-analysis.md"
        ),
        request_evidence_task=resource(
            "agents/researcher/tasks/request-evidence.md"
        ),
        interviewer_contract=resource("agents/interviewer/contract.md"),
        investigate_evidence_request_task=resource(
            "agents/interviewer/tasks/investigate-evidence-request.md"
        ),
        integrate_evidence_task=resource(
            "__UNRESOLVED__/approved-integrate-evidence-task-required"
        ),
        writer_contract=resource("agents/writer/contract.md"),
        generate_resume_task=resource("agents/writer/tasks/generate-resume.md"),
        evaluator_contract=resource("agents/evaluator/contract.md"),
        evaluate_resume_task=resource(
            "agents/evaluator/tasks/evaluate-resume.md"
        ),
        jea_schema=schema("schemas/job-experience-analysis.yaml"),
        evidence_request_schema=schema("schemas/evidence-request.yaml"),
        evidence_response_schema=schema("schemas/evidence-response.yaml"),
        jer_schema=schema("schemas/job-experience-record.yaml"),
        wcm_schema=schema("schemas/writer-content-manifest.yaml"),
        resume_evaluation_schema=schema("schemas/resume-evaluation.yaml"),
    )


def validation_context(items: V01OperationResources) -> RegistryValidationContext:
    resource_paths = frozenset(
        {
            items.researcher_contract.path,
            items.generate_analysis_task.path,
            items.request_evidence_task.path,
            items.interviewer_contract.path,
            items.investigate_evidence_request_task.path,
            items.integrate_evidence_task.path,
            items.writer_contract.path,
            items.generate_resume_task.path,
            items.evaluator_contract.path,
            items.evaluate_resume_task.path,
        }
    )
    schema_paths = frozenset(
        {
            items.jea_schema.path,
            items.evidence_request_schema.path,
            items.evidence_response_schema.path,
            items.jer_schema.path,
            items.wcm_schema.path,
            items.resume_evaluation_schema.path,
        }
    )
    dependency_names = frozenset(
        {
            "researcher_contract",
            "generate_analysis_task",
            "jea_schema",
            "retrieval_result_fingerprint",
            "request_evidence_task",
            "evidence_request_schema",
            "interaction_id",
            "last_interviewer_turn_boundary",
            "interviewer_contract",
            "investigate_evidence_request_task",
            "evidence_response_schema",
            "interaction_status",
            "integrate_evidence_task",
            "jer_schema",
            "writer_contract",
            "generate_resume_task",
            "wcm_schema",
            "output_format_identity",
            "evaluator_contract",
            "evaluate_resume_task",
            "resume_evaluation_schema",
        }
    )
    return RegistryValidationContext(
        handler_keys=frozenset(item.value for item in OperationType),
        resource_paths=resource_paths,
        schema_paths=schema_paths,
        professional_roles=frozenset(
            {"researcher", "interviewer", "writer", "evaluator"}
        ),
        reconciliation_keys=frozenset(
            {"reconcile_active_erqs_from_jea"}
        ),
        retry_policy_refs=frozenset(
            {
                "professional_default",
                "professional_evidence_required",
                "professional_interviewer",
                "professional_integration",
                "professional_resume",
                "professional_evaluation",
            }
        ),
        evidence_source_keys=frozenset({"professional_evidence"}),
        dependency_names=dependency_names,
    )


def specs_by_type():
    return {
        item.operation_type: item
        for item in build_v01_operation_specifications(resources())
    }


def test_all_six_v01_specifications_build_and_validate() -> None:
    items = resources()
    specs = build_v01_operation_specifications(items)

    registry = OperationSpecificationRegistry.build(
        specs,
        validation_context(items),
    )

    assert {item.operation_type for item in registry.all()} == set(OperationType)
    assert len(registry.all()) == 6


def test_generate_analysis_matches_planning_contract() -> None:
    spec = specs_by_type()[OperationType.GENERATE_ANALYSIS]

    assert spec.allowed_lifecycle_phases == frozenset({LifecyclePhase.ANALYSIS})
    assert spec.retrieval.requirement is RetrievalRequirement.REQUIRED
    assert spec.output_contract.required_artifact_types == (
        ArtifactType.JOB_EXPERIENCE_ANALYSIS,
    )
    assert spec.pointer_authority == frozenset(
        {
            PointerMutationAuthority(
                PointerTarget.JEA,
                MutationType.SET,
            )
        }
    )


def test_request_evidence_matches_planning_contract() -> None:
    spec = specs_by_type()[OperationType.REQUEST_EVIDENCE]

    assert spec.allowed_lifecycle_phases == frozenset(
        {LifecyclePhase.EVIDENCE_REQUEST}
    )
    assert spec.retrieval.requirement is RetrievalRequirement.NONE
    assert spec.output_contract.required_artifact_types == (
        ArtifactType.EVIDENCE_REQUEST,
    )
    assert spec.pointer_authority == frozenset(
        {
            PointerMutationAuthority(
                CollectionTarget.ACTIVE_ERQS,
                MutationType.ADD,
            ),
            PointerMutationAuthority(
                CollectionTarget.ACTIVE_ERQS,
                MutationType.UPSERT_VERSION,
            ),
        }
    )


def test_investigation_matches_planning_contract() -> None:
    spec = specs_by_type()[OperationType.INVESTIGATE_EVIDENCE_REQUEST]

    assert spec.allowed_lifecycle_phases == frozenset(
        {LifecyclePhase.INVESTIGATION}
    )
    assert spec.retrieval.requirement is RetrievalRequirement.NONE
    assert spec.output_contract.required_artifact_types == (
        ArtifactType.EVIDENCE_RESPONSE,
    )
    assert spec.pointer_authority == frozenset(
        {
            PointerMutationAuthority(
                CollectionTarget.UNINTEGRATED_EVIDENCE_RESPONSES,
                MutationType.ADD,
            )
        }
    )


def test_integrate_evidence_matches_current_safe_default() -> None:
    spec = specs_by_type()[OperationType.INTEGRATE_EVIDENCE]

    assert spec.allowed_lifecycle_phases == frozenset(
        {LifecyclePhase.EVIDENCE_INTEGRATION}
    )
    assert spec.retrieval.requirement is RetrievalRequirement.NONE
    assert spec.output_contract.required_artifact_types == (
        ArtifactType.JOB_EXPERIENCE_RECORD,
    )
    assert spec.pointer_authority == frozenset(
        {
            PointerMutationAuthority(
                CollectionTarget.JER_SET,
                MutationType.UPSERT_VERSION,
            ),
            PointerMutationAuthority(
                CollectionTarget.UNINTEGRATED_EVIDENCE_RESPONSES,
                MutationType.REMOVE,
            ),
        }
    )


def test_generate_resume_declares_coupled_outputs() -> None:
    spec = specs_by_type()[OperationType.GENERATE_RESUME]

    assert spec.allowed_lifecycle_phases == frozenset(
        {LifecyclePhase.RESUME_PRODUCTION}
    )
    assert spec.retrieval.requirement is RetrievalRequirement.NONE
    assert spec.output_contract.required_artifact_types == (
        ArtifactType.TARGETED_RESUME,
        ArtifactType.WRITER_CONTENT_MANIFEST,
    )
    assert spec.output_contract.coupled_groups == (
        (
            ArtifactType.TARGETED_RESUME,
            ArtifactType.WRITER_CONTENT_MANIFEST,
        ),
    )
    assert spec.pointer_authority == frozenset(
        {
            PointerMutationAuthority(
                PointerTarget.RESUME,
                MutationType.SET,
            ),
            PointerMutationAuthority(
                PointerTarget.WCM,
                MutationType.SET,
            ),
        }
    )


def test_evaluate_resume_matches_planning_contract() -> None:
    spec = specs_by_type()[OperationType.EVALUATE_RESUME]

    assert spec.allowed_lifecycle_phases == frozenset(
        {LifecyclePhase.EVALUATION}
    )
    assert spec.retrieval.requirement is RetrievalRequirement.NONE
    assert spec.output_contract.required_artifact_types == (
        ArtifactType.RESUME_EVALUATION,
    )
    assert spec.pointer_authority == frozenset(
        {
            PointerMutationAuthority(
                PointerTarget.EVALUATION,
                MutationType.SET,
            )
        }
    )


def test_integrate_evidence_task_binding_is_explicitly_unresolved() -> None:
    assert INTEGRATE_EVIDENCE_TASK_BINDING_RESOLVED is False
    assert "approved" in INTEGRATE_EVIDENCE_TASK_BINDING_NOTE.lower()
    assert "task" in INTEGRATE_EVIDENCE_TASK_BINDING_NOTE.lower()


def test_integrate_evidence_does_not_gain_direct_erq_removal_authority() -> None:
    spec = specs_by_type()[OperationType.INTEGRATE_EVIDENCE]

    assert PointerMutationAuthority(
        CollectionTarget.ACTIVE_ERQS,
        MutationType.REMOVE,
    ) not in spec.pointer_authority
