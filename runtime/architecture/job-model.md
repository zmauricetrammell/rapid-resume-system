# RRS V3 Runtime Job Model

## Status

Draft V0.9 — FIX-001, FIX-002, FIX-013, FIX-014, FIX-027, FIX-028, FIX-031, FIX-033, and FIX-034 applied

## Purpose

The Runtime Job is the authoritative V3 control-plane representation of one resume-processing job.

It records:
- Current runtime lifecycle state.
- Current professional artifact pointers.
- Current automated operation.
- Current human-interaction state.
- Runtime health.
- Append-only routing decisions.

It does **not** contain professional reasoning or replace V2 professional artifacts.

The Runtime Job is intentionally small. Historical professional artifacts, execution records, events, and interaction records live outside the Job and are referenced when needed.

---

# Core Invariants

1. Professional state and runtime state remain separate.
2. Professional agents never mutate Runtime Job state.
3. Handlers own Runtime Job mutations.
4. Current professional pointers always reference the latest successfully validated and committed state.
5. Current pointers are never cleared merely because a new operation has started.
6. New professional state becomes current only after persistence, schema validation, and stale-input validation succeed.
7. Runtime state uses orthogonal dimensions rather than one combined state enum.
8. Routing decisions are derived from professional artifact state.
9. Routing history is append-only.
10. Trello and other integrations project Runtime Job state but are not authoritative for it.
11. Historical professional artifacts remain immutable outside the Runtime Job.
12. Terminal jobs do not automatically reopen.
13. Every successful authoritative Runtime Job mutation increments `identity.revision` exactly once.
14. Runtime Job writes use optimistic compare-and-swap semantics against the expected revision.
15. Runtime Job revision protects mutation concurrency; professional freshness is determined from exact operation dependencies, not revision alone.
16. Collection-valued professional state is mutated semantically with `ADD`, `REMOVE`, `REPLACE`, or `UPSERT_VERSION`; handlers do not overwrite collections from stale snapshots.
17. Collection mutations are applied atomically with the Runtime Job revision check.
18. Each Runtime Job pins exact JER versions; newer reusable JER versions do not silently propagate into existing in-flight Jobs.
19. Runtime Job interaction state is a coarse projection of the authoritative Interaction record and does not mirror every provider/runtime Interaction status.
20. Process Feedback is governance/Kaizen evidence and never appears in `RuntimeJob.professional_state`.
21. Runtime Job creation is owned by the deterministic `create_job` runtime Command; a new Job begins at revision 1 with an exact Target Job pointer and pinned initial JER snapshot.
22. Information Request, Information Response, and Target Role state are explicitly deferred future architecture concepts and are not part of the V0.1 Runtime Job aggregate.
23. `RuntimeJobRepository.get()` returns one canonical in-memory `RuntimeJob` aggregate independent of normalized SQLite table layout.
24. `health.failure_id` references the current material unresolved persistent `Failure` record; detailed failure state is not embedded in the Runtime Job.

---

# Runtime Job Structure

```yaml
runtime_job:
  schema_version: "3.0"

  identity:
    job_id: JOB-0001
    revision: 18
    created_at: 2026-08-22T19:00:00-07:00
    updated_at: 2026-08-22T19:14:00-07:00
    completed_at: null

  lifecycle:
    phase: analysis
    entered_at: 2026-08-22T19:05:00-07:00

  operation:
    status: idle
    operation_type: null
    execution_id: null
    started_at: null

  interaction:
    status: none
    interaction_type: null
    interaction_id: null
    started_at: null
    last_activity_at: null

  health:
    status: healthy
    failure_id: null
    retry_count: 0

  professional_state:
    target_job:
      artifact_type: target_job
      artifact_id: TARGET-0001
      artifact_version: 1
      uri: artifacts/TARGET-0001/v1.yaml

    jer_set:
      - artifact_type: job_experience_record
        artifact_id: JER-0001
        artifact_version: 3
        uri: artifacts/JER-0001/v3.yaml

      - artifact_type: job_experience_record
        artifact_id: JER-0007
        artifact_version: 2
        uri: artifacts/JER-0007/v2.yaml

    jea:
      artifact_type: job_experience_analysis
      artifact_id: JEA-0004
      artifact_version: 3
      uri: artifacts/JEA-0004/v3.yaml

    active_erqs: []
    unintegrated_evidence_responses: []
    resume: null
    wcm: null
    evaluation: null

  routing_history:
    - decision_id: ROUTE-00017
      decided_at: 2026-08-22T19:14:00-07:00
      from_phase: analysis
      to_phase: evidence_request
      predicate:
        name: has_unresolved_material_evidence_needs
        result: true
      basis:
        - artifact_type: job_experience_analysis
          artifact_id: JEA-0004
          artifact_version: 3
      reason: "Two unresolved Material Evidence Needs remain."
      execution_id: EXEC-0042
```

---

# 0. Canonical In-Memory RuntimeJob Aggregate

Repositories expose one canonical aggregate to handlers, routers, control-surface services, and recovery logic.

Conceptual Python shape:

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

Equivalent conceptual structure:

```yaml
runtime_job:
  identity: ...
  lifecycle: ...
  operation: ...
  interaction: ...
  health: ...
  professional_state: ...
  routing_history: [...]
```

Rules:
- The aggregate is the authoritative in-memory representation of current Runtime Job state.
- It is assembled by `RuntimeJobRepository`; callers do not manually join persistence tables.
- It contains current control-plane state and current professional artifact references, not artifact bodies.
- It does not expose SQLite row-layout details.
- Collection fields use deterministic immutable runtime collections such as tuples/frozen values once loaded.
- Repository mutations return or make available a newly loaded aggregate at the new revision rather than mutating a shared object in place.
- The aggregate's `identity.revision` is the CAS/concurrency version for authoritative Runtime Job mutations.
- Historical Events, Executions, Interactions, Failure records, and artifact bodies remain separate stores and are referenced by identity.

This aggregate is intentionally persistence-independent so SQLite normalization may evolve without changing handler/router contracts.

---

# 1. Identity

```yaml
identity:
  job_id: JOB-0001
  revision: integer
  created_at: datetime
  updated_at: datetime
  completed_at: datetime | null
```

Rules:
- `job_id` is immutable.
- `revision` is a monotonic positive integer representing the authoritative Runtime Job mutation version.
- A newly created Runtime Job begins at `revision: 1`.
- Every successful authoritative Runtime Job mutation increments `revision` exactly once.
- Failed or rejected mutations do not increment `revision`.
- `created_at` is immutable.
- `updated_at` changes on every successful Runtime Job mutation.
- `completed_at` is null until the Job reaches `complete`.


## 1.1 Revision and Optimistic Concurrency

Runtime Job mutations use optimistic compare-and-swap semantics.

Conceptually:

```text
load JOB-0001 at revision 18
        ↓
prepare authoritative mutation
        ↓
commit only if current revision is still 18
        ↓
success → apply mutation and revision becomes 19
conflict → reject mutation and reload current Job state
```

A repository implementation may express this as:

```sql
UPDATE runtime_jobs
SET revision = 19, ...
WHERE job_id = 'JOB-0001'
  AND revision = 18;
```

If no row is updated, the mutation encountered a concurrency conflict.

The caller must not silently overwrite current state.

Important distinction:

```text
Runtime Job revision
= concurrency protection for Runtime Job writes

Professional freshness dependencies
= whether the professional inputs consumed by an Execution are still current
```

An unrelated Runtime Job mutation may increment `revision` without making a professional Execution stale. After a compare-and-swap conflict, the runtime reloads the Job and separately evaluates the operation's exact freshness dependencies before deciding whether the mutation can be retried or the Execution is stale.


---

# 2. Lifecycle

Lifecycle answers: **Where is the Job in the professional processing lifecycle?**

```yaml
lifecycle:
  phase:
    enum:
      - new
      - analysis
      - evidence_request
      - investigation
      - evidence_integration
      - resume_production
      - evaluation
      - complete
      - manual_review
      - cancelled

  entered_at: datetime
```

Phase meanings:
- `new` — Job exists but processing has not begun.
- `analysis` — professional evidence is being analyzed or re-analyzed.
- `evidence_request` — Material Evidence Needs require ERQs.
- `investigation` — human factual investigation is required.
- `evidence_integration` — Evidence Responses are being reconciled into professional evidence.
- `resume_production` — current professional state supports resume generation.
- `evaluation` — current Resume + WCM product is being evaluated.
- `complete` — successful terminal state.
- `manual_review` — deterministic automation is suspended.
- `cancelled` — human-initiated terminal cancellation.

---

# 3. Operation

Operation answers: **What automated professional operation is currently executing?**

```yaml
operation:
  status:
    enum:
      - idle
      - queued
      - running
      - validating
      - committing

  operation_type:
    enum:
      - generate_analysis
      - request_evidence
      - investigate_evidence_request
      - integrate_evidence
      - generate_resume
      - evaluate_resume
    nullable: true

  execution_id: string | null
  started_at: datetime | null
```

Normal operation lifecycle:

```text
queued
→ running
→ validating
→ committing
→ idle
```

Current professional pointers are not changed before the `committing` stage succeeds.

---

# 4. Lifecycle / Operation Consistency

```text
generate_analysis
→ analysis

request_evidence
→ evidence_request

investigate_evidence_request
→ investigation

integrate_evidence
→ evidence_integration

generate_resume
→ resume_production

evaluate_resume
→ evaluation
```

An operation must not execute in an incompatible lifecycle phase.

---

# 5. Human Interaction

Interaction answers: **Is the Runtime Job currently associated with human participation?**

The Runtime Job stores only a coarse projection of Interaction state. Provider-specific and full lifecycle state belongs in the separate authoritative Interaction record.

```yaml
interaction:
  status:
    enum:
      - none
      - pending
      - active
      - paused
      - completed

  interaction_type:
    enum:
      - evidence_investigation
      - manual_review
    nullable: true

  interaction_id: string | null
  started_at: datetime | null
  last_activity_at: datetime | null
```

Rules:

```text
interaction_type == evidence_investigation
→ lifecycle.phase == investigation
```

```text
interaction_type == manual_review
→ lifecycle.phase == manual_review
```

```text
interaction.status in [pending, active, paused]
→ interaction_id must exist
```

The authoritative Interaction record may use a richer status vocabulary, including:

```text
pending
active
paused
completed
cancelled
```

The Runtime Job does not need to mirror `cancelled`.

When an authoritative Interaction is cancelled:

```text
Interaction.status = cancelled

Runtime Job interaction projection:
  status = none
  interaction_type = null
  interaction_id = null
  started_at = null
  last_activity_at = null
```

Lifecycle independently reflects the runtime consequence of cancellation, such as:

```text
manual_review
```

or:

```text
cancelled
```

according to the applicable runtime policy.

A completed Interaction may remain projected as:

```text
interaction.status = completed
```

until the next deterministic runtime transition clears or replaces the projection.

Discord thread IDs and all other provider-specific values belong only in the authoritative Interaction record.


---

# 6. Health

Health answers: **Can automated execution safely continue?**

```yaml
health:
  status:
    enum:
      - healthy
      - degraded
      - recoverable_failure
      - blocked

  failure_id: string | null
  retry_count: integer
```

Meanings:
- `healthy` — normal execution.
- `degraded` — a nonfatal runtime/integration problem exists; professional workflow may continue.
- `recoverable_failure` — current operation requires retry before continuing.
- `blocked` — automation cannot safely recover; manual review is required.

`failure_id` semantics:

```text
health.status == healthy
→ failure_id = null

health.status in [degraded, recoverable_failure, blocked]
→ failure_id references the current material unresolved Failure when one exists
```

A Runtime Job stores only the pointer to the current material failure. Full failure history belongs in the persistent Failure Store.

When the current material failure is resolved:
- its Failure record receives `resolved_at`,
- `health.failure_id` is cleared or replaced by another unresolved material Failure,
- health is recomputed through an authoritative Runtime Job mutation.

A historical resolved Failure is never deleted merely because health becomes healthy.

Example:
- Trello comment sync failure → `degraded`.
- Repeated schema-invalid agent output → `recoverable_failure`, then `blocked` after retry limits.

---

# 7. Professional State Pointers

```yaml
professional_state:
  target_job: artifact_ref
  jer_set:
    - artifact_ref
  jea: artifact_ref | null
  active_erqs:
    - artifact_ref
  unintegrated_evidence_responses:
    - artifact_ref
  resume: artifact_ref | null
  wcm: artifact_ref | null
  evaluation: artifact_ref | null
```

The Runtime Job stores only current pointers. Historical artifacts remain in the artifact store.


# 7.1 Collection Mutation Semantics

Collection-valued Runtime Job state must not be updated by reading the full collection, modifying it locally, and blindly replacing it.

V0.1 defines four semantic mutation operations:

```text
ADD
REMOVE
REPLACE
UPSERT_VERSION
```

Meanings:

- `ADD` — add one exact artifact reference if it is not already present.
- `REMOVE` — remove one exact/current artifact reference without deleting artifact history.
- `REPLACE` — replace the complete collection only when the operation explicitly owns the entire collection state.
- `UPSERT_VERSION` — for a logical artifact identity, replace the currently pinned version with a newly committed version; add it if no current version exists.

Examples:

```text
active_erqs
  request_evidence
  → ADD ERQ-0011:v1

active_erqs
  post-analysis reconciliation
  → REMOVE ERQ-0011:v1

unintegrated_evidence_responses
  completed investigation
  → ADD ERESP-0008:v1

unintegrated_evidence_responses
  successful evidence integration
  → REMOVE ERESP-0008:v1

jer_set
  evidence integration
  → UPSERT_VERSION JER-0007:v3 → JER-0007:v4
```

Collection mutations are applied against the current persisted collection inside the Runtime Job compare-and-swap commit.

If a Runtime Job revision conflict occurs:

```text
reload current collection
→ reapply semantic mutation
→ retry CAS if operation dependencies remain valid
```

This prevents lost updates such as:

```text
Handler A reads active_erqs = []
Handler B reads active_erqs = []

A adds ERQ-0011
B adds ERQ-0012

blind replacement would lose one ERQ
```

With semantic mutations:

```text
ADD ERQ-0011
ADD ERQ-0012
```

both survive regardless of which valid commit occurs first.

`REPLACE` should be used sparingly. It is valid only when a deterministic operation explicitly owns the complete resulting collection.


---

# 8. Artifact Reference

```yaml
artifact_ref:
  artifact_type:
    enum:
      - target_job
      - job_experience_record
      - job_experience_analysis
      - evidence_request
      - evidence_response
      - targeted_resume
      - writer_content_manifest
      - resume_evaluation

  artifact_id: string
  artifact_version:
    type: integer
    minimum: 1

  uri: string
```

Rules:
- References identify exact immutable versions.
- `uri` locates persisted content.
- Artifact contents are not duplicated in the Runtime Job.
- Handlers resolve artifact contents when building professional invocation bundles.

## 8.1 Process Feedback Boundary

Process Feedback is not current candidate professional state.

It may be stored in the common Artifact Store for governance, supervision, Kaizen, or process-improvement purposes, but it must not appear under:

```text
RuntimeJob.professional_state
```

and it must not participate in professional routing predicates.

Process Feedback therefore does not use a Runtime Job current pointer.

If Process Feedback needs Job provenance, that relationship belongs in artifact metadata or a governance/supervisory record rather than the Runtime Job professional-state aggregate.

---

# 9. Current JER Set

Professional evidence state contains multiple exact JER versions.

```yaml
jer_set:
  - artifact_type: job_experience_record
    artifact_id: JER-0001
    artifact_version: 4
    uri: artifacts/JER-0001/v4.yaml

  - artifact_type: job_experience_record
    artifact_id: JER-0007
    artifact_version: 3
    uri: artifacts/JER-0007/v3.yaml
```

Historical JER versions remain immutable outside the Job.

## 9.1 JER Snapshot Semantics

A Runtime Job's `jer_set` is a versioned snapshot of the reusable professional evidence state available to that Job.

Canonical rule:

```text
Reusable JER repository
→ may contain newer versions over time

New Runtime Job
→ resolves and pins the latest eligible JER versions at creation

Existing Runtime Job
→ keeps its exact pinned JER versions
→ does not silently advance when a reusable JER receives a newer version
```

This prevents evidence updates produced by one Job from unexpectedly changing the professional input state of another in-flight Job.

Example:

```text
JOB-0001 pins JER-0007 v3
JOB-0002 pins JER-0007 v3

JOB-0001 integrates new evidence
→ JER-0007 v4 is committed
→ JOB-0001 jer_set UPSERT_VERSION v3 → v4

JOB-0002 remains pinned to JER-0007 v3
```

`JOB-0002` may move to `JER-0007 v4` only through an explicit evidence-state refresh or evidence-integration operation that is valid for that Job.

A newer reusable JER version does not itself make another Job's existing Execution stale.

Freshness is evaluated against that Job's exact pinned professional dependencies.

## 9.2 New Job Initialization

When the `create_job` Command creates a new Runtime Job, its initial `jer_set` resolves the latest eligible committed version of each reusable JER included in the professional evidence baseline.

The same successful Job-creation transaction establishes:

```text
Runtime Job revision = 1
Target Job current pointer
initial exact jer_set snapshot
job_created Event
create_job Command completion
```

The resulting exact artifact references become that Job's initial evidence snapshot.

The intended `job_id` is allocated before Command execution and remains stable across retries. Retrying the same `create_job` Command must reconcile the same Job rather than creating another Runtime Job.


---

# 10. Active Evidence Requests

`active_erqs` contains only Evidence Requests relevant to current investigation state.

Resolved historical ERQs remain in artifact history and may be removed from current pointers without deleting the artifact.

---

# 11. Unintegrated Evidence Responses

`unintegrated_evidence_responses` contains Evidence Responses that exist but have not yet been reconciled into authoritative professional evidence.

After successful reconciliation:
1. New authoritative professional evidence is committed.
2. The Evidence Response remains immutable in history.
3. Its current pointer is removed from `unintegrated_evidence_responses`.

---

# 12. Current Product Pointers

Resume production uses a coupled product:

```yaml
resume: artifact_ref | null
wcm: artifact_ref | null
```

The Evaluation pointer identifies the latest successfully committed Resume Evaluation:

```yaml
evaluation: artifact_ref | null
```

---

# 13. Pointer Commit Model

Agents never set or clear Runtime Job pointers.

Handlers follow:

```text
1. Resolve current inputs.
2. Snapshot exact input artifact IDs + versions into Execution.
3. Invoke professional task.
4. Receive output.
5. Validate output.
6. Confirm execution inputs are still current.
7. Persist immutable output.
8. Atomically update permitted current pointer(s).
9. Return operation to idle.
10. Evaluate routing predicates.
```

If any step before successful commit fails, existing current professional pointers remain unchanged.

---

# 14. Stale Input Protection

Before committing professional output, compare the Execution input snapshot to current Runtime Job pointers.

Example:

```text
Writer execution started with JEA-0004 v3
Current Runtime Job now references JEA-0004 v4
```

The returned resume is stale.

The same principle applies to JER dependencies: an Execution becomes stale when the Runtime Job's own pinned JER reference changes, not merely because a newer reusable JER version exists elsewhere.

It may be persisted historically for diagnostics but must not become current state.

---

# 15. Handler Pointer Authority

Pointer authority includes the permitted mutation operation, not only the pointer/collection name.

Current V2-compatible conceptual mapping:

```text
handle_generate_analysis
→ SET jea
→ REMOVE active_erqs only through deterministic post-analysis reconciliation

handle_request_evidence
→ ADD active_erqs

handle_investigation
→ ADD unintegrated_evidence_responses

handle_integrate_evidence
→ UPSERT_VERSION jer_set
→ REMOVE unintegrated_evidence_responses

handle_generate_resume
→ SET resume
→ SET wcm

handle_evaluate_resume
→ SET evaluation
```

A handler may not substitute a broader mutation for its authorized semantic operation.

Examples:

```text
request_evidence may ADD an ERQ
request_evidence may not REPLACE active_erqs

evidence integration may UPSERT_VERSION affected JERs
evidence integration may not replace the entire jer_set from a stale snapshot
```

Exact executable mutation contracts belong in handler design and must be enforced by the commit layer.

---

# 16. Routing History

Routing history is append-only.

```yaml
routing_history:
  - decision_id: ROUTE-00017
    decided_at: datetime
    from_phase: analysis
    to_phase: evidence_request

    predicate:
      name: has_unresolved_material_evidence_needs
      result: true

    basis:
      - artifact_ref

    reason: "Two unresolved Material Evidence Needs remain."

    execution_id: EXEC-0042
```

A routing decision records **why a transition occurred**, not who should act next.

---

# 17. Routing Decision Fields

```yaml
decision_id: string
decided_at: datetime
from_phase: lifecycle_phase
to_phase: lifecycle_phase

predicate:
  name: string
  result: boolean

basis:
  - artifact_ref

reason: string
execution_id: string | null
```

Past routing decisions are never rewritten because later artifacts change.

---

# 18. Trello Projection

Trello comments may mirror routing decisions.

Example:

```text
Routing decision · ROUTE-00018

Analysis → Resume Production

Basis: JEA-0007 v5

No unresolved Material Evidence Needs remain.
```

The authoritative source remains `Runtime Job.routing_history`.

Trello synchronization failure should normally degrade runtime health without invalidating professional state or routing.

---

# 19. Initial Routing Predicate Vocabulary

Recommended V0.1 predicate names:

```text
has_unresolved_material_evidence_needs
has_unresolved_erqs
has_unintegrated_evidence_responses
has_blocking_product_defects
has_blocking_evidence_uncertainties
is_ready_to_submit
```

Prefer schema-defined professional state over free-text interpretation.

---

# 20. Normal Lifecycle Transitions

```text
new
 ↓
analysis
 ↓
├──────── unresolved evidence ────────┐
│                                    ▼
│                             evidence_request
│                                    ↓
│                               investigation
│                                    ↓
│                            evidence_integration
│                                    ↓
└────────────────────────────── analysis
 ↓
resume_production
 ↓
evaluation
 ↓
├── blocking Product Defect ───────► resume_production
├── blocking Evidence Uncertainty ─► analysis
└── ready_to_submit ───────────────► complete
```

Candidate Limitations do not independently create a lifecycle loop.

---

# 21. Exceptional Lifecycle Transitions

Any nonterminal phase may enter `manual_review` when deterministic automation cannot safely continue.

Any nonterminal phase may enter `cancelled` through explicit human cancellation.

`manual_review` may return to a safe resumable phase through explicit recovery action.

---

# 22. Terminal States

Terminal lifecycle phases:

```text
complete
cancelled
```

Handlers may not automatically transition out of terminal state.

V3 initially does not support automatic reopening.

---

# 23. State Mutation Ownership

```text
Professional Agent
→ professional reasoning
→ professional artifact contents

Job Creation Service
→ deterministic create_job Command
→ Target Job persistence
→ Runtime Job creation
→ initial JER snapshot

Handler
→ professional execution
→ validation
→ persistence
→ pointer commits

Router
→ deterministic lifecycle decisions

Runtime Job
→ current control-plane state
→ coarse current Interaction projection

Interaction Store
→ authoritative Interaction lifecycle and provider metadata

Trello / Discord
→ external projections and interaction surfaces
```

---

# 23.1 Explicitly Deferred Professional State

The following concepts are intentionally not part of the V0.1 Runtime Job professional-state aggregate:

```text
Information Request
Information Response
Target Role
```

Their absence in V0.1 is deliberate, not an implicit claim that they will never exist.

These concepts are reserved for the planned Analyst/Custodian decomposition.

Expected future use may include:

```text
Target Job
→ Analyst scrutinizes target
→ Target Role / structured target interpretation
→ Information Request
→ Custodian retrieval
→ Information Response
→ Analyst analysis
```

V0.1 does not define:
- Runtime Job current pointers for these artifact/state types,
- collection semantics for them,
- routing predicates for them,
- lifecycle phases dedicated to them,
- mutation authority for them.

Until the Analyst/Custodian design is finalized, runtime code must not invent placeholder fields such as:

```text
professional_state.target_role
professional_state.information_requests
professional_state.information_responses
```

If the future design introduces these concepts, they must be added through an explicit architecture/schema update with defined artifact identity/version semantics, current-state ownership, operation authority, routing behavior, persistence behavior, and freshness/identity dependencies.

This preserves the MVP boundary without constraining the final architecture.

---

# 24. Data Stored Outside Runtime Job

## Professional Artifact Store
Contains immutable artifact versions.

## Execution Store
Contains detailed handler invocation history.

Example:

```yaml
execution_id: EXEC-0042
job_id: JOB-0001
operation_type: generate_analysis
status: completed

inputs:
  - exact artifact references

outputs:
  - exact artifact references

started_at: ...
completed_at: ...
```

## Interaction Store
Contains provider-specific Discord or other human-interaction metadata.

## Event Store / Runtime Log
Contains webhook events, retries, integration events, and other runtime history.

## Failure Store

Contains persistent runtime failure records.

`RuntimeJob.health.failure_id` references the current material unresolved Failure when health is not healthy.

Failure history is not embedded in the Runtime Job aggregate.

## Governance / Process Feedback
Process Feedback may be retained in the common Artifact Store or a future supervisory/governance index, but it is not a current Runtime Job professional-state pointer.

---

# 25. Runtime Job Design Boundary

The Runtime Job should answer:
- What Job is this?
- What is its lifecycle phase?
- What operation is executing?
- Is human interaction active?
- Is runtime healthy?
- What professional artifact versions are currently authoritative?
- Why did the Job previously transition?

It should not answer:
- What professional evidence means.
- Whether a claim is strong.
- Why a candidate qualifies.
- What an agent should write.
- What an interviewer should ask.
- Which agent should receive the Job next.

---

# 26. V0.1 Acceptance Criteria

- [ ] `RuntimeJobRepository` returns one canonical persistence-independent `RuntimeJob` aggregate.
- [ ] The aggregate contains current control-plane state and references, not historical record bodies.
- [ ] `health.failure_id` references a persistent unresolved Failure record rather than embedding failure detail.
- [ ] Resolved Failure history remains persistent after Runtime Job health recovers.

- [ ] Lifecycle, operation, interaction, and health are orthogonal.
- [ ] Runtime Job interaction state is a coarse projection of the authoritative Interaction record.
- [ ] Cancelled authoritative Interactions clear the Runtime Job interaction projection rather than requiring a duplicate `cancelled` projection state.
- [ ] Professional artifacts are represented by exact versioned pointers.
- [ ] Collection-valued professional state uses semantic `ADD`, `REMOVE`, `REPLACE`, or `UPSERT_VERSION` mutations.
- [ ] Collection mutation commits are revision-checked and cannot silently overwrite concurrent valid members.
- [ ] Historical artifact contents are not duplicated in Runtime Job.
- [ ] Process Feedback remains outside `RuntimeJob.professional_state` and does not participate in routing.
- [ ] Information Request, Information Response, and Target Role are explicitly documented as deferred future state rather than silently omitted.
- [ ] V0.1 Runtime Job does not invent provisional current pointers for deferred Analyst/Custodian concepts.
- [ ] Handlers can resolve complete invocation bundles from current pointers.
- [ ] Current pointers are never cleared before replacement artifacts commit.
- [ ] Failed operations preserve the last valid professional state.
- [ ] Stale outputs cannot silently become current.
- [ ] JER current state can contain multiple versioned records.
- [ ] Each Runtime Job pins exact JER versions as a reproducible evidence snapshot.
- [ ] New reusable JER versions do not silently propagate into existing in-flight Jobs.
- [ ] Active ERQs are distinguishable from historical ERQs.
- [ ] Unintegrated Evidence Responses are distinguishable from historical responses.
- [ ] Resume and WCM current pointers remain coupled.
- [ ] Routing history is append-only.
- [ ] Routing decisions identify exact professional-artifact basis.
- [ ] Trello may mirror routing history without becoming authoritative.
- [ ] `create_job` is the sole normal runtime path for initial Runtime Job creation.
- [ ] New Runtime Jobs begin at revision 1 with an exact Target Job pointer and pinned initial JER snapshot.
- [ ] Retrying the same `create_job` Command cannot create a duplicate Runtime Job.
- [ ] Terminal lifecycle states cannot automatically reopen.
- [ ] Runtime Job contains no professional reasoning or agent-routing instructions.

---

# Next Design Step

The next V3 design artifact should define the **Artifact and Execution Commit Model**:

- Execution identity.
- Input snapshots.
- Idempotency keys.
- Output staging.
- Schema validation.
- Stale-input detection.
- Atomic pointer commits.
- Partial-failure handling.
- Retry behavior.
- Duplicate-event protection.