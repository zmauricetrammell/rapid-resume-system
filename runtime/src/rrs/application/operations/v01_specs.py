"""Concrete V0.1 Operation Specification definitions."""

from dataclasses import dataclass

from rrs.domain.artifacts import ResourceRef, SchemaRef
from rrs.domain.enums import (
    ArtifactType,
    LifecyclePhase,
    MutationType,
    OperationType,
    RetrievalRequirement,
)
from rrs.domain.mutations import CollectionTarget, PointerTarget
from rrs.domain.operations import (
    OperationSpecification,
    OutputContract,
    PointerMutationAuthority,
    ProfessionalBinding,
    RetrievalSpecification,
)

INTEGRATE_EVIDENCE_TASK_BINDING_RESOLVED = False
INTEGRATE_EVIDENCE_TASK_BINDING_NOTE = (
    "No approved dedicated integrate-evidence professional task was found during "
    "implementation planning. A real approved task ResourceRef must be supplied "
    "before production startup."
)


@dataclass(frozen=True)
class V01OperationResources:
    """Resolved professional resources used to construct the six V0.1 specifications."""

    researcher_contract: ResourceRef
    generate_analysis_task: ResourceRef
    request_evidence_task: ResourceRef
    interviewer_contract: ResourceRef
    investigate_evidence_request_task: ResourceRef
    integrate_evidence_task: ResourceRef
    writer_contract: ResourceRef
    generate_resume_task: ResourceRef
    evaluator_contract: ResourceRef
    evaluate_resume_task: ResourceRef
    jea_schema: SchemaRef
    evidence_request_schema: SchemaRef
    evidence_response_schema: SchemaRef
    jer_schema: SchemaRef
    wcm_schema: SchemaRef
    resume_evaluation_schema: SchemaRef


def _binding(
    role: str,
    contract: ResourceRef,
    task: ResourceRef,
) -> ProfessionalBinding:
    return ProfessionalBinding(
        professional_role=role,
        contract=contract,
        task=task,
    )


def build_v01_operation_specifications(
    resources: V01OperationResources,
) -> tuple[OperationSpecification, ...]:
    """Build all six V0.1 specifications from already-resolved resources."""

    return (
        OperationSpecification(
            operation_type=OperationType.GENERATE_ANALYSIS,
            handler_key="generate_analysis",
            allowed_lifecycle_phases=frozenset({LifecyclePhase.ANALYSIS}),
            professional_binding=_binding(
                "researcher",
                resources.researcher_contract,
                resources.generate_analysis_task,
            ),
            required_inputs=("target_job", "jer_set"),
            optional_inputs=(
                "resume_evaluation",
                "unintegrated_evidence_responses",
            ),
            identity_dependencies=(
                "target_job",
                "jer_set",
                "resume_evaluation",
                "unintegrated_evidence_responses",
                "researcher_contract",
                "generate_analysis_task",
                "jea_schema",
                "retrieval_result_fingerprint",
            ),
            freshness_dependencies=(
                "target_job",
                "jer_set",
                "resume_evaluation",
                "unintegrated_evidence_responses",
            ),
            retrieval=RetrievalSpecification(
                requirement=RetrievalRequirement.REQUIRED,
                evidence_source_key="professional_evidence",
            ),
            output_contract=OutputContract(
                required_artifact_types=(ArtifactType.JOB_EXPERIENCE_ANALYSIS,),
                coupled_groups=(),
                schemas=(resources.jea_schema,),
            ),
            pointer_authority=frozenset(
                {
                    PointerMutationAuthority(
                        PointerTarget.JEA,
                        MutationType.SET,
                    )
                }
            ),
            deterministic_reconciliation=("reconcile_active_erqs_from_jea",),
            retry_policy_ref="professional_evidence_required",
            specification_hash="unfinalized",
        ),
        OperationSpecification(
            operation_type=OperationType.REQUEST_EVIDENCE,
            handler_key="request_evidence",
            allowed_lifecycle_phases=frozenset({LifecyclePhase.EVIDENCE_REQUEST}),
            professional_binding=_binding(
                "researcher",
                resources.researcher_contract,
                resources.request_evidence_task,
            ),
            required_inputs=("job_experience_analysis", "target_job"),
            optional_inputs=("active_erqs",),
            identity_dependencies=(
                "job_experience_analysis",
                "target_job",
                "active_erqs",
                "researcher_contract",
                "request_evidence_task",
                "evidence_request_schema",
            ),
            freshness_dependencies=("job_experience_analysis", "active_erqs"),
            retrieval=RetrievalSpecification(
                requirement=RetrievalRequirement.NONE,
                evidence_source_key=None,
            ),
            output_contract=OutputContract(
                required_artifact_types=(ArtifactType.EVIDENCE_REQUEST,),
                coupled_groups=(),
                schemas=(resources.evidence_request_schema,),
            ),
            pointer_authority=frozenset(
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
            ),
            deterministic_reconciliation=("reconcile_active_erqs_from_jea",),
            retry_policy_ref="professional_default",
            specification_hash="unfinalized",
        ),
        OperationSpecification(
            operation_type=OperationType.INVESTIGATE_EVIDENCE_REQUEST,
            handler_key="investigate_evidence_request",
            allowed_lifecycle_phases=frozenset({LifecyclePhase.INVESTIGATION}),
            professional_binding=_binding(
                "interviewer",
                resources.interviewer_contract,
                resources.investigate_evidence_request_task,
            ),
            required_inputs=(
                "current_evidence_request",
                "interaction_conversation",
                "unprocessed_human_message_batch",
            ),
            optional_inputs=("target_job", "authorized_professional_context"),
            identity_dependencies=(
                "interaction_id",
                "current_evidence_request",
                "last_interviewer_turn_boundary",
                "unprocessed_human_message_batch",
                "interviewer_contract",
                "investigate_evidence_request_task",
                "evidence_response_schema",
            ),
            freshness_dependencies=(
                "current_evidence_request",
                "interaction_status",
                "unprocessed_human_message_batch",
            ),
            retrieval=RetrievalSpecification(
                requirement=RetrievalRequirement.NONE,
                evidence_source_key=None,
            ),
            output_contract=OutputContract(
                required_artifact_types=(ArtifactType.EVIDENCE_RESPONSE,),
                coupled_groups=(),
                schemas=(resources.evidence_response_schema,),
            ),
            pointer_authority=frozenset(
                {
                    PointerMutationAuthority(
                        CollectionTarget.UNINTEGRATED_EVIDENCE_RESPONSES,
                        MutationType.ADD,
                    )
                }
            ),
            deterministic_reconciliation=(),
            retry_policy_ref="professional_interviewer",
            specification_hash="unfinalized",
        ),
        OperationSpecification(
            operation_type=OperationType.INTEGRATE_EVIDENCE,
            handler_key="integrate_evidence",
            allowed_lifecycle_phases=frozenset({LifecyclePhase.EVIDENCE_INTEGRATION}),
            professional_binding=_binding(
                "researcher",
                resources.researcher_contract,
                resources.integrate_evidence_task,
            ),
            required_inputs=("jer_set", "unintegrated_evidence_responses"),
            optional_inputs=(
                "job_experience_analysis",
                "target_job",
                "active_erqs",
            ),
            identity_dependencies=(
                "jer_set",
                "unintegrated_evidence_responses",
                "job_experience_analysis",
                "researcher_contract",
                "integrate_evidence_task",
                "jer_schema",
            ),
            freshness_dependencies=(
                "jer_set",
                "unintegrated_evidence_responses",
                "job_experience_analysis",
            ),
            retrieval=RetrievalSpecification(
                requirement=RetrievalRequirement.NONE,
                evidence_source_key=None,
            ),
            output_contract=OutputContract(
                required_artifact_types=(ArtifactType.JOB_EXPERIENCE_RECORD,),
                coupled_groups=(),
                schemas=(resources.jer_schema,),
            ),
            pointer_authority=frozenset(
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
            ),
            deterministic_reconciliation=(),
            retry_policy_ref="professional_integration",
            specification_hash="unfinalized",
        ),
        OperationSpecification(
            operation_type=OperationType.GENERATE_RESUME,
            handler_key="generate_resume",
            allowed_lifecycle_phases=frozenset({LifecyclePhase.RESUME_PRODUCTION}),
            professional_binding=_binding(
                "writer",
                resources.writer_contract,
                resources.generate_resume_task,
            ),
            required_inputs=(
                "target_job",
                "job_experience_analysis",
                "jer_set",
                "resume_skeleton",
                "prompt_bank",
            ),
            optional_inputs=(
                "resume_evaluation",
                "resume",
                "authorized_presentation_resources",
            ),
            identity_dependencies=(
                "target_job",
                "job_experience_analysis",
                "jer_set",
                "resume_skeleton",
                "prompt_bank",
                "resume_evaluation",
                "writer_contract",
                "generate_resume_task",
                "wcm_schema",
                "output_format_identity",
            ),
            freshness_dependencies=(
                "target_job",
                "job_experience_analysis",
                "jer_set",
                "resume_evaluation",
            ),
            retrieval=RetrievalSpecification(
                requirement=RetrievalRequirement.NONE,
                evidence_source_key=None,
            ),
            output_contract=OutputContract(
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
                schemas=(resources.wcm_schema,),
            ),
            pointer_authority=frozenset(
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
            ),
            deterministic_reconciliation=(),
            retry_policy_ref="professional_resume",
            specification_hash="unfinalized",
        ),
        OperationSpecification(
            operation_type=OperationType.EVALUATE_RESUME,
            handler_key="evaluate_resume",
            allowed_lifecycle_phases=frozenset({LifecyclePhase.EVALUATION}),
            professional_binding=_binding(
                "evaluator",
                resources.evaluator_contract,
                resources.evaluate_resume_task,
            ),
            required_inputs=(
                "target_job",
                "resume",
                "wcm",
                "job_experience_analysis",
            ),
            optional_inputs=("jer_set", "supporting_evidence"),
            identity_dependencies=(
                "target_job",
                "resume",
                "wcm",
                "job_experience_analysis",
                "jer_set",
                "supporting_evidence",
                "evaluator_contract",
                "evaluate_resume_task",
                "resume_evaluation_schema",
            ),
            freshness_dependencies=(
                "target_job",
                "resume",
                "wcm",
                "job_experience_analysis",
            ),
            retrieval=RetrievalSpecification(
                requirement=RetrievalRequirement.NONE,
                evidence_source_key=None,
            ),
            output_contract=OutputContract(
                required_artifact_types=(ArtifactType.RESUME_EVALUATION,),
                coupled_groups=(),
                schemas=(resources.resume_evaluation_schema,),
            ),
            pointer_authority=frozenset(
                {
                    PointerMutationAuthority(
                        PointerTarget.EVALUATION,
                        MutationType.SET,
                    )
                }
            ),
            deterministic_reconciliation=(),
            retry_policy_ref="professional_evaluation",
            specification_hash="unfinalized",
        ),
    )


__all__ = [
    "INTEGRATE_EVIDENCE_TASK_BINDING_NOTE",
    "INTEGRATE_EVIDENCE_TASK_BINDING_RESOLVED",
    "V01OperationResources",
    "build_v01_operation_specifications",
]
