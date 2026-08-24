# RRS V3 Transaction Matrix

## Status

Implementation Planning — Phase 4

## Purpose

This document defines the authoritative transaction boundaries required by the frozen RRS V3 architecture.

It translates architecture statements such as:

```text
these mutations must commit atomically
```

into explicit implementation contracts.

This document defines:

- transaction purpose,
- required reads,
- required writes,
- optimistic concurrency expectations,
- filesystem boundaries,
- event/command coupling,
- failure behavior,
- retry/recovery behavior,
- idempotency expectations.

It does **not** define final repository method names or production SQL syntax. Those belong to the package/interface and implementation phases.

The design goal is:

```text
architecture invariant
→ transaction contract
→ repository/unit-of-work implementation
→ crash/recovery test
```

---

# 1. Transaction Rules

The following rules apply to all authoritative V0.1 transactions.

1. All SQLite-local state that represents one authoritative runtime fact must commit together.
2. A transaction must not expose partial current professional state.
3. Runtime Job authoritative mutations use revision/CAS semantics unless the transaction creates the Job.
4. Filesystem artifact content is outside SQLite ACID.
5. Filesystem artifact finalization therefore occurs before authoritative SQLite professional commit.
6. Orphaned immutable files are tolerable.
7. Current Runtime Job pointers to missing or incompletely finalized files are not tolerable.
8. Event processing that produces durable Commands commits the Commands and Event processing state together.
9. `artifact_committed` is persisted inside the professional commit transaction.
10. `execution_committed` is telemetry/audit only and is not a routing trigger.
11. Human-message consumption for a completed Evidence Response commits with the Evidence Response.
12. Interaction completion is separate from Evidence Response professional commit.
13. Routing-history append, lifecycle mutation, Runtime Job revision, and `lifecycle_changed` Event commit together.
14. Failure records persist after resolution.
15. External provider effects cannot join SQLite transactions and require durable intent/reconciliation where ambiguity is possible.
16. Every transaction must have a deterministic recovery interpretation after process interruption.

---

# 2. Transaction Categories

V0.1 transactions fall into five categories:

```text
A. Runtime control-plane transactions
B. Professional commit transactions
C. Interaction transactions
D. Failure/recovery transactions
E. External-side-effect coordination transactions
```

---

# 3. Summary Matrix

| ID | Transaction | Primary Owner | SQLite Atomic | Filesystem Before TX | External Side Effect |
|---|---|---|---|---|---|
| TX-001 | Create Job | `create_job` Command handler | Yes | Target Job finalize | No |
| TX-002 | Claim Command | Command processor | Yes | No | No |
| TX-003 | Complete SQLite-local Command | Command handler | Yes | No | No |
| TX-004 | Claim Event | Event processor | Yes | No | No |
| TX-005 | Event → Command | Event processor | Yes | No | No |
| TX-006 | Create/Reuse Execution for schedule_operation | schedule_operation handler | Yes | No | No |
| TX-007 | Begin Execution | Execution worker | Yes | No | Provider call follows |
| TX-008 | Professional Single-Output Commit | Commit Coordinator | Yes | Yes | No |
| TX-009 | Coupled Resume/WCM Commit | Commit Coordinator | Yes | Yes | No |
| TX-010 | Evidence Integration Commit | Commit Coordinator | Yes | Yes | No |
| TX-011 | Completed Evidence Response Commit | Commit Coordinator | Yes | Yes | No |
| TX-012 | Routing Transition | Router | Yes | No | No |
| TX-013 | Routing No-Op Completion | Router | Yes | No | No |
| TX-014 | Inbound Human Message Persistence | Discord adapter/runtime | Yes | No | Inbound already happened |
| TX-015 | Conversational Interviewer Continuation | Interaction processor | Yes | No | Discord send follows |
| TX-016 | Complete Interaction | complete_interaction handler | Yes | No | Optional Discord projection follows |
| TX-017 | Pause/Resume Interaction Projection | Interaction runtime | Yes | No | Optional provider action |
| TX-018 | Material Failure Transition | failure/runtime service | Yes | No | No |
| TX-019 | Resolve Failure / Recompute Health | recovery/control service | Yes | No | No |
| TX-020 | Cancel Job | cancel_job handler | Yes | No | Optional provider cleanup follows |
| TX-021 | Execution Interrupted Recovery | recovery service | Yes | No | No |
| TX-022 | Event Lease Recovery | recovery service | Yes | No | No |
| TX-023 | Command Lease Recovery | recovery service | Yes | No | No |
| TX-024 | Interaction Projection Repair | recovery service | Yes | No | No |
| TX-025 | Commit Recovery Completion | recovery service | Yes | Maybe already finalized | No |
| TX-026 | External Delivery Intent | integration service | Yes | No | Yes, afterward |
| TX-027 | External Delivery Acknowledgement | integration service | Yes | No | Already occurred |
| TX-028 | Runtime Startup Identity | startup coordinator | Yes | No | No |

---

# 4. TX-001 — Create Job

## Purpose

Create one Runtime Job from one persisted `create_job` Command.

## Precondition

```text
create_job Command exists
job_id is already allocated and stable
Target Job source is valid
```

## Filesystem Boundary

Before SQLite commit:

```text
persist/finalize immutable Target Job artifact file
verify stored bytes/hash
```

If file finalization fails:

```text
no Runtime Job is created
Command remains retryable/fails according to policy
```

## SQLite Reads

- `commands` current row.
- latest eligible reusable JER artifact versions.
- existing Runtime Job for intended `job_id`, if retry/reconciliation.

## SQLite Writes

```text
artifacts
→ Target Job metadata

runtime_jobs
→ create revision 1

job_artifact_pointers
→ target_job

job_artifact_collection_members
→ initial exact pinned jer_set

events
→ job_created

commands
→ create_job completed
```

## Atomic Boundary

```text
BEGIN

insert Target Job artifact metadata
insert Runtime Job revision 1
set target_job pointer
insert exact JER collection members
persist job_created Event
mark create_job Command completed

COMMIT
```

## Idempotency

Retrying the same `create_job` Command:

```text
same command_id
same intended job_id
→ reconcile existing state
→ never allocate another Job
```

A separate new `create_job` Command may intentionally create another Job from the same source.

## Crash Interpretation

```text
file exists + SQLite Job absent
→ safe orphan file / retry job transaction

SQLite Job exists + Command incomplete
→ reconcile and complete same Command

Job + Event + Command completion
→ success
```

---

# 5. TX-002 — Claim Command

## Purpose

Atomically acquire short-lived ownership of one eligible Command.

## Reads

Eligible:

```text
status IN (pending, retry_pending)
AND lease absent/expired
```

## Writes

```text
status = processing
owner_runtime_instance_id = current runtime
lease_expires_at = now + lease_duration
attempt_count += 1
```

## Atomic Boundary

One claim transaction.

No external work occurs inside the transaction.

## Failure

If another worker wins:

```text
zero rows claimed
→ normal contention
```

Not a Runtime Job failure.

---

# 6. TX-003 — Complete SQLite-Local Command

## Purpose

Complete deterministic runtime work whose authoritative effects all live in SQLite.

Examples:

```text
evaluate_routing
complete_interaction
cancel_job
enter_manual_review
```

## Required Rule

```text
authoritative mutation
+
required Event(s)
+
Command completion
```

commit together.

## Generic Boundary

```text
BEGIN

validate Command still processing/owned
perform authoritative local mutation
persist required Event(s)
mark Command completed
clear lease/ownership

COMMIT
```

If the transaction fails:

```text
none of the authoritative effects commit
Command remains recoverable
```

---

# 7. TX-004 — Claim Event

Same ownership pattern as Command claim.

## Writes

```text
status = processing
owner_runtime_instance_id = current runtime
lease_expires_at = ...
attempt_count += 1
```

No downstream Commands are created in this claim transaction.

---

# 8. TX-005 — Event → Command

## Purpose

Convert one processed Event into one or more durable Commands.

## Reads

- Event.
- current runtime state required for deterministic command derivation.
- existing Command rows by dedupe key.

## Writes

```text
commands
→ insert/reuse all deterministic Commands

events
→ processed
→ processed_at
→ clear lease/ownership
```

## Atomic Boundary

```text
BEGIN

derive deterministic command_dedupe_key(s)
insert Command(s) if absent
mark Event processed

COMMIT
```

## Critical Invariant

Never:

```text
mark Event processed
→ crash
→ required Command not durable
```

## Duplicate Event Processing

Retry safely reuses Commands by dedupe key.

---

# 9. TX-006 — schedule_operation Creates or Reuses Execution

## Purpose

Complete the `schedule_operation` Command once the target professional Execution is durably created or safely reused.

## Reads

- Runtime Job.
- Operation Specification.
- identity dependencies.
- existing active/committed Execution by `operation_key`.

## Writes

Possible:

```text
executions
→ create attempt

runtime_jobs
→ operation projection queued/current Execution
→ revision increment when projection changes

commands
→ schedule_operation completed
```

Optional Event:

```text
operation_scheduled
```

if required by implementation vocabulary.

## Atomic Boundary

```text
BEGIN

revalidate Job/spec eligibility
derive/reconfirm operation_key
reuse compatible Execution OR insert new Execution
update RuntimeJob.operation projection if required
increment Runtime Job revision if projection changed
persist required runtime Event(s)
mark schedule_operation Command completed

COMMIT
```

## Invariant

The Command lease ends here.

It does **not** remain held during professional invocation.

---

# 10. TX-007 — Begin Execution

## Purpose

Move a queued/created Execution into provider invocation ownership.

## Reads

- Execution.
- runtime instance.
- current Job/spec validity as needed.

## Writes

```text
Execution.status = running
owner_runtime_instance_id = current runtime
started_at
RuntimeJob.operation projection = running, if projection changes
Runtime Job revision increment, if applicable
execution_started Event, if persisted
```

## Provider Boundary

Commit this transaction **before** calling the professional provider.

Then:

```text
SQLite commit
→ provider invocation
```

A provider timeout cannot be rolled back through SQLite.

---

# 11. TX-008 — Professional Single-Output Commit

## Purpose

Make one validated professional artifact current.

Examples:

```text
JEA
ERQ
Resume Evaluation
```

## Preconditions

```text
Execution exists
status compatible with committing
output staged
schema valid
Operation Specification valid
requested mutation authorized
freshness dependencies current
immutable artifact file finalized and verified
```

## SQLite Reads

- Runtime Job current revision/state.
- Execution/input snapshot.
- Operation Specification identity/provenance.
- current pointer/collection state.
- artifact metadata collision check.

## Writes

```text
artifacts
→ committed artifact metadata

job_artifact_pointers OR collection_members
→ authorized mutation

runtime_jobs
→ revision +1
→ operation projection returns idle/current state as appropriate

executions
→ committed
→ committed_outputs
→ completed_at

events
→ artifact_committed
```

Potential commit-group rows if implementation uses them for all outputs.

## Atomic Boundary

```text
BEGIN

recheck expected Runtime Job revision
recheck exact freshness dependencies

insert artifact metadata
apply authorized semantic pointer/collection mutation
update Runtime Job operation projection
increment Runtime Job revision
finalize Execution committed
persist artifact_committed

COMMIT
```

## CAS Conflict

If Runtime Job revision changed:

```text
reload Job
re-evaluate freshness dependencies
```

If still fresh:

```text
retry same commit transaction using new expected revision
```

If stale:

```text
do not advance pointer
mark Execution/output stale through appropriate transaction
```

## Filesystem Failure Cases

```text
final file absent
→ do not begin authoritative SQLite commit

final file exists
+ SQLite commit fails
→ orphan immutable file tolerated
```

---

# 12. TX-009 — Coupled Resume/WCM Commit

## Purpose

Commit Resume + WCM as one semantic product.

## Filesystem Before Transaction

Finalize and verify both:

```text
Targeted Resume
Writer Content Manifest
```

If either fails:

```text
no authoritative SQLite commit
```

## SQLite Writes

```text
artifacts
→ Resume metadata
→ WCM metadata

artifact_commit_groups
→ coupled group

artifact_commit_group_members
→ both members

job_artifact_pointers
→ resume
→ wcm

runtime_jobs
→ operation projection / revision

executions
→ committed with both outputs

events
→ exactly one artifact_committed for coupled product
```

## Atomic Boundary

All above rows commit together.

Never expose:

```text
new resume
+
old WCM
```

or vice versa.

---

# 13. TX-010 — Evidence Integration Commit

## Purpose

Atomically integrate one or more Evidence Responses into authoritative reusable JER state.

## Preconditions

- integrate_evidence Execution valid.
- all required JER outputs staged/validated/finalized.
- exact Evidence Responses remain unintegrated/current.
- Operation Specification authorizes mutations.

## Writes

Potentially multiple:

```text
artifacts
→ new JER versions

job_artifact_collection_members
→ UPSERT_VERSION jer_set

job_artifact_collection_members
→ REMOVE consumed unintegrated Evidence Responses

runtime_jobs
→ revision + operation projection

executions
→ committed

events
→ one artifact_committed for logical integration group
```

Commit-group records recommended.

## Atomic Invariant

Either:

```text
all required JER versions
+
all required consumed Evidence Response removals
```

become authoritative,

or none do.

No partial integration.

---

# 14. TX-011 — Completed Evidence Response Professional Commit

## Purpose

Commit a completed Interviewer Evidence Response and consume exactly the human-message batch that produced it.

## Preconditions

```text
Interaction active/paused
exact ERQ/version current
Interviewer continuation returned CompletedProfessionalArtifact
artifact_type == evidence_response
exact immutable human-message batch known
all messages currently unprocessed
Evidence Response staged/validated/finalized
```

## SQLite Writes

```text
artifacts
→ Evidence Response metadata

job_artifact_collection_members
→ ADD unintegrated_evidence_responses

interaction_messages
→ exact consumed message IDs processed
→ processed_at
→ processed_by_continuation_id

executions
→ committed

runtime_jobs
→ authorized professional state mutation
→ operation projection
→ revision increment

events
→ artifact_committed
```

Continuation provenance as required.

## Atomic Boundary

```text
BEGIN

validate exact message IDs still unprocessed
validate exact ERQ/version freshness
insert Evidence Response metadata
add Evidence Response current collection member
mark exact messages processed
finalize Execution committed
update Runtime Job + revision
persist artifact_committed

COMMIT
```

## Critical Invariant

Never expose:

```text
committed Evidence Response
+
same source human messages unprocessed
```

## Failure

Transaction failure:

```text
Evidence Response not authoritative
messages remain unprocessed
continuation retryable
```

Interaction completion is **not** part of this transaction.

---

# 15. TX-012 — Routing Transition

## Purpose

Apply a deterministic lifecycle transition.

## Reads

- canonical Runtime Job.
- exact current artifact state needed by predicate.

## Writes

```text
routing_decisions
→ append decision

runtime_jobs
→ lifecycle.phase
→ lifecycle.entered_at
→ revision +1

events
→ lifecycle_changed

commands
→ evaluate_routing completed
```

## Atomic Boundary

```text
BEGIN

revalidate expected Job revision
insert RoutingDecision
update lifecycle
increment revision
persist lifecycle_changed
mark evaluate_routing Command completed

COMMIT
```

## Invariant

Routing history cannot exist without the corresponding lifecycle state.

Lifecycle change cannot exist without the Event.

---

# 16. TX-013 — Routing No-Op Completion

## Purpose

Complete `evaluate_routing` when current state requires no lifecycle transition.

## Writes

```text
commands
→ completed
```

No routing-history append.

No lifecycle Event.

No Runtime Job revision unless another authoritative Runtime Job mutation actually occurs.

This prevents meaningless revision/history growth from routine duplicate routing checks.

---

# 17. TX-014 — Inbound Human Message Persistence

## Purpose

Normalize and durably record authorized provider input.

## External Boundary

The Discord message already exists externally before this transaction.

## Reads

- Interaction mapping/provider context.
- provider message dedupe identity.

## Writes

```text
interaction_messages
→ persist unseen message

events
→ human_input_received
```

Potential Interaction activity timestamp/projection update if architecture requires.

If RuntimeJob interaction last-activity projection is updated, include:

```text
Runtime Job revision
```

in the same transaction.

## Atomic Boundary

```text
BEGIN

dedupe provider message
insert InteractionMessage
persist human_input_received Event
update authoritative Interaction activity state if required
update RuntimeJob projection + revision if coarse projection changes

COMMIT
```

A duplicate provider message should converge on the existing stored Message.

---

# 18. TX-015 — Conversational Interviewer Continuation

## Purpose

Consume one exact immutable human-message batch and persist the next Interviewer conversational turn.

## Preconditions

- Interaction active/paused.
- exact batch resolved in canonical provider chronology.
- continuation returns `ConversationTurn`.

## Provider Boundary

Professional provider invocation occurs **before** this transaction.

The returned next Interviewer message is not sent to Discord until after local persistence succeeds.

## SQLite Writes

```text
interaction_messages
→ exact human batch processed

interaction_messages
→ persist next Interviewer outbound message/intention

interactions
→ update continuation/activity state

RuntimeJob interaction projection
→ update only if coarse projection changes
→ revision increment if changed
```

Optional Events as defined.

## Atomic Invariant

Never:

```text
human messages marked processed
+
next Interviewer message lost locally
```

## Discord Delivery

After commit:

```text
durable local outbound message
→ Discord send
→ acknowledgement/reconciliation transaction
```

---

# 19. TX-016 — Complete Interaction

## Purpose

Complete the authoritative Interaction only after exact Evidence Response professional commit is durable.

## Preconditions

```text
Interaction active/paused
committed Evidence Response exists
Evidence Response matches current ERQ/version
```

## Writes

```text
interactions
→ status completed
→ completed_at

runtime_jobs
→ interaction projection completed
→ revision +1

events
→ interaction_completed

commands
→ complete_interaction completed
```

## Atomic Boundary

All four effects commit together.

## Recovery Rule

```text
Interaction active/paused
+
matching committed Evidence Response
→ schedule/retry complete_interaction
```

Invalid reverse state:

```text
Interaction completed
+
no matching committed Evidence Response
→ repair/manual review
```

---

# 20. TX-017 — Pause / Resume / Cancel Interaction Projection

## Purpose

Keep authoritative Interaction and Runtime Job coarse projection synchronized.

## Writes

When projection changes:

```text
interactions
+
runtime_jobs.interaction
+
Runtime Job revision
+
required Event
+
responsible Command completion
```

all in one transaction.

Provider-only metadata changes that do not affect coarse projection do not increment Runtime Job revision.

---

# 21. TX-018 — Material Failure Transition

## Purpose

Persist a runtime failure and make it the current material Job health failure when applicable.

## Writes

```text
failures
→ new Failure

runtime_jobs
→ health.status
→ health.failure_id
→ health.retry_count as appropriate
→ revision +1

events
→ health_changed / manual_review_required as required
```

Related Execution/Event/Command status change may join the transaction when the failure is locally caused by that same processing step.

## Atomic Invariant

Do not expose:

```text
Job blocked
+
no persistent Failure explaining why
```

where a material failure exists.

---

# 22. TX-019 — Resolve Failure / Recompute Health

## Purpose

Resolve one current/historical Failure and recompute Job health.

## Reads

- Failure.
- other unresolved material Failures.
- Job health/current failure pointer.

## Writes

```text
failures
→ resolved_at
→ resolution_message

runtime_jobs
→ clear/replace health.failure_id
→ recompute health status
→ revision +1 when state changes

events
→ health_changed when required
```

Historical Failure remains stored.

---

# 23. TX-020 — Cancel Job

## Purpose

Explicit terminal human cancellation.

## Writes

```text
runtime_jobs
→ lifecycle cancelled
→ completed/terminal timing as defined
→ operation state safe terminal/idle
→ interaction projection cleared or cancellation-consistent
→ revision +1

routing_decisions
→ optional explicit cancellation history if model requires

events
→ job_cancelled / lifecycle_changed as required

commands
→ cancel_job completed
```

Any external Discord cleanup occurs after authoritative local cancellation.

Professional artifacts are retained.

---

# 24. TX-021 — Interrupted Execution Recovery

## Purpose

Reconcile a nonterminal Execution owned by a dead runtime instance.

## Reads

```text
Execution status
owner_runtime_instance_id
current Runtime Job
staging state
artifact metadata/current pointers
```

## Typical `running` Recovery Writes

```text
Execution
→ failed
→ completed_at

Failure
→ invocation_failure/runtime_interrupted

RuntimeJob
→ operation projection cleared/recoverable
→ health/retry state if required
→ revision

Event
→ execution_failed / health_changed as required
```

If retry allowed, scheduling a **new** Execution attempt occurs through normal Command flow rather than rewriting the old attempt.

Old physical attempt remains immutable history.

---

# 25. TX-022 — Event Lease Recovery

## Purpose

Return abandoned Event processing to retryable state.

## Reads

```text
Event.status == processing
lease expired / owner runtime dead
```

## Writes

```text
status = retry_pending
owner_runtime_instance_id = NULL
lease_expires_at = NULL
last_error / recovery detail if appropriate
```

No duplicate downstream Command is created here.

Normal Event processing will use dedupe.

---

# 26. TX-023 — Command Lease Recovery

Same pattern as Event lease recovery.

## Writes

```text
processing
→ retry_pending

clear owner/lease
```

For `schedule_operation`, recovery must first inspect whether the Execution was already created/reused before rerunning the Command.

---

# 27. TX-024 — Interaction Projection Repair

## Purpose

Repair a safely derivable mismatch between authoritative Interaction and Runtime Job projection.

Example:

```text
Interaction = completed
RuntimeJob projection = active
```

## Reads

- authoritative Interaction.
- Runtime Job expected revision.

## Writes

```text
runtime_jobs.interaction projection
Runtime Job revision
repair/recovery Event if required
```

If ambiguity exists:

```text
do not guess
→ TX-018 failure/manual-review transition
```

---

# 28. TX-025 — Commit Recovery Completion

## Purpose

Finish or reconcile an Execution interrupted around professional commit.

## Recovery Cases

### Case A — files exist, no SQLite professional commit, freshness still valid

Retry the same professional commit transaction.

### Case B — current pointers/commit state already advanced, Execution not marked committed

Repair:

```text
Execution → committed
```

and any missing telemetry only if professional authoritative commit can be proven complete.

Never emit a second `artifact_committed` if the canonical Event already exists.

### Case C — files exist, newer conflicting professional state exists

Classify old output:

```text
stale_output
orphaned_output
```

as appropriate.

Do not advance current pointers.

---

# 29. TX-026 — External Delivery Intent

## Purpose

Durably record an outbound external action before calling a provider when losing the intention would make recovery unsafe.

Examples:

```text
Discord outbound Interviewer message
future projection update
```

## SQLite Writes

Depending on integration:

```text
durable outbound message/intention
provider idempotency key if supported
delivery status = pending
```

## Boundary

```text
SQLite intent commit
→ external provider call
```

Never rely only on in-memory intent.

---

# 30. TX-027 — External Delivery Acknowledgement

## Purpose

Persist known provider result.

## Reads

- durable local outbound intent.
- provider response/reconciliation result.

## Writes

```text
provider message/action ID
delivery status
provider timestamp
reconciliation metadata
```

Optional integration Event.

## Ambiguous Timeout

```text
timeout
≠ provider definitely did not act
```

Reconcile provider state before repeating when duplicate external action would be unsafe.

---

# 31. TX-028 — Runtime Startup Identity

## Purpose

Persist one daemon-process lifetime before claiming runtime work.

## Writes

```text
runtime_instances
→ new runtime_instance_id
→ build identity
→ started_at
```

Occurs after config/database initialization and before worker ownership uses the ID.

Shutdown may later update:

```text
stopped_at
```

best-effort.

Recovery must not depend on graceful shutdown having occurred.

---

# 32. Professional Commit State Machine

Common Execution path:

```text
created
→ queued
→ running
→ output_received
→ validating
→ validated
→ committing
→ committed
```

Important durable boundaries:

```text
before provider call
→ running is committed

after provider returns
→ output/staging state may be persisted

before authoritative commit
→ status committing

professional SQLite commit
→ Execution committed + artifact_committed atomically
```

A process crash at every arrow must have one deterministic recovery interpretation.

---

# 33. Runtime Job Revision Rules

Increment Runtime Job revision exactly once per authoritative Runtime Job mutation transaction.

Examples that increment:

```text
set operation projection
professional pointer/collection commit
lifecycle transition
Interaction projection change
health state change
cancel Job
```

Examples that normally do not increment:

```text
Event processing metadata only
Command claim only
Execution provider telemetry only
provider metadata update that does not change RuntimeJob projection
Failure record resolution that leaves Job health unchanged
```

A transaction performing several Runtime Job field changes still increments revision only once.

---

# 34. CAS Retry Rules

CAS conflict handling is transaction-specific.

## Professional Commit

```text
CAS conflict
→ reload Job
→ re-evaluate declared freshness dependencies
→ retry same commit only if still fresh
→ otherwise stale
```

## Routing

```text
CAS conflict
→ reload Job/current professional state
→ recompute predicate
→ do not blindly replay old RoutingDecision
```

## Interaction Projection

```text
CAS conflict
→ reload authoritative Interaction + Job
→ recompute projection
```

## Health

```text
CAS conflict
→ reload unresolved Failure set + Job
→ recompute health
```

CAS retry must re-derive semantic validity.

---

# 35. Event Ownership Rules

Events persisted transactionally with their authoritative facts:

```text
job_created
→ TX-001

artifact_committed
→ TX-008 / TX-009 / TX-010 / TX-011

lifecycle_changed
→ TX-012

human_input_received
→ TX-014

interaction_completed
→ TX-016

health_changed
→ TX-018 / TX-019 when state changes

job_cancelled
→ TX-020
```

This prevents Events from claiming state that is not durable.

---

# 36. Command Completion Rules

A Command is completed only when its authoritative effect is durable.

Examples:

```text
create_job
→ Job + job_created durable

schedule_operation
→ target Execution created/reused durably

evaluate_routing
→ lifecycle transition durable OR deterministic no-op completed

complete_interaction
→ Interaction + projection + Event durable

cancel_job
→ Job cancellation durable
```

Starting a handler is never sufficient for Command completion.

---

# 37. Filesystem / SQLite Boundary Matrix

| Operation | Filesystem Before SQLite | SQLite Authority |
|---|---|---|
| create_job | Target Job finalized | metadata + Job + pointers |
| generate_analysis | JEA finalized | metadata + JEA pointer |
| request_evidence | ERQ finalized | metadata + active_erqs |
| integrate_evidence | JER files finalized | metadata + JER collection + consumed responses |
| generate_resume | Resume + WCM finalized | metadata + coupled pointers |
| evaluate_resume | Evaluation finalized | metadata + evaluation pointer |
| Interviewer Evidence Response | Evidence Response finalized | metadata + unintegrated response + consumed messages |

Rule:

```text
file exists without SQLite authority
→ tolerable/recoverable

SQLite authority points to missing file
→ integrity failure
```

---

# 38. External Side-Effect Matrix

| External Action | Durable Intent First? | Local Authority Depends on External Success? |
|---|---|---|
| Professional model invocation | Execution running already durable | No; output commit depends on returned result |
| Discord outbound message | Yes when duplicate/loss matters | Interaction professional state does not depend on delivery acknowledgement |
| Discord inbound message | External fact already exists | Local persistence required before processing |
| EvidenceSource retrieval | Execution state durable | Professional invocation may be blocked if required retrieval fails |
| Future Trello projection | Yes if implemented | No; projection is nonauthoritative |

---

# 39. Transaction Isolation Assumptions

V0.1 uses one active runtime container and SQLite serialized writes.

Recommended authoritative mutations use:

```text
BEGIN IMMEDIATE
```

when early write-lock acquisition materially simplifies correctness.

Read-only work may use ordinary deferred transactions.

Implementation should avoid holding SQLite write transactions open during:

```text
professional provider calls
Discord API calls
Google Drive/network retrieval
large file writes
long CPU-bound parsing
```

Perform those outside the authoritative SQLite transaction.

Transactions should remain short.

---

# 40. Deadlock / Locking Principle

SQLite uses database-level write serialization rather than row-level deadlocks typical of larger RDBMSs.

The primary risks are:

```text
long write transactions
busy timeout exhaustion
incorrect async connection sharing
```

Therefore:

- provider/network calls never occur inside write transactions;
- file finalization occurs before professional SQLite commit;
- transaction code should not await unrelated network operations;
- one UnitOfWork owns one transaction connection.

---

# 41. Idempotency Matrix

| Transaction | Idempotency Mechanism |
|---|---|
| Create Job | stable Command ID + intended Job ID |
| Event → Command | Command dedupe key |
| schedule_operation | operation_key + one active Execution constraint |
| Professional commit | operation_key + Execution state + exact artifact identity |
| Routing | current state recomputation + Command dedupe |
| Human message ingress | provider_message_id unique constraint |
| Conversational continuation | exact message batch / persisted continuation state |
| Evidence Response commit | exact message IDs + Execution/operation identity |
| complete_interaction | authoritative Interaction status + Command dedupe |
| External delivery | durable local intent + provider ID/idempotency/reconciliation |

---

# 42. Crash Injection Points

Every critical transaction must be tested at these boundaries where applicable:

```text
before BEGIN
after first write
after each major table write
before COMMIT
immediately after COMMIT
before Event processor sees new Event
before external provider call
after provider success but before local acknowledgement
```

Professional commit additionally:

```text
after staged output
after file finalization
before SQLite commit
after artifact metadata insert
after pointer mutation
after Execution finalization
after artifact_committed insert
after COMMIT
```

The test plan should implement deterministic crash injection around these points.

---

# 43. Recovery Decision Table

| Observed State | Interpretation | Recovery |
|---|---|---|
| finalized file, no artifact metadata | orphan/precommit | retry or classify orphan |
| artifact metadata, no current pointer, Execution noncommitted | incomplete commit candidate | inspect transaction evidence/freshness |
| current pointer advanced + `artifact_committed`, Execution not committed | repair Execution terminal state |
| Execution running, owner runtime dead | interrupted physical attempt | fail attempt, retry via new Execution if allowed |
| Event processed, no required Command | integrity defect | should be impossible if TX-005 correct |
| Command completed, authoritative effect absent | integrity defect | manual repair/recovery |
| Evidence Response committed, source messages unprocessed | integrity defect | should be impossible if TX-011 correct |
| Evidence Response committed, Interaction active | safe crash window | schedule complete_interaction |
| Interaction completed, no matching Evidence Response | invalid | repair/manual review |
| lifecycle changed, no lifecycle_changed Event | integrity defect | should be impossible if TX-012 correct |
| Job blocked, no current Failure pointer | integrity defect if material failure expected | repair/manual review |

---

# 44. Unit-of-Work Requirements

The transaction design requires a transaction-scoped persistence boundary.

Conceptual:

```python
async with uow_factory() as uow:
    ...
    await uow.commit()
```

One UnitOfWork must expose repositories bound to the **same SQLite connection and transaction**.

Required repository access may include:

```text
jobs
artifacts
executions
events
commands
interactions
messages
failures
routing
provenance
```

No repository may silently open a second independent connection during one required atomic mutation.

---

# 45. Transaction Ownership

| Transaction | Primary Service |
|---|---|
| TX-001 | CreateJobCommandHandler |
| TX-002 | CommandProcessor |
| TX-003 | relevant deterministic CommandHandler |
| TX-004 | EventProcessor |
| TX-005 | EventProcessor |
| TX-006 | ScheduleOperationCommandHandler |
| TX-007 | ExecutionWorker / execution service |
| TX-008–011 | CommitCoordinator |
| TX-012–013 | Router / EvaluateRoutingCommandHandler |
| TX-014 | Discord ingress adapter/service |
| TX-015 | InteractionProcessor |
| TX-016 | CompleteInteractionCommandHandler |
| TX-017 | Interaction runtime service |
| TX-018–019 | Failure/Health service |
| TX-020 | CancelJobCommandHandler |
| TX-021–025 | RecoveryCoordinator subservices |
| TX-026–027 | integration delivery service |
| TX-028 | StartupCoordinator |

Ownership means:

```text
component responsible for constructing the transaction
```

not unrestricted authority beyond architecture rules.

---

# 46. Transaction Audit Metadata

Every authoritative transaction should make later diagnosis possible through existing records.

Minimum reconstruction should reveal:

```text
job_id
expected/ resulting Runtime Job revision
command_id when command-driven
event_id when event-driven
execution_id when professional
interaction_id when human-interaction related
operation_key for professional work
runtime_instance_id
timestamps
```

Avoid introducing a generic transaction-log table unless implementation evidence shows it is necessary.

Existing domain records should provide sufficient causal history.

---

# 47. Transaction Logging

Structured application logs should include transaction context but are not authoritative persistence.

Recommended log fields:

```text
transaction_kind
job_id
command_id
event_id
execution_id
interaction_id
expected_revision
resulting_revision
runtime_instance_id
outcome
latency_ms
```

Never rely on logs to reconstruct authoritative state that belongs in SQLite.

---

# 48. Phase 4 Decisions Made

This planning phase confirms:

1. A shared SQLite UnitOfWork is required.
2. Provider/network calls occur outside SQLite write transactions.
3. Artifact files finalize before authoritative professional SQLite commit.
4. Event→Command durability is one transaction.
5. Command completion is transactionally tied to the authoritative local effect when SQLite-local.
6. Professional commit always owns `artifact_committed`.
7. Coupled Resume/WCM is one professional commit.
8. Evidence integration is one multi-artifact commit group.
9. Completed Evidence Response consumes the exact human-message batch in the same commit.
10. Interaction completion is a later independent transaction.
11. Routing transition/history/Event/Command completion is one transaction.
12. Failure creation and current Job health linkage are atomic when locally caused together.
13. CAS conflict retry must re-evaluate semantic validity, not blindly replay stale mutations.
14. Crash/recovery tests must target transaction boundaries directly.

---

# 49. Open Decisions for Later Phases

Still intentionally deferred:

- exact UnitOfWork class/API;
- which transactions use `BEGIN IMMEDIATE`;
- exact repository method granularity;
- exact outbound-delivery persistence representation;
- exact artifact commit-group status implementation;
- exact operation projection timing for some Execution transitions;
- exact Event vocabulary for telemetry-only state changes;
- retry limits and backoff;
- crash-injection framework.

These belong to package/interface planning and the test plan.

---

# 50. Phase 4 Acceptance Criteria

The Transaction Matrix is complete when:

- [ ] every authoritative Runtime Job mutation has an explicit transaction owner;
- [ ] every transaction defines its atomic SQLite writes;
- [ ] professional filesystem work is separated from SQLite authority;
- [ ] `artifact_committed` is always transactionally coupled to professional commit;
- [ ] Event processing cannot lose required Commands;
- [ ] routing cannot expose lifecycle state without routing history/Event;
- [ ] completed Evidence Response cannot leave source human messages unprocessed;
- [ ] Interaction completion cannot diverge from the Runtime Job projection;
- [ ] material failure state has persistent Failure support;
- [ ] Command completion means the authoritative effect is durable;
- [ ] CAS conflict behavior is defined for semantic mutations;
- [ ] each critical crash window has a deterministic recovery interpretation;
- [ ] provider/network calls are outside SQLite write transactions;
- [ ] the model supports deterministic crash-injection testing.

## Result

**READY FOR PHASE 5 — PACKAGE AND INTERFACE PLAN**