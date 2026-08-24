# RRS V3 Python Domain Model

## Status

Implementation Planning — Phase 2

## Purpose

This document translates the frozen RRS V3 architecture into concrete Python-facing domain contracts.

It defines:

- canonical ID types,
- enums,
- immutable value objects,
- domain aggregates,
- mutation contracts,
- operation/result types,
- repository and service protocols,
- error/failure types,
- ownership and dependency boundaries.

It does **not** define production service implementations, SQLite table layouts, migration syntax, provider SDK code, or final package structure.

Those belong to later implementation-planning artifacts.

The design goal is:

```text
architecture vocabulary
→ one canonical Python vocabulary
→ repositories/services implement against it
→ tests assert the same invariants
```

---

# 1. Python Baseline

Recommended implementation baseline:

```text
Python 3.12+
```

Domain types should prefer:

```text
dataclasses
Enum / StrEnum
typing.Protocol
typing.NewType or lightweight frozen ID wrappers
datetime with timezone-aware UTC values
tuple / frozenset for immutable collections
```

The domain layer should avoid depending directly on:

```text
SQLite
Discord SDKs
Google Drive SDKs
OpenAI/provider SDKs
CLI frameworks
Docker/runtime environment
```

Infrastructure dependencies belong behind protocols.

---

# 2. Domain Design Rules

1. Domain aggregates and value objects are immutable after construction unless the type explicitly represents mutable persistence state.
2. Runtime mutations create new authoritative state rather than mutating shared aggregate instances in place.
3. IDs are strongly typed enough that a `JobId` cannot be accidentally passed where an `ExecutionId` is expected.
4. All persisted enum values have one canonical string representation.
5. `RuntimeJob` contains references to professional artifacts, not artifact bodies.
6. `Execution` contains immutable input identity/freshness snapshots once invocation begins.
7. Professional output remains nonauthoritative until Commit Coordinator success.
8. Provider-specific types never cross domain interfaces.
9. Domain types never depend on raw SQLite rows.
10. Architecture authority remains reflected in Python interfaces:
    - Operation Specification declares authority.
    - Handler coordinates.
    - Commit Coordinator commits professional state.
    - Router mutates lifecycle/routing state.
    - repositories enforce persistence/CAS.
11. UTC-aware `datetime` values are used internally.
12. Collection ordering is deterministic where identity, hashing, replay, or provenance depends on order.

---

# 3. Strongly Typed IDs

Recommended conceptual approach:

```python
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
```

A later implementation may choose frozen wrapper classes instead of `NewType` when runtime validation is useful.

Required behavior:

```text
IDs are opaque
IDs are immutable
IDs are serializable to canonical strings
IDs are never reused for another logical object
```

---

# 4. Artifact Version

```python
@dataclass(frozen=True, order=True)
class ArtifactVersion:
    value: int
```

Invariant:

```text
value >= 1
```

`ArtifactVersion` is distinct from Runtime Job revision.

```text
ArtifactVersion
= immutable professional artifact version

RuntimeJob.revision
= control-plane aggregate CAS version
```

---

# 5. Canonical Enums

## LifecyclePhase

```python
class LifecyclePhase(StrEnum):
    NEW = "new"
    ANALYSIS = "analysis"
    EVIDENCE_REQUEST = "evidence_request"
    INVESTIGATION = "investigation"
    EVIDENCE_INTEGRATION = "evidence_integration"
    RESUME_PRODUCTION = "resume_production"
    EVALUATION = "evaluation"
    COMPLETE = "complete"
    MANUAL_REVIEW = "manual_review"
    CANCELLED = "cancelled"
```

Terminal:

```text
complete
cancelled
```

`manual_review` is nonterminal automation suspension unless future policy explicitly changes that behavior.

---

## OperationType

```python
class OperationType(StrEnum):
    GENERATE_ANALYSIS = "generate_analysis"
    REQUEST_EVIDENCE = "request_evidence"
    INVESTIGATE_EVIDENCE_REQUEST = "investigate_evidence_request"
    INTEGRATE_EVIDENCE = "integrate_evidence"
    GENERATE_RESUME = "generate_resume"
    EVALUATE_RESUME = "evaluate_resume"
```

This is the current V2-compatible professional operation set.

Future Analyst/Custodian operations require explicit architecture/specification additions.

---

## RuntimeOperationStatus

```python
class RuntimeOperationStatus(StrEnum):
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    VALIDATING = "validating"
    COMMITTING = "committing"
```

This is the **Runtime Job projection** of current professional execution.

It is intentionally smaller than `ExecutionStatus`.

---

## ExecutionStatus

```python
class ExecutionStatus(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    OUTPUT_RECEIVED = "output_received"
    VALIDATING = "validating"
    VALIDATED = "validated"
    STALE = "stale"
    COMMITTING = "committing"
    COMMITTED = "committed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

Terminal:

```text
stale
committed
failed
cancelled
```

---

## InteractionProjectionStatus

```python
class InteractionProjectionStatus(StrEnum):
    NONE = "none"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
```

This belongs to `RuntimeJob.interaction`.

---

## InteractionStatus

```python
class InteractionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

This belongs to the authoritative `Interaction` record.

---

## InteractionType

```python
class InteractionType(StrEnum):
    EVIDENCE_INVESTIGATION = "evidence_investigation"
    MANUAL_REVIEW = "manual_review"
```

---

## HealthStatus

```python
class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RECOVERABLE_FAILURE = "recoverable_failure"
    BLOCKED = "blocked"
```

---

## MutationType

```python
class MutationType(StrEnum):
    SET = "set"
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
    UPSERT_VERSION = "upsert_version"
```

Persistence may store uppercase or lowercase strings, but one canonical representation must be selected before migrations are finalized.

Recommendation:

```text
lowercase persisted values
```

---

## RetrievalRequirement

```python
class RetrievalRequirement(StrEnum):
    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"
```

---

## ArtifactRuntimeStatus

```python
class ArtifactRuntimeStatus(StrEnum):
    COMMITTED = "committed"
    STALE_OUTPUT = "stale_output"
    ORPHANED_OUTPUT = "orphaned_output"
    DIAGNOSTIC = "diagnostic"
```

There is intentionally no:

```text
superseded
```

Currentness is derived from Runtime Job pointers.

---

## EventStatus

```python
class EventStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    IGNORED = "ignored"
    RETRY_PENDING = "retry_pending"
    DEAD_LETTER = "dead_letter"
```

---

## EventCriticality

```python
class EventCriticality(StrEnum):
    WORKFLOW_CRITICAL = "workflow_critical"
    INTEGRATION_ONLY = "integration_only"
```

---

## CommandStatus

The architecture requires a durable processing lifecycle but does not freeze one exact enum as strongly as Event status.

Recommended V0.1:

```python
class CommandStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    RETRY_PENDING = "retry_pending"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

This is an implementation-planning decision and must be confirmed by the SQLite Schema model.

---

## FailureClass

The exact final enum should be centralized.

Minimum known values include:

```python
class FailureClass(StrEnum):
    EVIDENCE_SOURCE_UNAVAILABLE = "evidence_source_unavailable"
    INVOCATION_FAILURE = "invocation_failure"
    SCHEMA_VALIDATION_FAILURE = "schema_validation_failure"
    STALE_OUTPUT = "stale_output"
    PERSISTENCE_FAILURE = "persistence_failure"
    STORAGE_CONFLICT = "storage_conflict"
    CONCURRENCY_CONFLICT = "concurrency_conflict"
    INTERACTION_FAILURE = "interaction_failure"
    PROVIDER_RECONCILIATION_FAILURE = "provider_reconciliation_failure"
    RUNTIME_INTEGRITY_FAILURE = "runtime_integrity_failure"
```

The SQLite planning phase must reconcile this list against every architecture-model failure reference.

---

# 6. ArtifactType

Recommended V0.1 domain enum:

```python
class ArtifactType(StrEnum):
    TARGET_JOB = "target_job"
    JOB_EXPERIENCE_RECORD = "job_experience_record"
    JOB_EXPERIENCE_ANALYSIS = "job_experience_analysis"
    EVIDENCE_REQUEST = "evidence_request"
    EVIDENCE_RESPONSE = "evidence_response"
    TARGETED_RESUME = "targeted_resume"
    WRITER_CONTENT_MANIFEST = "writer_content_manifest"
    RESUME_EVALUATION = "resume_evaluation"
    PROCESS_FEEDBACK = "process_feedback"
```

`Process Feedback` remains outside `RuntimeJob.professional_state`.

Future/deferred:

```text
information_request
information_response
target_role
```

Do not add those to V0.1 Runtime Job state merely because the domain enum could support them later.

---

# 7. ArtifactRef

```python
@dataclass(frozen=True)
class ArtifactRef:
    artifact_type: ArtifactType
    artifact_id: ArtifactId
    artifact_version: ArtifactVersion
    uri: str
```

Invariants:

```text
artifact_id is nonempty
artifact_version >= 1
uri identifies immutable stored content
```

ArtifactRef does not include professional artifact body content.

Equality should represent exact reference equality:

```text
type + id + version + uri
```

For dependency identity, the architecture may rely primarily on:

```text
artifact_type + artifact_id + artifact_version
```

with content hash verified through metadata when necessary.

---

# 8. ResourceRef and SchemaRef

```python
@dataclass(frozen=True)
class ResourceRef:
    path: str
    content_hash: str
    git_commit: str | None = None
```

```python
@dataclass(frozen=True)
class SchemaRef:
    path: str
    content_hash: str
    git_commit: str | None = None
```

Rules:

- `content_hash` carries semantic content identity.
- `git_commit` is provenance.
- Git commit alone must not determine semantic operation identity.
- Exact schema supplied to the provider must equal the schema used for runtime validation.

---

# 9. RuntimeJob Aggregate

```python
@dataclass(frozen=True)
class RuntimeJob:
    identity: RuntimeJobIdentity
    lifecycle: LifecycleState
    operation: OperationState
    interaction: InteractionProjection
    health: HealthState
    professional_state: ProfessionalState
    routing_history: tuple[RoutingDecision, ...]
```

This is the canonical in-memory aggregate returned by `RuntimeJobRepository`.

It must remain persistence-independent.

---

# 10. RuntimeJobIdentity

```python
@dataclass(frozen=True)
class RuntimeJobIdentity:
    job_id: JobId
    revision: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
```

Invariants:

```text
revision >= 1
created_at <= updated_at
complete lifecycle → completed_at is not null
non-complete lifecycle → completed_at normally null
```

Repository mutation owns revision changes.

No caller manually increments revision.

---

# 11. LifecycleState

```python
@dataclass(frozen=True)
class LifecycleState:
    phase: LifecyclePhase
    entered_at: datetime
```

Lifecycle transition authority belongs to the Router/deterministic runtime control plane.

Professional agents cannot construct authoritative lifecycle transitions.

---

# 12. OperationState

```python
@dataclass(frozen=True)
class OperationState:
    status: RuntimeOperationStatus
    operation_type: OperationType | None
    execution_id: ExecutionId | None
    started_at: datetime | None
```

Invariants:

```text
status == idle
→ operation_type is None
→ execution_id is None
→ started_at is None
```

For non-idle active professional operation states:

```text
operation_type is not None
execution_id is normally not None once Execution exists
```

The SQLite Schema planning phase should define exact transitional constraints for `queued`.

---

# 13. InteractionProjection

```python
@dataclass(frozen=True)
class InteractionProjection:
    status: InteractionProjectionStatus
    interaction_type: InteractionType | None
    interaction_id: InteractionId | None
    started_at: datetime | None
    last_activity_at: datetime | None
```

Rules:

```text
status == none
→ interaction_type = None
→ interaction_id = None
→ started_at = None
→ last_activity_at = None
```

```text
status in [pending, active, paused]
→ interaction_id exists
```

The projection is not authoritative detailed Interaction state.

It is synchronized from the authoritative Interaction record.

---

# 14. HealthState

```python
@dataclass(frozen=True)
class HealthState:
    status: HealthStatus
    failure_id: FailureId | None
    retry_count: int
```

Invariants:

```text
retry_count >= 0

status == healthy
→ failure_id is None
```

Nonhealthy state may reference the current material unresolved Failure.

Full failure history does not live in RuntimeJob.

---

# 15. ProfessionalState

```python
@dataclass(frozen=True)
class ProfessionalState:
    target_job: ArtifactRef
    jer_set: tuple[ArtifactRef, ...]
    jea: ArtifactRef | None
    active_erqs: tuple[ArtifactRef, ...]
    unintegrated_evidence_responses: tuple[ArtifactRef, ...]
    resume: ArtifactRef | None
    wcm: ArtifactRef | None
    evaluation: ArtifactRef | None
```

Collection invariants:

```text
deterministic ordering
no duplicate exact refs
target_job required
jer_set pinned to exact versions
```

Recommended deterministic ordering:

```text
jer_set
→ artifact_id ASC, artifact_version ASC

active_erqs
→ artifact_id ASC, artifact_version ASC

unintegrated_evidence_responses
→ artifact_id ASC, artifact_version ASC
```

The runtime should not rely on incidental database row order.

---

# 16. RoutingDecision

```python
@dataclass(frozen=True)
class RoutingPredicateResult:
    name: str
    result: bool
```

```python
@dataclass(frozen=True)
class RoutingDecision:
    decision_id: RoutingDecisionId
    decided_at: datetime
    from_phase: LifecyclePhase
    to_phase: LifecyclePhase
    predicate: RoutingPredicateResult
    basis: tuple[ArtifactRef, ...]
    reason: str
    execution_id: ExecutionId | None
```

Routing history is append-only.

A `RoutingDecision` becomes authoritative only as part of the Router's atomic lifecycle mutation.

---

# 17. Runtime Job Mutation Types

Do not expose a generic:

```python
dict[str, Any]
```

mutation API.

Use typed semantic mutations.

Conceptual union:

```python
RuntimeJobMutation = (
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
```

Example:

```python
@dataclass(frozen=True)
class SetPointerMutation:
    pointer: ProfessionalPointer
    value: ArtifactRef | None
```

```python
@dataclass(frozen=True)
class CollectionAddMutation:
    collection: ProfessionalCollection
    value: ArtifactRef
```

```python
@dataclass(frozen=True)
class CollectionRemoveMutation:
    collection: ProfessionalCollection
    value: ArtifactRef
```

```python
@dataclass(frozen=True)
class CollectionUpsertVersionMutation:
    collection: ProfessionalCollection
    value: ArtifactRef
```

This prevents stale full-collection overwrite behavior.

---

# 18. Professional Pointer and Collection Enums

Recommended:

```python
class ProfessionalPointer(StrEnum):
    TARGET_JOB = "target_job"
    JEA = "jea"
    RESUME = "resume"
    WCM = "wcm"
    EVALUATION = "evaluation"
```

```python
class ProfessionalCollection(StrEnum):
    JER_SET = "jer_set"
    ACTIVE_ERQS = "active_erqs"
    UNINTEGRATED_EVIDENCE_RESPONSES = "unintegrated_evidence_responses"
```

These names become the basis for Operation Specification pointer authority.

---

# 19. Execution

```python
@dataclass(frozen=True)
class Execution:
    execution_id: ExecutionId
    job_id: JobId
    owner_runtime_instance_id: RuntimeInstanceId
    operation_type: OperationType
    operation_key: OperationKey
    attempt_number: int
    status: ExecutionStatus
    input_snapshot: InputSnapshot
    staged_outputs: tuple[StagedOutputRef, ...]
    committed_outputs: tuple[ArtifactRef, ...]
    failure_id: FailureId | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
```

Invariant:

```text
attempt_number >= 1
```

One active nonterminal Execution per:

```text
operation_key
```

is a persistence constraint.

Execution history is preserved.

---

# 20. InputSnapshot

```python
@dataclass(frozen=True)
class InputSnapshot:
    identity_dependencies: tuple[DependencyFingerprint, ...]
    freshness_dependencies: tuple[DependencyFingerprint, ...]
```

```python
@dataclass(frozen=True)
class DependencyFingerprint:
    dependency_type: str
    logical_name: str
    identity: str
```

Exact representation will be refined when Operation Specifications are concretized.

The key requirement is separation:

```text
identity dependency
→ changes logical operation_key

freshness dependency
→ determines whether staged output may still commit
```

---

# 21. Operation Specification

```python
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
```

The effective object is immutable once resolved.

---

# 22. ProfessionalBinding

```python
@dataclass(frozen=True)
class ProfessionalBinding:
    professional_role: str
    contract: ResourceRef
    task: ResourceRef
```

Current roles may use a domain enum later:

```text
researcher
interviewer
writer
evaluator
```

Recommendation: do **not** make role names part of core orchestration enums unless needed. The runtime is operation-centric and the binding is configuration.

---

# 23. RetrievalSpecification

```python
@dataclass(frozen=True)
class RetrievalSpecification:
    requirement: RetrievalRequirement
    evidence_source_key: str | None
```

Invariant:

```text
requirement == none
→ evidence_source_key is normally None
```

Startup validation owns provider/config resolution.

---

# 24. OutputContract

```python
@dataclass(frozen=True)
class OutputContract:
    required_artifact_types: tuple[ArtifactType, ...]
    coupled_groups: tuple[tuple[ArtifactType, ...], ...]
    schemas: tuple[SchemaRef, ...]
```

Coupled group rule:

```text
all members validate
or
none commit as current
```

For `generate_resume`:

```text
targeted_resume + writer_content_manifest
```

form one semantic coupled group.

---

# 25. PointerMutationAuthority

```python
@dataclass(frozen=True)
class PointerMutationAuthority:
    target: str
    mutation_type: MutationType
```

The target is eventually constrained to canonical pointer/collection enums.

Example:

```python
PointerMutationAuthority(
    target="resume",
    mutation_type=MutationType.SET,
)
```

Handlers may request only declared mutations.

Commit Coordinator enforces them.

---

# 26. Command

```python
@dataclass(frozen=True)
class Command:
    command_id: CommandId
    command_type: str
    job_id: JobId | None
    payload: Mapping[str, object]
    status: CommandStatus
    dedupe_key: str | None
    causation_event_id: EventId | None
    owner_runtime_instance_id: RuntimeInstanceId | None
    lease_expires_at: datetime | None
    attempt_count: int
    created_at: datetime
    completed_at: datetime | None
```

Command bodies should become typed per-command payload objects rather than remain generic mappings in production code.

Recommended typed command variants:

```text
CreateJobCommand
ScheduleOperationCommand
EvaluateRoutingCommand
OpenInteractionCommand
CompleteInteractionCommand
RetryExecutionCommand
EnterManualReviewCommand
CancelJobCommand
```

The generic envelope may contain a tagged payload union.

---

# 27. Event

```python
@dataclass(frozen=True)
class Event:
    event_id: EventId
    event_type: str
    job_id: JobId | None
    payload: EventPayload
    source: EventSource
    correlation_id: str | None
    causation_id: EventId | CommandId | ExecutionId | None
    criticality: EventCriticality
    status: EventStatus
    attempt_count: int
    owner_runtime_instance_id: RuntimeInstanceId | None
    lease_expires_at: datetime | None
    created_at: datetime
    processed_at: datetime | None
```

The event body is logically immutable.

Processing state is mutable persistence metadata.

As with Commands, event payloads should become typed tagged unions during implementation.

---

# 28. EventSource

```python
@dataclass(frozen=True)
class EventSource:
    category: str
    provider: str
    provider_event_id: str | None
```

Provider-specific raw payload does not belong here.

---

# 29. ArtifactMetadata

```python
@dataclass(frozen=True)
class ArtifactMetadata:
    artifact_id: ArtifactId
    artifact_version: ArtifactVersion
    artifact_type: ArtifactType
    storage_uri: str
    content_hash: str
    committed_by_execution_id: ExecutionId | None
    operation_key: OperationKey | None
    committed_at: datetime | None
    runtime_status: ArtifactRuntimeStatus
```

Target Job creation may not be associated with a professional Execution, hence the nullable execution reference.

---

# 30. Commit Group

```python
@dataclass(frozen=True)
class ArtifactCommitGroup:
    commit_group_id: CommitGroupId
    execution_id: ExecutionId
    artifacts: tuple[ArtifactRef, ...]
    committed_at: datetime | None
```

The SQLite design phase should determine whether commit-group status needs an enum or can be inferred from timestamps/Execution state.

---

# 31. Staged Artifact

```python
@dataclass(frozen=True)
class StagedArtifact:
    artifact_type: ArtifactType
    execution_id: ExecutionId
    staged_path: str
    content_hash: str
    media_type: str
```

Staged output is never a current professional artifact reference.

---

# 32. Professional Invocation Types

```python
@dataclass(frozen=True)
class InvocationBundle:
    invocation_id: InvocationId
    job_id: JobId
    execution_id: ExecutionId
    operation_type: OperationType
    professional_binding: ProfessionalBinding
    artifact_refs: tuple[ArtifactRef, ...]
    retrieval_results: tuple[EvidenceSearchResult, ...]
    resource_refs: tuple[ResourceRef, ...]
    output_contract: OutputContract
    input_snapshot: InputSnapshot
    created_at: datetime
```

The bundle is immutable once invocation starts.

---

# 33. RawProfessionalResponse

```python
@dataclass(frozen=True)
class RawProfessionalResponse:
    provider: str
    provider_request_id: str | None
    text: str | None
    structured_data: object | None
    attachments: tuple[ProviderAttachment, ...]
    metadata: Mapping[str, object]
```

This is provider-neutral transport output.

It is not authoritative professional state.

---

# 34. Interviewer Continuation Result

Use an explicit tagged union.

```python
@dataclass(frozen=True)
class ConversationTurn:
    kind: Literal["conversation_turn"]
    content: str
    message_type: str
```

```python
@dataclass(frozen=True)
class CompletedProfessionalArtifact:
    kind: Literal["completed_professional_artifact"]
    artifact_type: ArtifactType
    content: object
    schema_version: str
```

```python
InterviewerContinuationResult = (
    ConversationTurn | CompletedProfessionalArtifact
)
```

V0.1 invariant:

```text
CompletedProfessionalArtifact.artifact_type
== evidence_response
```

---

# 35. Evidence Retrieval Types

## EvidenceQuery

```python
@dataclass(frozen=True)
class EvidenceQuery:
    query_id: str
    purpose: str
    search_text: str
    requested_evidence_types: tuple[str, ...]
    filters: Mapping[str, object]
    max_results: int
```

## RetrievedEvidenceItem

```python
@dataclass(frozen=True)
class RetrievedEvidenceItem:
    item_id: str
    source_ref: EvidenceSourceRef
    title: str
    media_type: str
    excerpt: str
    normalized_text_hash: str
    metadata: Mapping[str, object]
```

## EvidenceSearchResult

```python
@dataclass(frozen=True)
class EvidenceSearchResult:
    query_id: str
    items: tuple[RetrievedEvidenceItem, ...]
    executed_at: datetime
    source_adapter: str
    result_fingerprint: str
```

A successful empty result is:

```python
items=()
```

Evidence provider failure is **not** an empty successful result.

It raises/maps to runtime failure.

---

# 36. Interaction

```python
@dataclass(frozen=True)
class Interaction:
    interaction_id: InteractionId
    job_id: JobId
    interaction_type: InteractionType
    provider: str
    provider_context: ProviderInteractionContext
    professional_context: InteractionProfessionalContext
    status: InteractionStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
```

Provider-specific IDs remain inside provider context, not RuntimeJob.

---

# 37. InteractionMessage

```python
@dataclass(frozen=True)
class InteractionMessage:
    message_id: MessageId
    interaction_id: InteractionId
    provider: str
    provider_message_id: str | None
    provider_created_at: datetime | None
    direction: str
    message_type: str
    content: str | None
    content_ref: str | None
    persisted_at: datetime
    processed_at: datetime | None
    processed_by_continuation_id: InvocationId | None
```

Ordering for inbound Discord human messages:

```text
provider_created_at ASC
provider_message_id ASC
```

not `persisted_at`.

---

# 38. Failure

```python
@dataclass(frozen=True)
class Failure:
    failure_id: FailureId
    job_id: JobId
    execution_id: ExecutionId | None
    event_id: EventId | None
    command_id: CommandId | None
    interaction_id: InteractionId | None
    failure_class: FailureClass
    message: str
    details_ref: str | None
    created_at: datetime
    resolved_at: datetime | None
    resolution_message: str | None
```

Failure records are persistent history.

Resolving a Failure does not delete it.

---

# 39. RuntimeBuildIdentity

```python
@dataclass(frozen=True)
class RuntimeBuildIdentity:
    git_sha: str
    image_digest: str | None
    operation_registry_hash: str
    built_at: datetime | None
```

Important:

```text
git_sha
= provenance

operation_specification_hash
= semantic specification identity
```

These are not interchangeable.

---

# 40. RuntimeInstance

```python
@dataclass(frozen=True)
class RuntimeInstance:
    runtime_instance_id: RuntimeInstanceId
    build_identity: RuntimeBuildIdentity
    started_at: datetime
    stopped_at: datetime | None
```

Every daemon start creates a new `runtime_instance_id`.

Execution and queue ownership may reference it.

---

# 41. Core Repository Protocols

The domain layer defines protocols; SQLite implementations come later.

## RuntimeJobRepository

```python
class RuntimeJobRepository(Protocol):
    async def get(self, job_id: JobId) -> RuntimeJob:
        ...

    async def create(self, job: RuntimeJob) -> RuntimeJob:
        ...

    async def mutate(
        self,
        job_id: JobId,
        expected_revision: int,
        mutations: tuple[RuntimeJobMutation, ...],
    ) -> RuntimeJob:
        ...
```

`mutate` uses CAS semantics.

---

## ExecutionRepository

```python
class ExecutionRepository(Protocol):
    async def get(self, execution_id: ExecutionId) -> Execution:
        ...

    async def find_committed_by_operation_key(
        self,
        operation_key: OperationKey,
    ) -> Execution | None:
        ...

    async def find_active_by_operation_key(
        self,
        operation_key: OperationKey,
    ) -> Execution | None:
        ...

    async def create_attempt(self, execution: Execution) -> Execution:
        ...

    async def transition_status(
        self,
        execution_id: ExecutionId,
        expected_status: ExecutionStatus,
        new_status: ExecutionStatus,
    ) -> Execution:
        ...
```

Exact repository transition APIs may be refined to support atomic multi-record transactions.

---

## EventRepository

```python
class EventRepository(Protocol):
    async def get(self, event_id: EventId) -> Event:
        ...

    async def persist(self, event: Event) -> Event:
        ...

    async def claim_next(
        self,
        runtime_instance_id: RuntimeInstanceId,
        now: datetime,
    ) -> Event | None:
        ...

    async def mark_processed(self, event_id: EventId) -> None:
        ...
```

Lease semantics belong in the persistence plan.

---

## CommandRepository

```python
class CommandRepository(Protocol):
    async def get(self, command_id: CommandId) -> Command:
        ...

    async def persist(self, command: Command) -> Command:
        ...

    async def get_or_create_by_dedupe_key(
        self,
        command: Command,
    ) -> Command:
        ...

    async def claim_next(
        self,
        runtime_instance_id: RuntimeInstanceId,
        now: datetime,
    ) -> Command | None:
        ...
```

---

## ArtifactRepository

```python
class ArtifactRepository(Protocol):
    async def get_metadata(
        self,
        artifact_id: ArtifactId,
        version: ArtifactVersion,
    ) -> ArtifactMetadata:
        ...

    async def list_versions(
        self,
        artifact_id: ArtifactId,
    ) -> tuple[ArtifactMetadata, ...]:
        ...
```

Professional artifact bytes belong behind a separate `ArtifactFileStore`.

---

## InteractionRepository

```python
class InteractionRepository(Protocol):
    async def get(self, interaction_id: InteractionId) -> Interaction:
        ...

    async def get_active_for_job(
        self,
        job_id: JobId,
    ) -> Interaction | None:
        ...
```

Atomic Interaction + RuntimeJob projection mutations may require a transaction coordinator rather than independent repository calls.

---

## InteractionMessageRepository

```python
class InteractionMessageRepository(Protocol):
    async def list_unprocessed_authorized_human_messages(
        self,
        interaction_id: InteractionId,
    ) -> tuple[InteractionMessage, ...]:
        ...

    async def get(self, message_id: MessageId) -> InteractionMessage:
        ...
```

The professional commit transaction must be able to mark an exact message-ID batch processed.

---

## FailureRepository

```python
class FailureRepository(Protocol):
    async def create(self, failure: Failure) -> Failure:
        ...

    async def get(self, failure_id: FailureId) -> Failure:
        ...

    async def list_unresolved(
        self,
        job_id: JobId,
    ) -> tuple[Failure, ...]:
        ...

    async def resolve(
        self,
        failure_id: FailureId,
        resolved_at: datetime,
        resolution_message: str | None,
    ) -> Failure:
        ...
```

---

# 42. Infrastructure Protocols

## ArtifactFileStore

```python
class ArtifactFileStore(Protocol):
    async def stage(
        self,
        execution_id: ExecutionId,
        artifact_type: ArtifactType,
        content: bytes,
    ) -> StagedArtifact:
        ...

    async def finalize(
        self,
        staged: StagedArtifact,
        artifact_id: ArtifactId,
        version: ArtifactVersion,
    ) -> ArtifactRef:
        ...

    async def verify(self, artifact_ref: ArtifactRef) -> bool:
        ...
```

---

## ProfessionalInvoker

```python
class ProfessionalInvoker(Protocol):
    async def invoke(
        self,
        bundle: InvocationBundle,
    ) -> RawProfessionalResponse:
        ...
```

The first runtime implementation should provide:

```text
FakeProfessionalInvoker
```

before a real provider adapter.

---

## EvidenceSource

```python
class EvidenceSource(Protocol):
    async def search(
        self,
        query: EvidenceQuery,
    ) -> EvidenceSearchResult:
        ...
```

Provider-specific failures are translated into normalized runtime failure categories.

---

## OutputExtractor

```python
class OutputExtractor(Protocol):
    def extract(
        self,
        response: RawProfessionalResponse,
        output_contract: OutputContract,
    ) -> tuple[StagedArtifactCandidate, ...]:
        ...
```

Extraction parses.

It does not establish professional correctness.

---

# 43. Runtime Service Protocols

## OperationHandler

```python
class OperationHandler(Protocol):
    async def execute(
        self,
        job_id: JobId,
        command: Command,
        specification: OperationSpecification,
    ) -> ExecutionResult:
        ...
```

Handlers coordinate.

They do not own routing or unrestricted mutation authority.

---

## CommitCoordinator

```python
class CommitCoordinator(Protocol):
    async def commit(
        self,
        execution: Execution,
        specification: OperationSpecification,
        staged_outputs: tuple[StagedArtifact, ...],
        requested_mutations: tuple[RuntimeJobMutation, ...],
        consumed_message_ids: tuple[MessageId, ...] = (),
    ) -> CommitResult:
        ...
```

Responsibilities:

```text
validate mutation authority
validate output contract
validate freshness
finalize immutable output as required
perform authoritative SQLite professional commit
persist artifact_committed
```

The implementation may separate file finalization from SQLite commit internally.

---

## Router

```python
class Router(Protocol):
    async def evaluate(
        self,
        job_id: JobId,
    ) -> RoutingOutcome:
        ...
```

Routing operates on current committed professional state only.

---

## RecoveryCoordinator

```python
class RecoveryCoordinator(Protocol):
    async def recover(self) -> RecoveryReport:
        ...
```

It coordinates, but does not necessarily implement every recovery rule itself.

---

# 44. Result Types

Avoid returning loosely structured dictionaries.

Recommended:

```python
@dataclass(frozen=True)
class ExecutionResult:
    execution_id: ExecutionId
    status: ExecutionStatus
    committed_outputs: tuple[ArtifactRef, ...]
    failure_id: FailureId | None
```

```python
@dataclass(frozen=True)
class CommitResult:
    job: RuntimeJob
    execution: Execution
    committed_outputs: tuple[ArtifactRef, ...]
    event_id: EventId
```

```python
@dataclass(frozen=True)
class RoutingOutcome:
    job: RuntimeJob
    decision: RoutingDecision | None
    lifecycle_changed_event_id: EventId | None
```

```python
@dataclass(frozen=True)
class RecoveryReport:
    recovered_executions: int
    recovered_events: int
    recovered_commands: int
    recovered_interactions: int
    unresolved_failures: tuple[FailureId, ...]
```

---

# 45. Domain Exceptions

Exceptions should represent implementation/control-flow faults.

Persistent operational failures are represented by `Failure` records.

Recommended exception hierarchy:

```python
class RRSRuntimeError(Exception):
    pass

class DomainValidationError(RRSRuntimeError):
    pass

class ConcurrencyConflict(RRSRuntimeError):
    pass

class StaleExecutionError(RRSRuntimeError):
    pass

class UnauthorizedMutationError(RRSRuntimeError):
    pass

class ArtifactStorageConflict(RRSRuntimeError):
    pass

class SchemaValidationError(RRSRuntimeError):
    pass

class OperationSpecificationError(RRSRuntimeError):
    pass

class EvidenceSourceUnavailable(RRSRuntimeError):
    pass

class RuntimeIntegrityError(RRSRuntimeError):
    pass
```

Important distinction:

```text
Python exception
= immediate software control flow

Failure record
= durable runtime fact/history
```

Failure mapping converts relevant exceptions into persistent `Failure` records.

---

# 46. Immutability and Collections

Recommended default:

```python
@dataclass(frozen=True)
```

for domain values and aggregates loaded from repositories.

Collections exposed from aggregates should prefer:

```text
tuple
frozenset
```

over mutable:

```text
list
set
```

Mutable builders may exist internally inside infrastructure implementations, but repository/service boundaries return immutable domain state.

---

# 47. Serialization Boundary

Domain types should not implement provider or SQLite serialization directly.

Recommended separation:

```text
domain object
↕
repository mapper / serializer
↕
SQLite row

domain object
↕
provider adapter mapper
↕
provider JSON/API object
```

This protects the domain model from infrastructure schema changes.

---

# 48. Time Handling

All internal timestamps should be timezone-aware.

Recommended canonical storage/domain convention:

```text
UTC
```

Example:

```python
datetime.now(timezone.utc)
```

Human-facing CLI output may convert to local time.

Provider chronology values such as Discord message timestamps must preserve provider chronology semantics.

---

# 49. Hashes

Introduce explicit semantic types or validation helpers for:

```text
content_hash
operation_specification_hash
operation_registry_hash
result_fingerprint
operation_key
```

Recommendation:

```text
sha256:<hex>
```

for content/specification fingerprints.

`operation_key` may be a prefixed deterministic hash:

```text
OPKEY-<digest>
```

Exact encoding belongs to implementation detail but must be deterministic.

---

# 50. State Validation

Domain constructors or factories should reject impossible state.

Examples:

```text
RuntimeJob revision < 1
→ invalid

InteractionProjection.status == none
+ interaction_id != null
→ invalid

Health.status == healthy
+ failure_id != null
→ invalid

Execution.status == committed
+ completed_at == null
→ invalid

ArtifactVersion <= 0
→ invalid
```

Cross-aggregate validation belongs in services/repositories when construction alone cannot know the required state.

---

# 51. Domain Factories

Direct constructors may be appropriate for reconstruction from persistence.

Business creation should prefer factories for complex initial invariants.

Examples:

```python
RuntimeJob.create(...)
Execution.create_attempt(...)
Interaction.create(...)
Command.create(...)
Event.create(...)
Failure.create(...)
```

Factories should be deterministic except for injected ID/time generation.

Do not call global random/time functions from deep domain logic when deterministic tests can inject them.

---

# 52. ID and Clock Services

Recommended small protocols:

```python
class IdGenerator(Protocol):
    def new_job_id(self) -> JobId: ...
    def new_execution_id(self) -> ExecutionId: ...
    def new_event_id(self) -> EventId: ...
    def new_command_id(self) -> CommandId: ...
```

```python
class Clock(Protocol):
    def now(self) -> datetime: ...
```

These improve deterministic testing and crash/replay simulation.

---

# 53. Transaction Boundary Implication

Repository protocols alone are insufficient for cross-record atomic mutations.

The implementation will need a transaction-scoped unit or coordinator.

Do **not** finalize the interface here, but the SQLite phase must support:

```text
RuntimeJob
ArtifactMetadata
Execution
Event
InteractionMessage
Command
Failure
```

being mutated atomically in architecture-defined combinations.

Likely implementation strategies include:

```text
UnitOfWork
transaction-bound repository session
explicit transaction coordinator
```

The exact design belongs in:

```text
sqlite-schema.md
transaction-matrix.md
```

---

# 54. Recommended Initial Python Module Ownership

This is provisional and will be finalized in `package-interface-plan.md`.

```text
domain/
├── ids.py
├── enums.py
├── artifacts.py
├── jobs.py
├── operations.py
├── executions.py
├── events.py
├── commands.py
├── interactions.py
├── failures.py
├── retrieval.py
├── invocation.py
└── results.py
```

Protocols may initially live in:

```text
ports/
```

or beside their domain areas.

Do not allow package structure to redefine architecture ownership.

---

# 55. Domain Model Test Requirements

Before implementing repositories, domain tests should verify:

```text
ArtifactVersion rejects <= 0
RuntimeJob begins at revision >= 1
healthy HealthState rejects non-null failure_id
none InteractionProjection rejects active metadata
RuntimeJob aggregate exposes immutable collections
Operation Specification is immutable
pointer authority rejects unknown target/mutation
Execution terminal states obey completion invariants
CompletedProfessionalArtifact accepts only Evidence Response in V0.1
EvidenceSearchResult allows successful empty tuple
EvidenceSource failure is represented separately
hash/resource identity keeps Git provenance separate from semantic hash
```

These tests validate the vocabulary before persistence makes mistakes expensive.

---

# 56. Architecture Traceability

| Python Domain Area | Architecture Models |
|---|---|
| RuntimeJob / state projections | Runtime Job Model |
| ArtifactRef / versions / metadata | Runtime Job, Commit, Persistence |
| Execution / OperationKey / snapshots | Commit Model |
| Commands / Events | Event Model |
| RoutingDecision / predicates | Routing Model |
| OperationSpecification | Operation Specification Registry Model |
| OperationHandler / InvocationBundle | Handler Interface Model |
| ProfessionalInvoker / retrieval | Professional Invocation Model |
| Interaction / InteractionMessage | Discord Interaction, Persistence |
| Failure | Persistence, Control Surface |
| Build/runtime identity | Deployment, Registry |
| repository protocols | Persistence + owning domain models |
| Commit result / mutation authority | Commit, Registry, Job |
| recovery result/types | Persistence, Deployment |

---

# 57. Decisions Made in This Planning Phase

This document makes the following implementation-design decisions:

1. Domain state uses immutable Python value objects/aggregates by default.
2. IDs are strongly typed.
3. Internal time is timezone-aware UTC.
4. Runtime Job collections use deterministic immutable collection types.
5. Commands and Events should migrate toward typed tagged payload unions.
6. Repository APIs expose domain objects rather than database rows.
7. Python exceptions and persistent `Failure` records are distinct concepts.
8. Semantic operation-spec identity and Git/build provenance remain separate.
9. Transaction-scoped coordination is required but deferred to SQLite/Transaction planning.
10. A FakeProfessionalInvoker should implement the same `ProfessionalInvoker` protocol as real providers.

These choices do not alter frozen runtime architecture semantics.

---

# 58. Open Implementation Decisions for Later Phases

The following remain intentionally unresolved:

- `dataclasses` vs Pydantic for boundary validation.
- NewType vs frozen wrapper class for IDs.
- Exact Command status enum.
- Exact normalized FailureClass completeness.
- Unit-of-Work interface shape.
- exact SQLite schema.
- exact repository transaction APIs.
- package layout.
- dependency injection approach.
- model/provider SDK.
- Google Drive implementation technology.
- Discord SDK.
- CLI framework.
- serialization library.
- migration framework.

They are not blockers to the domain vocabulary.

---

# 59. Phase 2 Acceptance Criteria

The Python Domain Model is complete when:

- [ ] Every current Runtime Job field has one Python domain representation.
- [ ] Every current lifecycle and operation state has one canonical enum value.
- [ ] RuntimeJob is an immutable persistence-independent aggregate.
- [ ] Artifact references and versions are strongly represented.
- [ ] Execution and logical operation identity are separate types.
- [ ] Command, Event, Interaction, Failure, and artifact metadata records have domain representations.
- [ ] Operation Specification authority is represented explicitly.
- [ ] Handler, Invoker, EvidenceSource, Router, Commit Coordinator, and repository boundaries have protocols.
- [ ] Interviewer continuation is a typed union.
- [ ] Successful empty evidence retrieval is distinguishable from retrieval failure.
- [ ] Runtime build provenance is distinct from semantic specification identity.
- [ ] Domain mutation contracts avoid generic untyped Runtime Job writes.
- [ ] Cross-record transaction coordination is explicitly deferred to the SQLite/Transaction planning phase rather than ignored.
- [ ] No provider SDK, database row type, or CLI framework leaks into the domain model.

## Result

**READY FOR PHASE 3 — SQLITE PHYSICAL SCHEMA AND MIGRATION MODEL**