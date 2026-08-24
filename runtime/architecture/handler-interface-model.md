# RRS V3 Handler Interface and Responsibility Model

## Status

Draft V0.5 — FIX-029 and FIX-030 applied; supplemental Operation Specification Registry alignment retained

## Purpose

The Handler Interface and Responsibility Model defines how V3 runtime handlers coordinate professional operations.

Handlers are deterministic software components. They do not read contracts at runtime in the same way AI agents do, and they do not perform professional reasoning.

Their behavior is enforced through:

- Python interfaces and types.
- Runtime invariants.
- Schema validation.
- Explicit pointer-mutation authority.
- Automated tests.
- Shared execution/commit machinery.

Handlers orchestrate professional operations. Professional agents reason.

---

# Core Invariants

1. Handlers are operation-centric, not agent-centric.
2. Commands dispatch professional operations, not agents.
3. Handlers receive `job_id + command`, not mutable Runtime Job objects.
4. Runtime Job state is loaded through repositories.
5. Shared execution mechanics are centralized.
6. Concrete handlers define only operation-specific behavior.
7. Input resolution is deterministic.
8. Invocation Bundles are immutable once execution begins.
9. Every handler declares expected outputs.
10. Every handler declares allowed Runtime Job pointer mutations.
11. Handlers may not mutate pointers outside their declared authority.
12. Professional invocation occurs behind a replaceable adapter.
13. Handlers do not depend directly on Trello or Discord.
14. Handlers do not route Runtime Jobs directly.
15. Successful commits emit Events.
16. Routing is triggered through the Event/Command layer.
17. Deterministic reconciliation logic remains separate from professional reasoning.
18. Handler behavior is ultimately enforced by executable code and tests.
19. The handler framework must remain compatible with future Analyst/Custodian decomposition.
20. OperationHandlers never encode permanent ownership by a professional role; the professional role/resources are resolved by the operation specification.
21. Operation declarations live in the Operation Specification Registry, not as duplicated class-level handler configuration.

---

# 1. Common Handler Interface

Every professional operation handler should implement a common conceptual interface:

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

The handler receives `job_id + command`. It does not receive a mutable Runtime Job instance from upstream callers. The handler loads current Runtime Job state through the Runtime Job repository.

---

# 2. Handler Execution Pipeline

Every professional operation should follow the same high-level pipeline:

```text
Validate command
→ Load Runtime Job
→ Validate lifecycle
→ Validate health
→ Resolve invocation inputs
→ Build operation identity
→ Check idempotency
→ Create Execution attempt
→ Invoke professional operation
→ Stage outputs
→ Validate outputs
→ Check input freshness
→ Persist immutable artifacts
→ Atomic Runtime Job pointer commit
→ Finalize Execution
→ Emit Events
```

Routing occurs afterward through the Event/Command/Router pipeline.

---

# 3. Shared Execution Framework

Common lifecycle mechanics should live in a shared framework rather than being reimplemented in every concrete handler.

Conceptually:

```python
class BaseOperationHandler:
    async def execute(self, job_id, command, specification):
        job = await self.jobs.get(job_id)
        self.validate_command(command)
        self.validate_runtime_state(job, specification)
        bundle = await self.resolve_inputs(job, command, specification)
        operation_key = self.build_operation_key(bundle)
        existing = await self.executions.find_by_operation_key(operation_key)

        if existing and existing.is_committed:
            return self.result_from_existing(existing)

        execution = await self.begin_execution(
            job=job,
            command=command,
            bundle=bundle,
            operation_key=operation_key,
        )

        try:
            raw_response = await self.invoke(bundle)
            staged_outputs = await self.stage_outputs(execution, raw_response)
            await self.validate_outputs(bundle, staged_outputs)
            await self.check_freshness(job_id, bundle)
            result = await self.commit(execution, staged_outputs)
        except Exception as exc:
            return await self.handle_failure(execution, exc)

        # CommitCoordinator persists artifact_committed transactionally
        # with the authoritative professional commit.
        return result
```

This is conceptual architecture, not required final Python syntax.

---

# 4. Concrete Handler Responsibilities

Concrete handlers implement only operation-specific execution behavior that cannot be expressed declaratively.

The handler receives a resolved immutable:

```text
OperationSpecification
```

The specification owns:
- allowed lifecycle phases,
- required/optional inputs,
- dependency declarations,
- retrieval requirement,
- professional binding,
- required resources,
- expected outputs,
- coupled output groups,
- schema references,
- pointer mutation authority,
- deterministic reconciliation declarations.

Concrete handlers implement only mechanics such as:

```text
resolve_operation_specific_inputs()
perform_operation_specific_retrieval_query_construction()
validate_operation_specific_cross_output_rules()
build_authorized_pointer_mutation_values()
```

Shared framework code owns lifecycle validation, resource loading, professional binding resolution, generic validation, freshness, commit authorization, idempotency, and Event emission.

Do not duplicate declarative specification values inside handler classes.

If handler behavior conflicts with the resolved specification:

```text
specification authority wins
→ unauthorized behavior rejected
```

---

# 5. Invocation Bundle

Handlers resolve professional inputs into an immutable Invocation Bundle.

```python
@dataclass(frozen=True)
class InvocationBundle:
    job_id: JobId
    operation_type: OperationType
    artifact_refs: tuple[ArtifactRef, ...]
    resource_refs: tuple[ResourceRef, ...]
    schema_refs: tuple[SchemaRef, ...]
    input_snapshot: InputSnapshot
```

The Invocation Bundle defines exactly what professional state and resources were supplied to the professional operation.

---

# 6. Input Resolver Boundary

Resolvers may:

- Read Runtime Job current pointers.
- Resolve exact artifact versions.
- Load professional contracts.
- Load task instructions.
- Load schemas.
- Load shared resources.
- Build deterministic input snapshots.

Resolvers must not:

- Interpret professional evidence.
- Decide whether evidence is strong.
- Change professional state.
- Select downstream lifecycle.
- Rewrite Runtime Job pointers.

---

# 6.1 Evidence Retrieval Boundary

When an operation requires EvidenceSource retrieval, the handler resolves retrieval before professional invocation.

Canonical flow:

```text
resolve professional inputs
→ execute required retrieval
→ validate retrieval result
→ build immutable Invocation Bundle
→ invoke professional agent
```

If required retrieval fails:

```text
EvidenceSource unavailable / unauthorized / timed out / invalid
→ do not invoke professional agent
→ Execution failure_class = EVIDENCE_SOURCE_UNAVAILABLE
→ retry policy applies
```

The handler must distinguish:

```text
retrieval succeeded with zero matches
```

from:

```text
retrieval did not successfully execute
```

Only the first may be represented as an empty retrieval result.

For optional retrieval, continuation without retrieval is permitted only when the handler's operation specification explicitly declares `retrieval_requirement = optional`.

# 7. Expected Output Declaration

Every Operation Specification declares required professional output types. The following is the current V2-compatible operation set:

```text
generate_analysis
→ Job Experience Analysis

request_evidence
→ Evidence Request

investigate_evidence_request
→ Evidence Response

integrate_evidence
→ updated Job Experience Record version(s)

generate_resume
→ Targeted Resume
→ Writer Content Manifest

evaluate_resume
→ Resume Evaluation
```

Missing required output causes execution failure before commit.

---

# 8. Coupled Outputs

Operation Specifications may declare output groups that must commit together.

Current known coupled product:

```text
generate_resume
→ Targeted Resume
→ Writer Content Manifest
```

The handler must treat this as one commit group. No handler may advance only one pointer from a semantically coupled output group.

---

# 9. Pointer Mutation Authority

Runtime pointer authority should be represented explicitly in code.

```python
class PointerField(Enum):
    TARGET_JOB = "target_job"
    JER_SET = "jer_set"
    JEA = "jea"
    ACTIVE_ERQS = "active_erqs"
    UNINTEGRATED_EVIDENCE_RESPONSES = "unintegrated_evidence_responses"
    RESUME = "resume"
    WCM = "wcm"
    EVALUATION = "evaluation"
```

Each Operation Specification declares a fixed pointer-mutation set.

Current conceptual mapping:

| Operation | Allowed Current-Pointer Mutations |
|---|---|
| `generate_analysis` | `jea`; deterministic `active_erqs` reconciliation when applicable |
| `request_evidence` | `active_erqs` |
| `investigate_evidence_request` | `unintegrated_evidence_responses` |
| `integrate_evidence` | `jer_set`; remove integrated response refs |
| `generate_resume` | `resume`, `wcm` |
| `evaluate_resume` | `evaluation` |

This table describes current V2-compatible operation semantics and is provisional pending the Analyst/Custodian domain refactor.

Pointer authority belongs to operations, not professional role names. Rebinding `generate_analysis` from Researcher to Analyst does not grant new pointer authority unless the operation specification itself changes.

---

# 10. Mutation Enforcement

The shared Commit Coordinator must verify:

```text
requested mutation ∈ specification.pointer_authority
```

If not, reject commit.

Runtime pointer authority should not rely on developer convention.

---

# 11. Deterministic Reconciliation

Some Runtime Job pointer changes may follow deterministically from a newly committed professional artifact.

Example:

```text
new JEA committed
→ compare Material Evidence Need state with active ERQ origin references
→ remove ERQs whose originating need is resolved or no_longer_material
```

Conceptual helper:

```python
def reconcile_active_erqs(
    active_erqs: tuple[ArtifactRef, ...],
    committed_jea: JobExperienceAnalysis,
) -> tuple[ArtifactRef, ...]:
    ...
```

Deterministic reconciliation may only use explicit schema state. It must not infer professional meaning from prose.

---

# 12. Professional Invoker

Professional operations should execute behind a replaceable invocation interface.

```python
class ProfessionalInvoker(Protocol):
    async def invoke(
        self,
        bundle: InvocationBundle,
    ) -> RawProfessionalResponse:
        ...
```

Possible implementations:

```text
OpenAIProfessionalInvoker
LocalModelInvoker
TestProfessionalInvoker
```

Handlers should not depend on one specific model provider.

---

# 13. Runtime Ports / Interfaces

Handlers should depend on interfaces rather than infrastructure implementations.

Recommended ports:

```text
RuntimeJobRepository
ArtifactRepository
ExecutionRepository
EventRepository
ResourceRepository
SchemaRegistry
OperationSpecificationRegistry
ProfessionalInvoker
CommitCoordinator
```

Potential future ports:

```text
InteractionRepository
CommandRepository
```

Professional handlers should not directly depend on Trello API, Discord API, provider-specific webhook structures, or storage-specific SQL/filesystem details.

---

# 14. Command Dispatch

Commands select operations.

Canonical dispatch:

```python
spec = operation_specifications.get(command.operation_type)
handler = handlers.get(spec.handler_key)

result = await handler.execute(
    command.job_id,
    command,
    spec,
)
```

The registries are distinct:

```text
Operation Specification Registry
operation_type → semantics + handler_key

Handler Registry
handler_key → Python implementation
```

Dispatch does not use professional agent identity.

A handler implementation may support compatible specifications, but it does not define the specification itself.

---

# 15. Why Dispatch by Operation

Operation-centric dispatch prevents orchestration code from becoming coupled to the current professional organization.

Current V2-compatible implementation may resolve:

```text
generate_analysis
→ Researcher resources

request_evidence
→ Researcher resources

integrate_evidence
→ Researcher resources
```

These are resource bindings, not permanent handler ownership.

Future mappings may resolve:

```text
generate_analysis
→ Analyst resources

retrieve_evidence
→ Custodian resources

integrate_evidence
→ Custodian resources
```

without changing the common runtime dispatch rule:

```text
command.operation_type
→ OperationHandler
→ OperationSpecification
→ professional role/resources
```

A handler such as:

```text
GenerateAnalysisHandler
```

means:

```text
handler for the generate_analysis operation
```

not:

```text
ResearcherHandler
```

The same handler framework may load different contracts/tasks/schemas after the professional domain split.

If the Analyst/Custodian redesign introduces genuinely new operations, those operations may receive new handlers. Existing orchestration abstractions remain unchanged.


---

# 16. Lifecycle Compatibility

Each Operation Specification declares allowed lifecycle phases.

Current conceptual mapping:

```text
generate_analysis → analysis
request_evidence → evidence_request
investigate_evidence_request → investigation
integrate_evidence → evidence_integration
generate_resume → resume_production
evaluate_resume → evaluation
```

If an invalid command arrives, the handler rejects it. It does not silently repair lifecycle state.

---

# 17. Health Compatibility

Normal professional operations may execute when health is `healthy` or `degraded`.

They should not normally start when health is `recoverable_failure` or `blocked` unless the command is specifically a retry/recovery path.

---

# 18. Handler Validation Responsibilities

Common validation includes:

```text
required outputs present
artifact type correct
schema validation passes
cross-output validation passes
input freshness preserved
pointer mutations permitted
commit conflicts absent
```

Concrete handlers may add operation-specific checks.

Writer output validation may include Resume/WCM identity consistency. Evidence Response validation may include exact ERQ-version reference integrity.

Handlers do not add professional interpretation.

---

# 19. Execution Result

Handlers return runtime execution state, not raw professional artifacts.

```python
@dataclass(frozen=True)
class ExecutionResult:
    execution_id: ExecutionId
    operation_key: OperationKey
    status: ExecutionStatus
    committed_artifacts: tuple[ArtifactRef, ...]
    job_revision: int | None
```

Detailed failure state remains in the Execution record.

---

# 20. Failure Classes

Handlers normalize execution failures to the Artifact/Execution Commit Model vocabulary.

```python
class FailureClass(Enum):
    EVIDENCE_SOURCE_UNAVAILABLE
    INVOCATION_FAILURE
    OUTPUT_PARSE_FAILURE
    SCHEMA_VALIDATION_FAILURE
    CROSS_OUTPUT_VALIDATION_FAILURE
    STALE_INPUT
    ARTIFACT_PERSISTENCE_FAILURE
    POINTER_COMMIT_CONFLICT
    RUNTIME_JOB_PERSISTENCE_FAILURE
    UNKNOWN_FAILURE
```

Integration projection failures are not professional-handler failures.

---

# 21. Event Emission

Professional commit Events have explicit ownership.

The Commit Coordinator persists:

```text
artifact_committed
```

inside the same SQLite transaction that commits artifact metadata, Runtime Job pointer mutations, Runtime Job revision, commit-group state, and Execution finalization.

Handlers must not emit `artifact_committed` after `commit()` returns.

Execution lifecycle telemetry may separately record or emit:

```text
execution_started
execution_committed
execution_failed
```

but `execution_committed` is audit/telemetry only and never substitutes for `artifact_committed`.

For semantically coupled outputs, the Commit Coordinator persists exactly one `artifact_committed` Event for the successful commit group.

---

# 22. Routing Trigger Boundary

Handlers do not call routing logic directly.

Preferred flow:

```text
Handler commits professional output
→ artifact_committed Event
→ Event processor
→ evaluate_routing Command
→ Router
```

This keeps handlers, router, and integrations independently testable.

---

# 23. Trello Boundary

Professional handlers must not:

- Move Trello cards.
- Add Trello comments.
- Inspect Trello lists.
- Read Trello state to determine lifecycle.
- Store professional artifacts in Trello.

Trello synchronization occurs through integration/event components.

---

# 24. Discord Boundary

Professional handlers must not:

- Open Discord threads directly.
- Read raw Discord webhook payloads.
- Treat Discord transcripts as professional evidence.
- Mutate Runtime Job lifecycle based on Discord provider state.

Discord belongs behind Interaction/Event adapters.

---

# 25. Long-Lived Investigation Operations

Most handlers should be short-lived. Human investigation may be long-lived.

The architecture must allow investigation to pause without holding database transactions, filesystem locks, worker processes, or in-memory mutable Job state.

The Interaction subsystem should preserve continuation state. This does not change the Evidence Response professional output contract.

---

# 26. Evidence Integration

V3 design has identified the need for an explicit professional `integrate_evidence` operation.

This responsibility should eventually belong to the professional evidence Custodian.

The operation should:

- Consume confirmed Evidence Response(s).
- Reconcile them into authoritative evidence state.
- Produce updated JER version(s).
- Preserve evidence provenance.
- Preserve conflicts and uncertainty.

It should not simultaneously perform target-fit analysis.

---

# 27. Future Analyst/Custodian Compatibility

Potential future operations include:

```text
analyze_target
request_information
retrieve_evidence
request_evidence
integrate_evidence
generate_analysis
```

The Handler framework should require only:

- New `OperationType` values.
- New concrete handlers/resolvers.
- New expected-output declarations.
- New pointer mutation declarations.
- Updated routing rules.

The shared execution pipeline should not require redesign.

---

# 28. Handler Model Is Not an Agent Contract

This document is an implementation architecture resource.

Handlers do not read it at runtime.

The executable authority hierarchy is:

```text
Architecture model
→ Python interfaces/types
→ Handler implementation
→ Automated tests
```

When prose and executable implementation disagree, the system should be treated as defective until reconciled.

---

# 29. Automated Testing

Handler invariants should be enforced with automated tests.

Required test classes include:

```text
generate_resume during analysis
→ rejected

GenerateResumeHandler attempts evaluation mutation
→ rejected

two identical schedule_operation Commands
→ one logical professional operation

Writer starts with JEA v3
JEA v4 commits before Writer returns
→ Writer output stale
→ Resume/WCM pointers unchanged

Resume persists
WCM fails
→ neither current pointer advances

Trello projection fails after professional commit
→ professional pointers remain committed
```

---

# 30. Suggested Python Package Boundary

Implementation may eventually resemble:

```text
runtime/
├── models/
│   ├── runtime_job.py
│   ├── execution.py
│   ├── event.py
│   ├── command.py
│   └── artifacts.py
├── handlers/
│   ├── base.py
│   ├── generate_analysis.py
│   ├── request_evidence.py
│   ├── investigation.py
│   ├── integrate_evidence.py
│   ├── generate_resume.py
│   └── evaluate_resume.py
├── repositories/
├── invocation/
├── commit/
└── tests/
```

This structure is provisional.

---

# 31. V0.1 Acceptance Criteria

The Handler Interface and Responsibility Model is acceptable when:

- [ ] Handlers are operation-centric rather than agent-centric.
- [ ] Professional role/resource ownership is resolved by operation specification rather than hard-coded handler identity.
- [ ] Current Researcher operation bindings are documented as V2-compatible and provisional.
- [ ] Analyst/Custodian rebinding does not require changing the common handler interface.
- [ ] One common handler interface exists.
- [ ] Handlers receive `job_id + command`.
- [ ] Runtime Job is loaded through a repository.
- [ ] Shared execution mechanics are centralized.
- [ ] Declarative operation semantics live in the Operation Specification Registry rather than handler classes.
- [ ] Handler Registry resolves Python implementation by `handler_key`; Operation Specification Registry resolves semantics by `operation_type`.
- [ ] Handlers receive immutable resolved specifications and cannot expand their authority.
- [ ] Concrete handlers define only operation-specific behavior.
- [ ] Invocation Bundles are deterministic and immutable.
- [ ] Resolvers do not perform professional reasoning.
- [ ] Every handler declares expected outputs.
- [ ] Every handler declares allowed pointer mutations.
- [ ] Unauthorized pointer mutation is rejected.
- [ ] Deterministic reconciliation uses schema-defined state only.
- [ ] Professional invocation is replaceable/testable.
- [ ] Professional handlers do not depend directly on Trello or Discord.
- [ ] Lifecycle compatibility is enforced.
- [ ] Health compatibility is enforced.
- [ ] Output validation occurs before commit.
- [ ] Coupled outputs remain atomic.
- [ ] Handlers never route directly.
- [ ] Successful commits emit generic Events.
- [ ] Failure handling preserves last valid professional state.
- [ ] Handler behavior is enforceable through Python types and tests.
- [ ] Future Analyst/Custodian operations can be added without redesigning the shared framework.

---

# Next Design Step

After this model is accepted, continue with the **V3 Persistence Model**.

The Persistence Model should define:

- Runtime Job storage.
- Professional artifact storage.
- Execution storage.
- Event storage.
- Interaction storage.
- Immutable artifact versioning.
- Runtime transactions.
- Concurrency/version checks.
- Storage technology boundaries.
- Recovery guarantees.