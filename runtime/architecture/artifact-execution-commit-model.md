# RRS V3 Artifact and Execution Commit Model

## Status

Draft V0.7 — FIX-005, FIX-006, FIX-010, FIX-011, FIX-012, and FIX-023 applied

## Purpose

This model defines how the V3 runtime safely turns one professional operation into committed new professional state.

It governs:

- Execution identity.
- Logical operation identity.
- Input snapshots.
- Idempotency.
- Output staging.
- Schema validation.
- Stale-input detection.
- Immutable artifact persistence.
- Atomic Runtime Job pointer commits.
- Multi-output product commits.
- Retry behavior.
- Partial failure handling.
- Duplicate event protection.
- Execution history.

The Runtime Job remains the source of current control-plane pointers.

Professional agents produce professional artifacts.

Handlers own execution, validation, persistence, and commit.

---

# Core Invariants

1. One physical execution attempt is identified separately from one logical professional operation.
2. Duplicate events must collapse onto the same logical operation when inputs and task identity are unchanged.
3. Agents never write directly to current Runtime Job pointers.
4. Agent output is staged before it becomes current professional state.
5. Staged output is not authoritative current state.
6. Professional output must validate against its authoritative schema before commit.
7. Execution inputs must still be current at commit time.
8. Stale output may be preserved historically but must not become current.
9. Current pointers advance only through an atomic commit.
10. Multi-output professional products commit as one logical unit when their semantics require coupling.
11. Failed attempts never clear or overwrite the last valid current pointers.
12. Retries must not duplicate successfully committed logical work.
13. Immutable artifact versions are never silently overwritten.
14. Execution records are append-only.
15. Routing occurs only after successful commit.
16. External integration failures after commit do not roll back professional state.
17. After immutable output files are finalized, artifact metadata, commit-group state, Runtime Job pointer mutations, Runtime Job revision, and Execution finalization commit atomically in one SQLite transaction.
18. The `artifact_committed` Event announcing a successful professional commit is persisted in that same SQLite transaction.
19. Every professional operation explicitly declares identity dependencies and freshness dependencies; retrieval fingerprints and materially relevant resources participate when they can change professional output.
20. At most one nonterminal active Execution may exist for a given `operation_key` at any time.
21. A Runtime Job compare-and-swap conflict never permits blind pointer overwrite; the runtime reloads current state and retries the same commit only when the Execution's declared freshness dependencies remain current.
22. Evidence integration may produce multiple JER versions in one logical operation; all required JER outputs and consumed Evidence Response mutations commit as one atomic commit group.

---

# 1. Execution Identity

The runtime distinguishes:

```text
execution_id
= one physical attempt

operation_key
= one logical professional operation
```

Example:

```text
Logical operation:
generate_analysis for JOB-0001 using current target + JER state

Attempt 1:
EXEC-0042
→ API timeout

Attempt 2:
EXEC-0043
→ success

Both attempts share the same operation_key.
```

This distinction is required for:

- Retry.
- Duplicate webhook suppression.
- Idempotency.
- Historical troubleshooting.
- Safe partial recovery.

---

# 2. Execution Record

Each physical attempt creates one immutable Execution record.

Example:

```yaml
execution:

  execution_id: EXEC-0042

  job_id: JOB-0001

  operation_type: generate_analysis

  operation_key: OPKEY-3f4a8c...

  attempt_number: 1

  status: running

  task_identity:
    agent_role: researcher
    task_name: generate_analysis
    task_version: "3.0"
    contract_version: "3.0"
    schema_versions:
      - artifact_type: job_experience_analysis
        schema_version: "2.0"

  input_snapshot:
    target_job:
      artifact_type: target_job
      artifact_id: TARGET-0001
      artifact_version: 1
      uri: artifacts/TARGET-0001/v1.yaml

    jer_set:
      - artifact_type: job_experience_record
        artifact_id: JER-0001
        artifact_version: 4
        uri: artifacts/JER-0001/v4.yaml

      - artifact_type: job_experience_record
        artifact_id: JER-0007
        artifact_version: 3
        uri: artifacts/JER-0007/v3.yaml

    product_feedback:
      - artifact_type: resume_evaluation
        artifact_id: EVAL-0003
        artifact_version: 2
        uri: artifacts/EVAL-0003/v2.yaml

  staged_outputs: []

  committed_outputs: []

  timestamps:
    created_at: ...
    started_at: ...
    completed_at: null

  failure: null
```

Execution records live outside the Runtime Job.

The Runtime Job references only the currently active execution:

```yaml
operation:
  execution_id: EXEC-0042
```

---

# 3. Execution Status

Recommended execution status vocabulary:

```text
created
queued
running
output_received
validating
validated
stale
committing
committed
failed
cancelled
```

Meaning:

### `created`

Execution record exists.

### `queued`

Execution is waiting for worker capacity or dispatch.

### `running`

Professional invocation is active.

### `output_received`

Agent returned output; no authoritative validation has completed.

### `validating`

Handler is parsing and validating staged outputs.

### `validated`

Outputs passed structural and professional output-contract validation.

### `stale`

Outputs are valid but input snapshot no longer matches current professional state.

### `committing`

Immutable persistence and pointer update are in progress.

### `committed`

Professional outputs became current successfully.

This status is written in the same SQLite transaction that records the commit group, final artifact metadata, Runtime Job current-state mutations, and Runtime Job revision increment.

### `failed`

Attempt terminated without a successful commit.

### `cancelled`

Attempt was explicitly cancelled before commit.

`committed`, `failed`, `stale`, and `cancelled` are terminal execution states.

---

# 4. Logical Operation Key

The `operation_key` identifies one logical unit of professional work.

It must be deterministic from the exact inputs and resources that can legitimately change the professional result.

Conceptually:

```text
operation_key =
hash(
    runtime_job_id
    +
    operation_type
    +
    identity_dependencies
    +
    retrieval_result_fingerprint
    +
    task_identity
    +
    contract_identity
    +
    material_resource_identity
)
```

`retrieval_result_fingerprint` is included only when retrieval is used.

Recommended identity fields:

```yaml
operation_identity:
  job_id: JOB-0001
  operation_type: generate_analysis
  task_identity: sha256(...)
  contract_identity: sha256(...)
  professional_input_fingerprint: sha256(...)
  retrieval_result_fingerprint: sha256(...) | null
  material_resource_fingerprint: sha256(...)
```

The exact serialized representation must be canonical so ordering differences do not produce different hashes.

Any changed dependency that can legitimately change professional output must produce a different `operation_key`.

Examples:

```text
same JEA + same Writer task + Evaluation v2
≠
same JEA + same Writer task + Evaluation v3
```

when Evaluation feedback is an authorized Writer input.

Likewise:

```text
same evidence query
+ changed retrieved source content
→ different retrieval_result_fingerprint
→ different operation_key
```

Provider/model configuration is invocation provenance. It participates in logical operation identity only if runtime policy explicitly treats provider/model changes as materially distinct professional inputs.

---

# 5. Input Fingerprint

The professional input fingerprint represents the exact professional state declared as an identity dependency for the logical operation.

Example:

```text
TARGET-0001:v1
JER-0001:v4
JER-0007:v3
EVAL-0003:v2
```

Canonicalize before hashing.

For unordered logical collections such as a JER set:

1. Sort by artifact type.
2. Sort by artifact ID.
3. Sort by artifact version.
4. Serialize deterministically.
5. Hash.

Example:

```text
sha256(
  "target_job|TARGET-0001|1
   job_experience_record|JER-0001|4
   job_experience_record|JER-0007|3
   resume_evaluation|EVAL-0003|2"
)
```

Artifact URI should generally not participate in professional input identity because URI may change without professional state changing.

Artifact ID + version is authoritative for professional artifacts.

When retrieval occurs, the normalized retrieval-result fingerprint is tracked separately and incorporated into the overall `operation_key`.

When static resources can materially change output, their exact resource identities are also incorporated into the overall `operation_key`.

---

# 6. Idempotency Rule

Before creating or dispatching a professional execution, the handler checks for an existing logical operation with the same `operation_key`.

Possible states:

```text
No existing operation
→ create new execution

Existing operation running
→ do not create duplicate work

Existing operation committed
→ return committed outputs

Existing operation failed
→ retry according to retry policy

Existing operation stale
→ recompute operation_key from current Runtime Job state

Existing operation cancelled
→ require explicit new invocation or policy decision
```

Duplicate webhook delivery therefore becomes:

```text
Webhook A
Webhook B
   │
   ▼
same Runtime Job
same operation
same current inputs
   │
   ▼
same operation_key
   │
   ▼
one logical professional operation
```


## 6.1 Active Execution Uniqueness

One logical professional operation may have multiple historical attempts, but only one nonterminal active attempt may exist at a time.

Canonical rule:

```text
one operation_key
→ zero or one nonterminal active Execution
```

Nonterminal active statuses include the statuses in which an attempt may still produce or commit output, such as:

```text
queued
running
validating
committing
```

Terminal statuses include:

```text
committed
failed
stale
cancelled
```

or the exact equivalent vocabulary defined by the Execution model.

When scheduling professional work:

```text
same operation_key + committed Execution
→ reuse existing committed result

same operation_key + active nonterminal Execution
→ do not create another Execution
→ return/reference the existing active logical operation

same operation_key + terminal failed/stale attempt
→ retry policy may create a new Execution attempt
```

Retries therefore occur sequentially:

```text
OPKEY-A
├── EXEC-001 attempt 1 → failed
├── EXEC-002 attempt 2 → failed
└── EXEC-003 attempt 3 → committed
```

not concurrently:

```text
OPKEY-A
├── EXEC-001 running
└── EXEC-002 running
```

The runtime must enforce active-attempt uniqueness transactionally when creating an Execution.

Application logic may enforce this rule, and SQLite may additionally use an index/constraint strategy where practical.

A duplicate scheduling request for an already-active `operation_key` is idempotent and must not create duplicate professional provider calls.

---

# 7. Attempt Number

Retries of the same logical operation increment:

```yaml
attempt_number: 1
attempt_number: 2
attempt_number: 3
```

Each attempt receives a new:

```text
execution_id
```

but retains the same:

```text
operation_key
```

Example:

```text
OPKEY-ABC
├── EXEC-0042 attempt 1 → timeout
├── EXEC-0043 attempt 2 → invalid schema
└── EXEC-0044 attempt 3 → committed
```

After `EXEC-0044` commits, further duplicate requests for `OPKEY-ABC` return its committed result rather than generating another artifact.

---

# 8. Invocation Input Resolver

Handlers do not pass the Runtime Job object directly to professional agents.

Each operation has a resolver.

Examples:

```text
resolve_generate_analysis_inputs(job)

resolve_request_evidence_inputs(job, evidence_need)

resolve_investigation_inputs(job, erq)

resolve_integrate_evidence_inputs(job)

resolve_generate_resume_inputs(job)

resolve_evaluate_resume_inputs(job)
```

Each operation specification declares:

```yaml
required_inputs: [...]
optional_inputs: [...]
identity_dependencies: [...]
freshness_dependencies: [...]
required_resources: [...]
expected_outputs: [...]
```

Definitions:
- `identity_dependencies` — exact professional inputs/resources whose changed identity or content requires a new logical operation.
- `freshness_dependencies` — exact current state that must still match before returned output may become current.
- `required_inputs` — inputs that must exist to invoke the operation.
- `optional_inputs` — authorized inputs included when present.
- `required_resources` — contracts, tasks, schemas, templates, or other static resources required by the operation.
- `expected_outputs` — professional artifacts required for successful completion.

For most V0.1 professional operations:

```text
identity_dependencies == freshness_dependencies
```

unless a documented reason requires otherwise.

A resolver:

1. Reads current Runtime Job pointers.
2. Loads exact professional artifact versions.
3. Performs authorized retrieval when the operation permits it.
4. Loads applicable contracts/tasks/schemas/resources.
5. Resolves exact identity and freshness dependency sets.
6. Produces the complete Invocation Bundle.
7. Produces the canonical fingerprints used for idempotency and stale checks.

This keeps the Runtime Job small while making professional operation identity explicit and reproducible.

---

# 9. Input Snapshot

Every Execution stores the exact dependency state actually supplied to the professional operation.

Example:

```yaml
input_snapshot:
  professional_inputs:
    target_job:
      artifact_id: TARGET-0001
      artifact_version: 1

    jea:
      artifact_id: JEA-0004
      artifact_version: 3

    product_feedback:
      - artifact_id: EVAL-0003
        artifact_version: 2

  identity_dependencies:
    - TARGET-0001:v1
    - JEA-0004:v3
    - EVAL-0003:v2

  freshness_dependencies:
    - TARGET-0001:v1
    - JEA-0004:v3
    - EVAL-0003:v2

  retrieval_result_fingerprint: null

  resources:
    contract_identity: sha256(...)
    task_identity: sha256(...)
    material_resource_fingerprint: sha256(...)
```

The snapshot is immutable after execution starts.

The handler must not silently substitute newer artifacts, retrieval results, or resources into an active Execution.

---

# 10. Task Identity

The same professional inputs processed by a materially different task definition are not necessarily the same logical operation.

Therefore the operation key should include task identity.

At minimum:

```yaml
task_identity:
  agent_role: writer
  task_name: generate_resume
  task_version: "3.0"
  contract_version: "3.0"
```

Schema identity should also be recorded.

Whether schema version participates directly in the operation key should be determined by compatibility rules.

Recommended V0.1 rule:

> If a schema change can change valid output semantics, it participates in the logical operation identity.

---

# 11. Output Staging

Professional outputs do not immediately enter the immutable artifact store as current artifacts.

They first enter an execution staging state.

Example:

```yaml
staged_outputs:

  - staged_output_id: STAGE-0081

    artifact_type: job_experience_analysis

    proposed_artifact_id: JEA-0004

    proposed_artifact_version: 4

    temporary_uri: staging/EXEC-0042/JEA.yaml

    received_at: ...

    validation_status: pending
```

Staging may be implemented through:

- Temporary filesystem.
- Temporary database record.
- Object-store staging path.
- Another transactional storage mechanism.

Implementation choice is separate from logical semantics.

---

# 12. Staged Output Rules

Staged outputs:

- Are not current professional state.
- Must not update Runtime Job professional pointers.
- May be inspected for diagnostics.
- May be discarded after failed validation.
- May be retained temporarily for debugging according to retention policy.
- Must not be exposed as authoritative artifacts to downstream handlers.

---

# 13. Output Parsing

Before schema validation, handlers must identify required artifacts from the professional response.

Examples:

### `generate_analysis`

Required output:

```text
Job Experience Analysis
```

### `request_evidence`

Required output:

```text
one Evidence Request per invoked coherent evidence need
```

### `investigate_evidence_request`

Required output:

```text
Evidence Response
```

### `generate_resume`

Required coupled outputs:

```text
Targeted Resume
Writer Content Manifest
```

### `evaluate_resume`

Required output:

```text
Resume Evaluation
```

Missing required output is an execution failure.

---

# 14. Schema Validation

Every structured professional artifact must validate against its authoritative schema before commit.

Validation sequence:

```text
Parse
 ↓
Artifact type check
 ↓
Schema resolution
 ↓
Schema validation
 ↓
Cross-output validation
 ↓
Professional commit eligibility
```

Examples of cross-output validation:

- Resume + WCM must refer to the same product state.
- Evidence Response must reference the exact ERQ version consumed.
- Resume Evaluation must reference the exact Resume + WCM evaluated.

Schema-valid does not automatically mean commit-valid.

---

# 15. Validation Result

Each staged output records:

```yaml
validation:
  schema_status: passed
  schema_id: ...
  schema_version: ...
  cross_output_status: passed
  errors: []
  validated_at: ...
```

On failure:

```yaml
validation:
  schema_status: failed
  errors:
    - path: ...
      message: ...
```

The Execution moves to:

```text
failed
```

or retry policy may create a new attempt.

Current Runtime Job pointers remain unchanged.

---

# 16. Stale Input Detection

After outputs validate but before commit, the handler compares the Execution's declared `freshness_dependencies` against current authoritative state.

Do not use Runtime Job revision alone as the professional freshness test.

Example:

Execution consumed:

```text
JEA-0004 v3
```

and declared that JEA reference as a freshness dependency.

Current Runtime Job now points to:

```text
JEA-0004 v4
```

Result:

```text
Execution is stale.
```

By contrast, an unrelated Runtime Job mutation may increment `revision` without changing any declared professional freshness dependency. That alone does not make the Execution stale.

The Execution becomes:

```text
stale
```

Validated outputs may be persisted as noncurrent historical artifacts only if policy finds that useful.

They must not advance current pointers.

---

# 17. Freshness Scope

Freshness validation considers only the exact dependencies declared by that operation.

Example:

`generate_resume` may depend on:

```text
Target Job
Current JEA
Applicable Resume Evaluation feedback
Resume Skeleton version
Prompt Bank version
```

A new unrelated Process Feedback artifact should not make the Writer Execution stale.

When retrieval is a freshness dependency, the exact retrieval-result fingerprint must still represent the authorized professional input state expected by the operation.

Each handler therefore uses the operation specification's `freshness_dependencies` rather than comparing every Runtime Job field.

---

# 18. Pre-Commit Check

Before commit:

```text
1. Required outputs exist?
2. Outputs validate?
3. Declared freshness dependencies still equal current authoritative state?
4. Runtime Job revision available for compare-and-swap?
```

If professional freshness fails:

```text
Execution
→ stale
```

If professional freshness passes, the commit attempts its authorized Runtime Job mutation using the expected Runtime Job revision.

A Runtime Job revision mismatch is a concurrency conflict, not automatically a stale professional result.

The conflict is resolved according to the pointer-commit conflict procedure below.

---

# 19. Immutable Artifact Persistence

Validated outputs are persisted as immutable professional artifact versions.

Example:

```text
artifacts/
└── JEA-0004/
    ├── v1.yaml
    ├── v2.yaml
    ├── v3.yaml
    └── v4.yaml
```

Existing artifact versions are never overwritten.

Attempting to write an already-existing artifact ID/version with different content is a conflict.

---

# 20. Artifact Version Assignment

V0.1 should centralize artifact version assignment in the handler/runtime rather than allowing freeform agent decisions to become authoritative.

Recommended flow:

```text
current artifact = JEA-0004 v3

handler reserves:
JEA-0004 v4

professional operation returns artifact content

handler verifies/normalizes expected identity

handler persists:
JEA-0004 v4
```

If professional schema requires ID/version fields, the invocation may provide expected output identity or the handler may verify the returned identity against the reservation.

Exact mechanism belongs in handler design.

---

# 21. New Artifact vs New Version

Handlers must know whether an operation creates:

```text
new artifact identity
```

or:

```text
new version of an existing artifact
```

Examples:

### New JEA generation for an existing target/job analysis

Likely:

```text
same JEA ID
new version
```

### New ERQ for a distinct Material Evidence Need

Likely:

```text
new ERQ ID
version 1
```

### Re-issued/updated ERQ

Potentially:

```text
same ERQ ID
new version
```

### New Resume generation

Architecture must define whether resumes use:
- same Resume ID with new versions, or
- new Resume ID per materially different product lineage.

V3 handlers must follow V2 artifact semantics rather than inventing them dynamically.

---

# 21.1 Pointer-Commit Conflict Resolution

Runtime Job pointer and collection mutations use optimistic compare-and-swap semantics.

If the professional commit loses the Runtime Job revision race:

```text
CAS conflict
→ do not overwrite
→ reload current Runtime Job
→ re-resolve declared freshness dependencies
```

Then:

```text
freshness dependencies unchanged
→ Execution remains professionally valid
→ recompute authorized mutation against current Runtime Job state
→ retry the same commit with the new expected revision
```

or:

```text
freshness dependencies changed
→ Execution is stale
→ do not advance current professional pointers
```

Example of a retryable conflict:

```text
Writer Execution consumes JEA v4.

While Writer runs:
Runtime Job interaction.last_activity_at changes.
Runtime Job revision increments.

Writer commit sees revision conflict.

Current JEA is still v4.
All Writer freshness dependencies still match.

→ retry same professional commit against current revision
```

Example of a stale conflict:

```text
Writer Execution consumes JEA v4.

While Writer runs:
Researcher commits JEA v5.
Runtime Job revision increments.

Writer commit sees revision conflict.

Current JEA is now v5.

→ mark Writer Execution stale
→ do not commit its Resume/WCM as current
```

A retry must preserve the original professional output and Execution identity. It is a retry of the commit transaction, not a new professional invocation.

For semantic collection mutations, the runtime reapplies the authorized `ADD`, `REMOVE`, `UPSERT_VERSION`, or `REPLACE` operation against the reloaded current collection rather than replaying a stale full-collection snapshot.

The implementation may impose a bounded number of commit retries. Exhaustion becomes a recoverable runtime failure; it must never fall back to blind overwrite.

---

# 22. Atomic Professional Commit

A successful professional commit has two durability stages:

```text
Stage 1 — filesystem
Persist and verify all required immutable output files.

Stage 2 — SQLite
Atomically commit runtime metadata and current-state changes.
```

After all required immutable output files are safely finalized, one SQLite transaction must commit:

```text
artifact runtime metadata for every output
+
commit-group record/state
+
all authorized Runtime Job pointer or collection mutations
+
Runtime Job revision increment
+
Execution committed_outputs
+
Execution terminal status = committed
+
artifact_committed Event
```

These SQLite changes must not be split across independent successful transactions.

Example for Writer:

```text
Filesystem:
  persist RESUME-0003 v4
  persist WCM-0003 v4
  verify both

SQLite transaction:
  insert/finalize metadata for RESUME-0003 v4
  insert/finalize metadata for WCM-0003 v4
  record COMMIT-0093
  update Runtime Job:
    resume → RESUME-0003 v4
    wcm    → WCM-0003 v4
  increment Runtime Job revision
  record both outputs in Execution
  mark Execution committed
```

The Runtime Job must never expose:

```text
resume → v4
wcm → v3
```

for a coupled product commit.

If the SQLite transaction fails, the previous Runtime Job pointers and Execution committed state remain unchanged, and no `artifact_committed` Event exists.

Successfully finalized immutable files may remain noncurrent and are reconciled according to orphan/stale output rules.

This prevents the failure mode:

```text
professional state commits
→ process crashes
→ routing-trigger Event is never persisted
```

A successful professional commit and the Event announcing that commit are therefore durably inseparable in SQLite.


---

# 23. Coupled Product Commit

Some operations produce semantically coupled outputs.

Current known case:

```text
generate_resume
→ Targeted Resume
→ Writer Content Manifest
```

These outputs form one commit group.

Commit rule:

> Either the entire output group becomes current, or none of it does.

If Resume persistence succeeds but WCM persistence fails:

```text
Runtime Job pointers remain on prior Resume + WCM pair.
```

The new Resume artifact may require rollback, quarantine, or noncurrent historical retention depending on persistence capabilities.

---

# 24. Commit Group

Execution records should represent commit groups:

```yaml
commit_group:
  group_id: COMMIT-0093

  outputs:
    - RESUME-0003:v4
    - WCM-0003:v4

  pointer_mutations:
    - professional_state.resume
    - professional_state.wcm

  status: committed
```

For single-output operations, the commit group contains one artifact.

Exactly one `artifact_committed` Event is persisted per successful commit group, whether the group contains one artifact or multiple coupled outputs.

The commit-group record is part of the same SQLite transaction that makes its outputs current and marks the Execution committed.

A commit group must never be recorded as `committed` while only part of its Runtime Job mutations or Execution finalization succeeded.

## Multi-JER Evidence Integration

One evidence-integration Execution may update multiple reusable Job Experience Records.

Example:

```text
Inputs:
  ERESP-0011 v1
  ERESP-0012 v1

Outputs:
  JER-0004 v6
  JER-0007 v4
  JER-0012 v2
```

All changed JERs belong to one logical commit group. The group atomically performs:

```text
finalize all changed JER versions
+
UPSERT_VERSION each affected JER in RuntimeJob.jer_set
+
REMOVE each Evidence Response successfully consumed by the integration
from RuntimeJob.unintegrated_evidence_responses
+
increment Runtime Job revision once
+
finalize the Execution
+
persist one artifact_committed Event
```

The Runtime Job must never expose a partial integration result.

If any required JER output fails validation, persistence, or transactional commit:

```text
no new JER version becomes current
AND
no corresponding Evidence Response is removed
```

An Evidence Response may be removed only when every professional output required to integrate that response commits successfully.

Unchanged JERs are not rewritten merely to participate in the commit group.

---

# 25. Runtime Job Concurrency Control

Pointer commit must be protected from concurrent mutation.

Recommended semantic mechanism:

```text
optimistic concurrency
```

The handler records a Runtime Job revision when execution begins.

Example:

```yaml
job_revision_at_start: 27
```

At commit:

```text
expected relevant pointer state still matches?
AND
job revision / dependency state compatible?
```

If not, commit fails as stale/conflicting.

Exact implementation may use:
- Database compare-and-swap.
- Transaction version column.
- File lock plus revision.
- Another atomic concurrency mechanism.

---

# 26. Job Revision

Recommended addition to Runtime Job identity:

```yaml
identity:
  job_id: JOB-0001
  revision: 28
  created_at: ...
  updated_at: ...
```

Every successful Runtime Job mutation increments:

```text
revision
```

This supports:
- Optimistic locking.
- Conflict detection.
- Reliable integration synchronization.

Professional freshness should still compare exact artifact dependencies, not blindly invalidate on any unrelated Runtime Job revision change.

---

# 27. Commit Sequence

Recommended logical commit sequence:

```text
BEGIN PROFESSIONAL COMMIT

1. Recheck declared professional freshness dependencies.
2. Load the expected Runtime Job revision.
3. Reserve/finalize required artifact versions.
4. Persist all immutable output files.
5. Verify persisted output integrity.

6. BEGIN SQLITE TRANSACTION
   a. Insert/finalize artifact runtime metadata.
   b. Record the commit group.
   c. Apply all authorized Runtime Job pointer/collection mutations using expected revision CAS.
   d. Increment Runtime Job revision.
   e. Record Execution committed_outputs.
   f. Mark Execution status = committed.
   g. Persist one `artifact_committed` Event for the successful commit group.
7. COMMIT SQLITE TRANSACTION

END PROFESSIONAL COMMIT
```

If the SQLite transaction fails because the Runtime Job compare-and-swap condition did not match:

```text
reload Runtime Job
→ reevaluate declared freshness dependencies
→ retry commit only if still fresh
→ otherwise mark Execution stale
```

For any other SQLite transaction failure:

```text
Runtime Job current state remains unchanged
Execution does not become committed
commit group does not become committed
```

Any already-finalized immutable files remain noncurrent until recovery classifies or reconciles them.

Routing occurs only after the successful SQLite professional commit.


---

# 28. Routing After Commit

A successful professional commit persists its `artifact_committed` Event before the SQLite transaction completes. Downstream routing may therefore consume that durable Event after commit without risking a lost transition trigger.

Routing predicates must only evaluate successfully committed current professional state.

Never route based on:

- Raw agent output.
- Staged artifact.
- Schema-invalid artifact.
- Stale artifact.
- Partially committed coupled product.

Sequence:

```text
commit
 ↓
Runtime Job now references new professional state
 ↓
router reads current state
 ↓
routing decision
 ↓
append routing_history
 ↓
lifecycle transition
 ↓
project to Trello
```

---

# 29. Partial Failure Classes

The runtime must distinguish partial failure location.

Recommended classes:

```text
invocation_failure
output_parse_failure
schema_validation_failure
cross_output_validation_failure
stale_input
artifact_persistence_failure
pointer_commit_conflict
runtime_job_persistence_failure
post_commit_projection_failure
unknown_failure
```

These drive retry policy.

---

# 30. Failure Before Commit

Examples:

- API timeout.
- Agent output missing.
- Schema validation failure.
- Stale input.
- Artifact staging failure.

Rule:

> Last valid Runtime Job professional pointers remain unchanged.

No professional rollback is necessary because no current commit occurred.

---

# 31. Failure During Persistence

Example:

```text
Resume persisted
WCM persistence failed
Runtime Job pointers not updated
```

The commit group is incomplete.

The Execution must record:

```text
artifact_persistence_failure
```

The runtime must ensure incomplete outputs cannot be treated as current.

Implementation options:
- Delete incomplete persisted artifacts if safe.
- Mark them orphaned/noncurrent.
- Retry missing persistence.
- Re-run commit transaction.

The logical rule is more important than storage mechanism:

> Partial persistence does not equal successful commit.

---

# 32. Failure After Pointer Commit

Example:

```text
Professional commit succeeded
Execution status update failed
```

This is dangerous because professional state may already be current.

Recovery must inspect actual Runtime Job pointer state and artifact persistence before retrying.

The retry must detect:

```text
logical operation already committed
```

and repair the Execution record rather than invoke the professional operation again.

---

# 33. Post-Commit Integration Failure

Example:

```text
Evaluation committed successfully
Routing committed successfully
Trello comment failed
```

Professional state remains valid.

Runtime health may become:

```text
degraded
```

Integration synchronization retries separately.

Do not roll back professional commits because Trello or Discord projection failed.

---

# 34. Retry Policy

Retry operates at the Execution attempt level.

Same logical inputs + same task identity:

```text
same operation_key
```

New retry:

```text
new execution_id
attempt_number + 1
```

Retry policy may vary by failure class.

Suggested V0.1 behavior:

```text
invocation_failure
→ automatic retry

output_parse_failure
→ limited automatic retry

schema_validation_failure
→ limited automatic retry

cross_output_validation_failure
→ limited automatic retry

stale_input
→ no retry of same operation_key
→ derive new operation from current state

artifact_persistence_failure
→ retry commit/persistence when safe

pointer_commit_conflict
→ recompute from current state

runtime_job_persistence_failure
→ reconcile before any professional re-invocation

post_commit_projection_failure
→ integration-only retry

unknown_failure
→ limited retry, then manual review
```

---

# 35. Retry Threshold

A retry may create a new Execution only after the prior attempt for the same `operation_key` is terminal.

The new `attempt_number` is allocated transactionally from the existing attempts for that `operation_key` so concurrent retry requests cannot create duplicate attempt numbers or simultaneous active attempts.

Retry limits should be configuration, not professional logic.

Example:

```yaml
retry_policy:
  invocation_failure: 3
  schema_validation_failure: 2
  artifact_persistence_failure: 3
  unknown_failure: 1
```

After configured retries are exhausted:

```text
health.status → blocked
lifecycle.phase → manual_review
```

where appropriate.

---

# 36. Duplicate Event Protection

Each inbound event should have its own event identity.

Example:

```yaml
runtime_event:
  event_id: EVT-0081
  provider: trello
  provider_event_id: abc123
  received_at: ...
```

Before processing:

```text
provider + provider_event_id already processed?
```

If yes:

```text
acknowledge / ignore duplicate
```

Even if event deduplication fails, operation-level idempotency remains the second protection layer.

Defense in depth:

```text
event deduplication
+
operation_key idempotency
+
atomic pointer commit
```

---

# 37. Execution Locking

Only one active execution for the same `operation_key` should run unless explicit parallelism is supported.

If two workers receive the same logical operation:

```text
Worker A → acquires logical operation lock
Worker B → sees active operation
```

Worker B must not start duplicate professional work.

Exact lock implementation may vary.

---

# 38. Parallel Operations

V0.1 should minimize parallel professional operations on one Runtime Job.

Recommended rule:

> Only one pointer-mutating professional execution may commit at a time per Runtime Job.

Some future non-mutating activities may run concurrently.

This simplifies:
- Stale detection.
- Pointer consistency.
- Human debugging.
- Retry behavior.

---

# 39. Multi-ERQ Operations

If multiple Material Evidence Needs exist, `request_evidence` may be invoked independently for each coherent need.

Each should receive its own logical operation key.

Example:

```text
EN-001
→ OPKEY-A
→ ERQ-0011

EN-002
→ OPKEY-B
→ ERQ-0012
```

The Runtime Job's:

```yaml
active_erqs:
```

is updated through commits for each successfully created ERQ.

If parallel ERQ generation is later supported, pointer mutation must merge safely rather than replace the whole collection blindly.

V0.1 may serialize these commits.

---

# 40. Investigation Execution Identity

Each Evidence Request investigation should be logically tied to the exact ERQ version.

Example:

```text
operation_type:
investigate_evidence_request

inputs:
ERQ-0011 v1

operation_key:
hash(JOB + ERQ-0011:v1 + task identity)
```

If ERQ-0011 becomes v2 before investigation completes, v1 output becomes stale.

---

# 41. Evidence Integration Identity

Evidence integration should fingerprint:

- Current JER state affected by the integration.
- Unintegrated Evidence Responses being reconciled.
- Professional reconciliation task identity.

Example:

```text
JER-0007:v3
+
ERESP-0008:v1
+
integration task version
```

If JER-0007 changes before commit, integration must re-evaluate against current professional state.

---

# 42. Resume Generation Identity

`generate_resume` should fingerprint all professional and presentation state material to its output.

At minimum:

- Target Job.
- Current JEA.
- Resume Skeleton version/content identity.
- Prompt Bank version/content identity.
- Applicable Resume Evaluation/product feedback.
- Writer contract/task identity.

This prevents reuse of a resume generated from an outdated skeleton or JEA.

---

# 43. Resume / WCM Coupled Commit

Writer output must pass:

```text
Resume present
WCM present
WCM schema valid
WCM references exact Resume product
Resume identity expected
WCM identity expected
Input freshness valid
```

Only then:

```text
resume pointer + wcm pointer
```

advance atomically.

---

# 44. Evaluation Identity

`evaluate_resume` should fingerprint:

- Target Job.
- Current Resume.
- Corresponding WCM.
- Applicable evaluation context.
- Evaluator task/contract identity.

A Resume Evaluation must not commit if Resume or WCM changed during execution.

---

# 45. Commit Provenance

Every committed artifact should be traceable to the Execution that committed it.

The artifact itself does not necessarily need runtime fields.

The artifact store metadata should preserve:

```yaml
artifact_runtime_metadata:
  artifact_id: JEA-0004
  artifact_version: 4
  committed_by_execution_id: EXEC-0044
  operation_key: OPKEY-ABC
  committed_at: ...
```

This keeps runtime provenance out of professional artifact schemas.

---

# 46. Execution History

Execution records are append-only.

The system should support questions such as:

```text
Which inputs produced Resume v4?

Which execution committed JEA v6?

How many retries occurred?

Why was EXEC-0042 rejected as stale?

Which operation generated ERQ-0011?
```

No professional artifact mutation is required to answer these.

---

# 47. Commit Recovery

On service restart, the runtime should reconcile incomplete Executions.

Examples:

### Execution says `committing`

Check:

```text
Did artifacts persist?
Did Runtime Job pointers advance?
```

Possible recovery:

```text
neither happened
→ retry commit

artifacts persisted, pointers not advanced
→ finish pointer commit if still fresh

pointers advanced
→ mark execution committed

conflicting newer state exists
→ preserve outputs as noncurrent and mark stale/conflicted
```

This is required for crash-safe operation.

---

# 48. Orphaned Artifacts

An artifact may exist in storage but not be current because:

- Commit failed.
- Output became stale.
- Coupled commit only partially persisted.
- Recovery preserved diagnostic output.

Such artifacts should have runtime metadata marking:

```text
current: false
commit_status: orphaned | stale | superseded | diagnostic
```

This metadata belongs to artifact storage/runtime indexing, not the professional artifact body.

---

# 49. Content Hash

Persisted professional artifacts should have a content hash.

Example:

```yaml
storage_metadata:
  sha256: ...
```

Uses:
- Detect accidental mutation.
- Verify persistence integrity.
- Detect same-version content conflicts.
- Support diagnostics.

Historical artifact content should be immutable after commit.

---

# 50. Successful Logical Operation

A logical operation is successful when one Execution with its `operation_key` reaches:

```text
committed
```

After that:

- Duplicate events return/reuse committed outputs.
- New physical attempts are not created.
- Routing may proceed from current state.

A new operation requires changed professional input state or task identity.

---

# 51. Commit Model Example — Generate Analysis

```text
Runtime Job
JER set current
Target current
      │
      ▼
resolve inputs
      │
      ▼
compute OPKEY-A
      │
      ▼
EXEC-0101
      │
      ▼
Researcher generate_analysis
      │
      ▼
stage JEA-0004 v5
      │
      ▼
validate JEA schema
      │
      ▼
compare current Target/JER set
      │
      ▼
persist JEA-0004 v5
      │
      ▼
atomically:
professional_state.jea → JEA-0004 v5
      │
      ▼
EXEC-0101 committed
      │
      ▼
evaluate routing
```

---

# 52. Commit Model Example — Generate Resume

```text
Current:
JEA v5
Resume v3
WCM v3
      │
      ▼
resolve Writer inputs
      │
      ▼
compute OPKEY-B
      │
      ▼
EXEC-0102
      │
      ▼
Writer
      │
      ├── Resume v4
      └── WCM v4
      │
      ▼
stage both
      │
      ▼
validate WCM + coupled consistency
      │
      ▼
freshness check
      │
      ▼
persist both
      │
      ▼
atomic pointer commit:
resume → v4
wcm → v4
      │
      ▼
EXEC committed
```

---

# 53. Commit Model Example — Stale Writer Output

```text
Writer starts with JEA v5
      │
      ▼
EXEC-0102 running

Researcher commits JEA v6
      │
      ▼
Writer returns Resume/WCM
      │
      ▼
schema validation passes
      │
      ▼
freshness check:
snapshot JEA v5
current JEA v6
      │
      ▼
STALE
```

Result:

```text
Resume/WCM do not become current.
Current Resume/WCM remain unchanged.
New Writer operation derives from JEA v6.
```

---

# 54. Commit Model Example — Duplicate Trello Webhook

```text
Webhook A
Webhook B
      │
      ▼
both request evaluation
      │
      ▼
same Resume/WCM/current task
      │
      ▼
same operation_key
      │
      ├── A starts EXEC-0201
      │
      └── B observes active OPKEY
             ↓
          no duplicate invocation
```

After commit, any further duplicate returns the committed Evaluation reference.

---

# 55. Commit Model Example — Post-Commit Trello Failure

```text
Evaluation committed
      │
      ▼
Routing decision committed
      │
      ▼
Trello comment POST
      │
      ▼
failure
```

Result:

```text
Professional state remains committed.
Routing remains committed.
Runtime health → degraded.
Trello sync retries independently.
```

---

# 55.1 Commit Model Example — Multi-JER Evidence Integration

```text
Evidence Responses committed
      │
      ▼
Integrate evidence
      │
      ├── JER-0004 v6
      ├── JER-0007 v4
      └── JER-0012 v2
      │
      ▼
validate all required JER outputs
      │
      ▼
atomic commit group:
  UPSERT all three JER pointers
  REMOVE consumed Evidence Responses
  revision +1
  Execution → committed
  artifact_committed Event
```

Failure of any required output leaves the prior JER snapshot and unintegrated Evidence Response collection unchanged.

---

# 56. V0.1 Acceptance Criteria

The Artifact and Execution Commit Model is acceptable when:

- [ ] Physical attempts and logical operations have separate identities.
- [ ] Operation keys are deterministic from declared identity dependencies and materially relevant resource identity.
- [ ] Every professional operation explicitly declares `identity_dependencies` and `freshness_dependencies`.
- [ ] Retrieval-result fingerprints participate in operation identity when retrieval is used.
- [ ] Material contract/task/schema/template identity participates when it can change professional output.
- [ ] Runtime Job revision alone is never used as the professional freshness test.
- [ ] Runtime Job CAS conflicts never cause blind pointer overwrite.
- [ ] A CAS-conflicted commit retries only when the Execution's declared freshness dependencies still match current authoritative state.
- [ ] Changed freshness dependencies mark the Execution stale instead of retrying the professional commit.
- [ ] Input snapshots are immutable.
- [ ] Duplicate events collapse onto existing logical operations.
- [ ] Retries create new execution IDs but preserve operation keys.
- [ ] Agent output is staged before commit.
- [ ] Structured outputs validate before commit.
- [ ] Coupled outputs validate together.
- [ ] Multi-JER evidence integration commits all changed JER versions and consumed Evidence Response mutations atomically.
- [ ] Failed multi-JER integration cannot advance only a subset of affected JER pointers or consume Evidence Responses prematurely.
- [ ] Freshness is checked after validation and before commit.
- [ ] Stale outputs cannot become current.
- [ ] Professional artifacts persist immutably.
- [ ] Finalized artifact metadata, commit-group state, Runtime Job mutations, Runtime Job revision, Execution finalization, and the `artifact_committed` Event commit in one SQLite transaction.
- [ ] Exactly one `artifact_committed` Event is persisted per successful professional commit group.
- [ ] Current Runtime Job pointers update atomically.
- [ ] Resume + WCM commit together.
- [ ] Failed attempts preserve last valid pointers.
- [ ] Partial persistence cannot masquerade as successful commit.
- [ ] Post-commit integration failures do not roll back professional state.
- [ ] Runtime Job concurrency is protected.
- [ ] Execution history is append-only.
- [ ] Committed artifacts are traceable to their committing Execution.
- [ ] Crash recovery can reconcile partially completed commits.
- [ ] Routing occurs only after successful current-state commit.

---

# Next Design Step

After this model is accepted, define the:

> **V3 Routing Model**

The Routing Model should specify:

- Exact predicates.
- Predicate inputs.
- Phase transitions.
- Priority when multiple predicates are true.
- Blocking vs nonblocking evaluation behavior.
- ERQ fan-out and investigation completion conditions.
- Evidence integration return paths.
- Product Defect loops.
- Evidence Uncertainty loops.
- Completion conditions.
- Manual Review transitions.