# RRS V3 Persistence Model

## Status

Draft V0.14 — FIX-007, FIX-008, FIX-009, FIX-015, FIX-016, FIX-017, FIX-018, FIX-019, FIX-022, FIX-026, FIX-036, FIX-037, and FIX-038 applied

## Purpose

The Persistence Model defines how the V3 runtime stores authoritative runtime state, immutable professional artifacts, execution history, events, interactions, and operational metadata.

V3 V0.1 standardizes on:

```text
SQLite
+
filesystem-backed immutable professional artifacts
+
Docker persistent storage
```

The runtime is intended to run as a single Docker container with persistent state mounted outside the container filesystem.

The container is disposable.

The data volume is authoritative.

---

# Core Invariants

1. Runtime state and professional artifact contents remain separate.
2. Runtime Job current state is mutable and revision-controlled.
3. Professional artifact versions are immutable after commit.
4. Runtime metadata is stored outside professional artifact bodies.
5. Current pointers reference exact artifact IDs and versions.
6. Historical artifact versions are never silently overwritten.
7. Executions and Events are append-oriented historical records.
8. SQLite is the authoritative runtime/control-plane store for V0.1.
9. The filesystem is the authoritative professional artifact-content store for V0.1.
10. Trello and Discord are projections/integrations, not persistence authorities.
11. Runtime commits may tolerate orphaned immutable artifacts but must never expose broken current pointers.
12. Storage must support crash/restart reconciliation.
13. Repository interfaces isolate handlers from SQLite/filesystem implementation.
14. One RRS runtime container owns one SQLite database file.
15. Multiple container replicas must not concurrently write the same SQLite database.
16. Persistent storage must survive container recreation and upgrade.

---

# 1. V0.1 Deployment Target

Recommended deployment shape:

```text
Docker Container
│
├── /app
│   ├── Python runtime
│   ├── runtime architecture
│   ├── handlers
│   ├── routing
│   ├── integrations
│   └── configuration
│
└── /data                       ← persistent mount
    ├── rrs.db                  ← SQLite
    └── artifacts/              ← immutable artifact files
```

The `/data` path must be backed by:

- Docker volume, or
- host bind mount.

The container image itself must not be treated as durable storage.

---

# 2. Logical Stores

V3 defines five authoritative logical stores:

```text
Runtime Job Store
Professional Artifact Store
Execution Store
Event Store
Interaction Store
```

They may share physical technology, but their responsibilities remain separate.

For V0.1:

```text
Runtime Job Store      → SQLite
Artifact metadata      → SQLite
Artifact content       → filesystem
Execution Store        → SQLite
Event Store            → SQLite
Interaction Store      → SQLite
```

---

# 3. Runtime Job Store

The Runtime Job Store owns current control-plane state.

It stores:

- Runtime Job identity.
- Runtime Job revision.
- Lifecycle state.
- Operation state.
- Human-interaction state.
- Health state.
- Current professional artifact pointers.
- Routing history.
- Creation/update/completion timestamps.

It does not store full professional artifact bodies.

---

# 4. Runtime Job Revision

Each Runtime Job has a monotonic integer revision.

Example:

```yaml
identity:
  job_id: JOB-0001
  revision: 28
```

Every successful Runtime Job mutation increments:

```text
revision
```

The revision supports:

- Optimistic concurrency.
- Compare-and-swap updates.
- Conflict detection.
- Projection synchronization.
- Crash recovery.

---

# 5. Optimistic Concurrency

Conceptually:

```text
read JOB-0001 revision 28
      ↓
prepare mutation
      ↓
UPDATE runtime_jobs
SET revision = 29, ...
WHERE job_id = 'JOB-0001'
AND revision = 28
```

If exactly one row updates:

```text
success
```

If no row updates:

```text
concurrency conflict
```

The caller must reload current state and reconcile.

Runtime Job revision is a mutation guard.

Professional stale-input validation still compares exact artifact dependencies.

An unrelated runtime mutation should not automatically make a professional execution stale.

---

# 6. Professional Artifact Store

The Professional Artifact Store owns immutable professional artifact content.

Examples include:

```text
Job Experience Record
Job Experience Analysis
Information Request
Information Response
Evidence Request
Evidence Response
Targeted Resume
Writer Content Manifest
Resume Evaluation
Process Feedback
```

Future artifact types may be added without changing the core storage model.

---

# 7. Artifact Immutability

A committed artifact version is immutable.

Example:

```text
JEA-0004
├── v1.yaml
├── v2.yaml
├── v3.yaml
└── v4.yaml
```

The runtime may create:

```text
v5
```

but it must never overwrite:

```text
v4
```

with new content.

If the same artifact ID/version already exists with different content:

```text
storage conflict
```

must be raised.

---

# 8. Artifact Filesystem Layout

Recommended V0.1 layout:

```text
/data/artifacts/
│
├── JER-0001/
│   ├── v1.yaml
│   ├── v2.yaml
│   └── v3.yaml
│
├── JEA-0004/
│   ├── v1.yaml
│   └── v2.yaml
│
├── ERQ-0011/
│   └── v1.yaml
│
├── ERESP-0008/
│   └── v1.yaml
│
├── RESUME-0003/
│   └── v4.docx
│
├── WCM-0003/
│   └── v4.yaml
│
└── EVAL-0003/
    └── v2.yaml
```

Exact filenames may vary by artifact type.

Directory naming should remain stable and deterministic.

---

# 9. Artifact Metadata

Artifact runtime metadata is stored separately from artifact contents.

Conceptual metadata:

```yaml
artifact_metadata:

  artifact_id: JEA-0004

  artifact_version: 4

  artifact_type: job_experience_analysis

  storage_uri: artifacts/JEA-0004/v4.yaml

  content_hash: sha256:...

  committed_by_execution_id: EXEC-0044

  operation_key: OPKEY-ABC123

  committed_at: ...

  runtime_status: committed
```

This metadata does not belong inside the professional JEA schema.

---

# 10. Artifact Metadata Purpose

Artifact metadata should answer:

- Where is the artifact stored?
- What type is it?
- Which exact version is it?
- What is its content hash?
- Which Execution committed it?
- Which logical operation produced it?
- When was it committed?
- Is it committed, stale, orphaned, diagnostic, or otherwise noncurrent?

It should not answer professional questions such as:

- Is this evidence strong?
- Does this satisfy the job?
- Is the candidate qualified?

---

# 11. Artifact Content Hash

Every persisted professional artifact should receive a cryptographic content hash.

Recommended:

```text
SHA-256
```

Example:

```yaml
content_hash: sha256:7b2...
```

Uses:

- Detect accidental mutation.
- Verify persistence integrity.
- Detect same-version content conflicts.
- Support backups and diagnostics.
- Confirm file identity during recovery.

---

# 12. Current Artifact Pointers

Current professional state belongs to the Runtime Job Store.

Conceptually:

```text
JOB-0001
│
├── current JEA        → JEA-0004:v5
├── current Resume     → RESUME-0003:v4
├── current WCM        → WCM-0003:v4
└── current Evaluation → EVAL-0003:v2
```

Current pointers are runtime state.

Artifact history remains in the Artifact Store.

---

# 13. Pointer Persistence

The implementation may represent current pointers through normalized relational records.

Conceptual table:

```text
job_artifact_pointers
------------------------------------------------
job_id
pointer_type
artifact_id
artifact_version
```

Example:

```text
JOB-0001 | jea        | JEA-0004    | 5
JOB-0001 | resume     | RESUME-0003 | 4
JOB-0001 | wcm        | WCM-0003    | 4
JOB-0001 | evaluation | EVAL-0003   | 2
```

This is an implementation recommendation, not a professional schema.

---

# 14. Pointer Collections

Some current professional state is a collection.

Examples:

```text
jer_set
active_erqs
unintegrated_evidence_responses
```

A normalized collection table may represent these:

```text
job_artifact_collection_members
------------------------------------------------
job_id
collection_type
artifact_id
artifact_version
```

Example:

```text
JOB-0001 | jer_set | JER-0001 | 4
JOB-0001 | jer_set | JER-0007 | 3
```

The implementation should support atomic replacement or deterministic merge semantics for collection updates.

---

# 15. Execution Store

The Execution Store records every physical professional-operation attempt.

Example:

```text
OPKEY-ABC
├── EXEC-0042 attempt 1 → timeout
├── EXEC-0043 attempt 2 → schema failure
└── EXEC-0044 attempt 3 → committed
```

Execution records support:

- Idempotency.
- Retry.
- Diagnostics.
- Input provenance.
- Output provenance.
- Crash recovery.
- Audit.

---

# 16. Execution Persistence

Execution records should preserve:

```text
execution_id
job_id
owner_runtime_instance_id
operation_key
operation_type
attempt_number
status
task identity
contract identity
schema identity
input snapshot
staged output metadata
committed output references
failure class
timestamps
```

Input snapshots are immutable after execution begins.

---

# 17. Execution Mutability

Execution records are append-oriented but may update while one attempt progresses.

Example status progression:

```text
created
→ queued
→ running
→ validating
→ committing
→ committed
```

or:

```text
running
→ failed
```

Once an Execution reaches a terminal state:

```text
committed
failed
stale
cancelled
```

its historical facts should not be rewritten except for narrowly defined recovery repair.

---

# 18. Event Store

The Event Store persists normalized internal Events.

It supports:

```text
received
processing
processed
ignored
retry_pending
dead_letter
```

Event body is logically immutable after persistence.

Processing metadata may change.

---

# 19. Event Persistence Guarantees

External events follow:

```text
normalize
↓
persist
↓
acknowledge provider
↓
process
```

This ensures the runtime can survive:

- Process crash.
- Container restart.
- Provider redelivery.
- Worker failure.

A persisted Event should not be lost because the runtime container restarts.

---

# 20. Event Deduplication

The Event Store should support uniqueness on:

```text
provider
+
provider_event_id
```

when provider identity exists.

Internal Events use unique:

```text
event_id
```

Operation-key idempotency remains a second line of protection.

---

# 21. Interaction Store

The Interaction Store owns long-lived human-interaction state.

Examples:

- Discord evidence investigation.
- Manual review.
- Paused Interviewer sessions.

Conceptual record:

```yaml
interaction:

  interaction_id: INT-0004

  job_id: JOB-0001

  interaction_type: evidence_investigation

  provider: discord

  provider_context:
    guild_id: ...
    channel_id: ...
    thread_id: ...
    last_seen_provider_message_id: ...
    last_seen_provider_created_at: ...

  professional_context:
    erq:
      artifact_id: ERQ-0011
      artifact_version: 1

  status: active

  created_at: ...
  updated_at: ...
```

Provider-specific metadata remains outside Runtime Job.

---

# 22. Interaction Messages

Interaction messages are stored separately from the Interaction record.

Conceptual table:

```text
interaction_messages
------------------------------------------------
message_id
interaction_id
provider
provider_message_id nullable
provider_created_at nullable
direction
message_type
content/reference
persisted_at
processed_at nullable
processed_by_continuation_id nullable
```

For inbound Discord human messages:

```text
provider = discord
provider_message_id = required
provider_created_at = required
persisted_at = required
```

For locally persisted outbound Interviewer messages awaiting Discord delivery:

```text
provider_message_id = null
provider_created_at = null
persisted_at = required
```

Provider identity should be unique within provider scope so duplicate gateway/reconciliation delivery cannot create duplicate stored messages.

Recommended uniqueness concept:

```text
UNIQUE(provider, provider_message_id)
WHERE provider_message_id IS NOT NULL
```

Exact SQLite syntax belongs in implementation.

Chronology semantics:

```text
provider_created_at
= provider-side conversational chronology

provider_message_id
= stable tie-breaker + dedupe identity

persisted_at
= local durability/audit timestamp
```

Inbound Discord conversation ordering must use:

```text
provider_created_at ASC
provider_message_id ASC
```

not local `persisted_at`.

This is necessary because live gateway arrival, reconnect recovery, and local scheduling can persist messages in a different order from provider chronology.

For inbound authorized human input, message persistence and Event persistence remain one SQLite transaction:

```text
BEGIN

insert Interaction Message
insert human_input_received Event referencing message_id

COMMIT
```

If the transaction fails:

```text
neither durable message receipt
nor human_input_received Event
is considered committed
```

The Event Store references `message_id` rather than duplicating full message content.


## Interviewer Message Batch Resolution

Before continuation invocation, resolve every currently committed authorized human message for the active Interaction where:

```text
processed_at IS NULL
```

Order the exact batch by:

```text
provider_created_at ASC
provider_message_id ASC
```

Both fields are required for inbound Discord messages before they are eligible for the batch.

The resulting `message_id` list is immutable for that continuation attempt.

Messages committed after batch resolution remain unprocessed and belong to the next continuation.

The exact batch boundary is included in continuation provenance/idempotency state.

## Interviewer Continuation Transaction

When a continuation consumes one or more unprocessed human messages and produces a new conversational Interviewer message:

```text
BEGIN

mark exact consumed human-message IDs processed
insert next Interviewer Interaction Message
update Interaction continuation metadata as needed

COMMIT
```

The human-message IDs are the immutable batch resolved before invocation. The transaction marks only those exact IDs processed.

The next Interviewer message is persisted before external Discord delivery.

On transaction failure:

```text
no consumed message is marked processed
AND
no next Interviewer message is committed
```

This keeps retry behavior deterministic.

If the continuation produces a completed Evidence Response rather than another conversational message, the professional artifact commit path owns completion semantics for that result; ordinary conversational-message processing must not independently finalize the professional result.

---

# 23. SQLite V0.1 Standard

V3 V0.1 standardizes on SQLite for runtime/control-plane persistence.

Recommended connection initialization:

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
```

Additional pragmas may be selected during implementation.

WAL mode supports:

- Concurrent readers.
- Serialized writes.
- Good performance for a single-container runtime.
- Crash-resistant journaling.

---

# 24. Single-Container SQLite Boundary

V0.1 assumes:

```text
one active RRS runtime container
→ one SQLite database
```

Multiple async tasks/workers may operate inside the same runtime process/container with correct concurrency control.

Do not run multiple independent Docker replicas concurrently against the same SQLite database file.

If horizontal scaling becomes necessary:

```text
migrate runtime/control-plane persistence to PostgreSQL or equivalent
```

Repository interfaces should make that migration possible.

---

# 25. Filesystem Artifact Store

Professional artifact content is stored on the persistent filesystem.

Recommended root:

```text
/data/artifacts
```

Benefits:

- Human inspectability.
- Easy backups.
- Native YAML/DOCX/PDF preservation.
- Simple immutable version layout.
- Reduced database blob complexity.
- Easier troubleshooting.

---

# 26. Artifact Write Process

Recommended artifact persistence flow:

```text
stage output
↓
validate
↓
write temporary file in persistent volume
↓
fsync / verify as appropriate
↓
compute content hash
↓
move/rename into immutable final path
↓
insert artifact metadata
↓
pointer commit
```

The exact filesystem durability mechanism should be validated during implementation.

---

# 27. Atomic File Placement

Where supported, artifact staging should use:

```text
temporary file
→ atomic rename
→ final immutable path
```

within the same filesystem.

This reduces risk of partially written committed artifact files.

---

# 28. Cross-Store Transaction Boundary

SQLite and filesystem cannot participate in one native ACID transaction.

Therefore V3 uses the logical commit model:

```text
persist immutable artifact content
↓
persist/verify artifact metadata
↓
compare-and-swap Runtime Job current pointers
```

If pointer commit fails:

```text
artifact may remain noncurrent
```

This is acceptable.

The unacceptable state is:

```text
Runtime Job points to artifact that was not successfully persisted.
```

---

# 29. Orphaned Artifact Tolerance

Immutable files may exist without becoming current because:

- Output became stale.
- Pointer commit conflicted.
- Coupled commit partially persisted.
- Recovery preserved diagnostics.

Such artifacts should be represented in metadata as:

```text
stale
orphaned
diagnostic
superseded
```

They must not appear as current professional state.

---

# 30. Coupled Product Persistence

Writer output:

```text
Targeted Resume
+
Writer Content Manifest
```

must become current together.

Example flow:

```text
persist Resume artifact
persist WCM artifact
verify both
↓
single SQLite transaction:
  update resume pointer
  update wcm pointer
  increment Runtime Job revision
  record commit metadata
```

If the SQLite transaction fails:

```text
previous Resume + WCM pointers remain current
```

New files remain noncurrent/orphaned until recovery or cleanup.

---

# 31. Runtime Database Transactions

Operations that mutate runtime state should use SQLite transactions.

Examples:

- Pointer commits.
- Runtime Job lifecycle transition + routing history append.
- Execution terminal status + committed outputs.
- Event-processing state updates.
- Interaction state transitions.

Where multiple records form one logical runtime state change, update them within one transaction when possible.

---

# 32. Routing Persistence

A routing transition commits one authoritative Runtime Job mutation:

```text
routing_history entry
+
lifecycle.phase
+
lifecycle.entered_at
+
Runtime Job revision increment
+
lifecycle_changed Event
```

inside one SQLite transaction.

If that transaction fails, none of those changes become authoritative.

The routing-history append must not succeed independently from the lifecycle transition, and the lifecycle transition must not become durable without its corresponding `lifecycle_changed` Event.

Trello synchronization happens afterward and is not part of the routing transaction.

---

# 33. Event and Command Persistence

Events persist before asynchronous processing.

Commands are durable when they represent work that must survive restart.

When Event processing produces one or more Commands, Command creation and Event completion are one SQLite transaction:

```text
BEGIN

derive deterministic command_dedupe_key where applicable
insert or reuse resulting Command(s) by dedupe key
mark Event processed

COMMIT
```

This transaction provides the V0.1 transactional Event-to-Command boundary.

Failure behavior:

```text
transaction commits
→ Commands are durable
→ Event is processed
```

```text
transaction fails
→ no resulting Command is committed
→ Event is not marked processed
→ Event remains recoverable/retryable
```

The runtime must never use:

```text
mark Event processed
→ later persist Command
```

because a crash between those steps can permanently lose required work.

Likewise, persisting the Command and only later marking the Event processed is safe only with Command deduplication; the atomic SQLite transaction is preferred and required when both records are local SQLite state.


## Nonprofessional Command Completion

When a nonprofessional Command changes authoritative SQLite-resident runtime state, its successful completion is one SQLite transaction:

```text
BEGIN

apply authoritative runtime mutation
persist required resulting Event(s)
mark Command completed

COMMIT
```

This prevents:

```text
state changed
→ crash
→ Command still appears pending
```

and:

```text
Command marked completed
→ crash
→ required resulting Event missing
```

If the transaction fails, the Command must remain nonterminal and eligible for deterministic recovery/retry.

Examples include:
- routing evaluation that commits a lifecycle transition,
- Interaction completion/cancellation,
- Job cancellation,
- retry scheduling,
- other local control-plane mutations.

### External Side-Effect Commands

SQLite cannot atomically commit with Discord, Trello, or another external provider.

For an external-side-effect Command, persistence should use durable local intent and reconciliation:

```text
1. Persist external action intent / delivery record.
2. Commit that intent locally.
3. Call external provider.
4. Persist provider result or provider identity.
5. Persist resulting Event if required.
6. Mark Command completed.
```

If the process fails between steps 3 and 4, recovery treats the outcome as ambiguous and reconciles provider state before repeating when possible.

The authoritative runtime mutation must not depend on an external projection transaction succeeding.

Projection failures are retried independently and may set runtime health to `degraded`.

---

# 34. SQLite Command Queue

V0.1 may use SQLite as the durable command/work queue.

Conceptual table:

```text
commands
------------------------------------------------
command_id
command_dedupe_key nullable
job_id
command_type
status
causation_event_id
payload
created_at
claimed_at
owner_runtime_instance_id
worker_id
lease_expires_at
completed_at
attempt_count
```

This avoids introducing Redis/RabbitMQ prematurely.

## Command Dedupe Key

Deterministic Commands produced from Events should carry:

```text
command_dedupe_key
```

Recommended derivation:

```text
hash(
  causation_event_id
  + command_type
  + canonical relevant payload identity
)
```

The persistence layer must prevent more than one durable Command from representing the same non-null dedupe key.

Conceptually:

```text
UNIQUE(command_dedupe_key)
WHERE command_dedupe_key IS NOT NULL
```

Exact SQLite index syntax belongs in implementation.

When Event processing retries:

```text
same Event
→ same intended Command
→ same command_dedupe_key
→ existing Command reused
```

This rule reduces queue noise and duplicate runtime actions.

It does not replace:
- provider Event deduplication,
- Event-processing idempotency,
- professional `operation_key`,
- Runtime Job CAS protection.

---

# 34.1 Runtime Instance Identity

Every daemon process start creates a new:

```text
runtime_instance_id
```

Example:

```text
RUN-20260823-ABC123
```

The identifier is stable only for that daemon process lifetime.

It is used to record ownership/provenance for:

```text
Execution ownership
Event processing leases
Command processing leases
runtime logs
restart reconciliation
```

Recommended runtime-instance record:

```yaml
runtime_instance:
  runtime_instance_id: RUN-20260823-ABC123
  started_at: ...
  build_identity: ...
  process_metadata: ...
  stopped_at: null
```

A clean shutdown may set `stopped_at`, but recovery must not depend on clean shutdown occurring.

A new process must never reuse the prior process's `runtime_instance_id`.

Runtime instance identity is operational metadata, not professional state.

---

# 35. Worker Claiming and Lease Lifecycle

Events and Commands use short-lived processing leases.

Claim metadata:

```text
runtime_instance_id
worker_id
lease_expires_at
```

Canonical state flow:

```text
pending / retry_pending
→ processing
→ completed
```

Claim occurs atomically.

If processing needs more time:

```text
current owner renews lease before expiry
```

If:

```text
lease expires
```

or:

```text
owner_runtime_instance_id belongs to a prior daemon instance
```

the work becomes eligible for recovery/reclaim according to retry policy.

The implementation must prevent two active owners from simultaneously treating the same queue record as exclusively claimed.

## Lease Scope

A lease covers only the immediate processing of the Event or Command record.

It must not be used as the durable representation of a long-running professional provider call.

For `schedule_operation`:

```text
claim Command
→ derive/reuse operation_key
→ create or reuse active Execution durably
→ mark Command completed
→ release Command ownership
```

Then:

```text
Execution
→ owns professional provider invocation
→ may remain running independently of the completed scheduling Command
```

The Command lease therefore remains short even if the professional model call takes minutes.

Similarly:

```text
Event lease
→ covers Event processing and durable Command creation
→ does not remain held while downstream Command/Execution work runs
```

This separates queue recovery from professional Execution recovery.

Architectural requirement:

> Abandoned queue work is recovered by lease/ownership rules; interrupted model work is recovered from Execution state.

---

# 36. Restart Recovery

On startup, the runtime should reconcile persistent state.

Recommended startup procedure:

1. Open SQLite.
2. Enable required pragmas.
3. Verify/migrate schema.
4. Create a new `runtime_instance_id` for this daemon start.
5. Find Events in:
   - `processing`
   - `retry_pending`
6. Find Commands in:
   - `processing`
   - `retry_pending`
7. Find Executions in:
   - `running`
   - `validating`
   - `committing`
8. Reconcile incomplete commits.
9. Repair expired worker leases and ownership from prior runtime instances.
10. Validate active Runtime Job execution references.
11. Re-synchronize projections where necessary.
12. Enter Manual Review when deterministic recovery is unsafe.

---

# 37. Execution Recovery

Startup recovery evaluates incomplete Executions by status and owning runtime instance.

## `running`

A `running` Execution represents an active provider invocation owned by a specific runtime instance.

If that runtime instance is no longer alive:

```text
running
→ failed
```

with failure detail equivalent to:

```text
failure_class = invocation_failure
reason = runtime_interrupted
```

The original physical attempt cannot resume its lost network/provider call.

If retry policy permits:

```text
same operation_key
→ new execution_id
→ next attempt_number
```

The old attempt remains immutable history.

## `validating`

If:

```text
status == validating
AND
/data/staging/<execution_id>/ contains complete verifiable output
```

recovery may resume validation from staged bytes.

If staging is missing or corrupt:

```text
attempt → failed
```

and normal retry policy applies.

## `committing`

For:

```text
status == committing
```

inspect:

```text
artifact files
artifact metadata
commit-group state
Runtime Job pointers
declared freshness dependencies
```

Possible outcomes:

```text
nothing committed
→ retry commit or fail safely

files exist, SQLite commit absent, inputs still fresh
→ finish/retry atomic professional commit

Runtime Job pointers and commit state already advanced
→ repair Execution state to committed

newer conflicting professional state exists
→ mark old output stale/noncurrent
```

Do not blindly re-invoke the professional operation.

No Execution may remain indefinitely `running`, `validating`, or `committing` merely because its prior runtime process disappeared.

---

# 38. Event Recovery

Events left:

```text
processing
```

with expired ownership after restart should be returned to:

```text
retry_pending
```

or equivalent claimable state.

Idempotency guarantees safe reprocessing.

---

# 38.1 Evidence Response / Interaction Completion Ordering

Professional Evidence Response commit and Interaction completion use separate authoritative transactions.

Professional commit transaction:

```text
Evidence Response artifact metadata
+
RuntimeJob.unintegrated_evidence_responses ADD
+
Execution committed
+
artifact_committed Event
```

After that transaction succeeds, a nonprofessional `complete_interaction` Command performs:

```text
BEGIN
Interaction.status = completed
Interaction.completed_at = ...
persist interaction_completed Event
mark complete_interaction Command completed
COMMIT
```

The second transaction must never run before the exact Evidence Response for the current ERQ/version is confirmed committed.

Recovery rule:

```text
Interaction active/paused
+
committed Evidence Response for exact current ERQ/version
→ schedule/retry complete_interaction
```

This repairs the safe crash window where professional state committed before Interaction completion.

The reverse state:

```text
Interaction completed
+
no committed Evidence Response for current ERQ/version
```

is invalid and requires repair/manual review rather than pretending investigation succeeded.

---

# 39. Interaction Recovery

Active/paused Interactions must survive container restart and Discord reconnect.

Persistence must be sufficient to reconstruct:

- Which Job is involved.
- Which ERQ is active.
- Which Discord thread/channel corresponds to it.
- Current Interaction status.
- Last known provider message boundary.
- Last processed local Interaction message.
- Whether Interviewer continuation can resume.

For Discord-backed Interactions, startup/reconnect recovery performs provider reconciliation:

```text
load active/paused Interaction
→ identify thread_id
→ load last_seen_provider_message_id / provider timestamp boundary
→ fetch provider messages after/beyond the known boundary
→ deduplicate by provider_message_id
→ persist unseen authorized human messages
→ persist corresponding human_input_received Events
→ resume Interaction Processor
```

If strict provider "after" semantics are unavailable, the adapter may fetch a recent bounded window and use persisted provider-message uniqueness to determine what is unseen.

The Interaction Store must retain provider chronology fields needed for deterministic ordering and reconciliation:

```text
provider_created_at
provider_message_id
```

Local `persisted_at` is retained separately for audit/recovery timing but is not a substitute for provider chronology.

Recovered messages use the same atomic message + Event persistence rule as live gateway messages.

Discord itself must not be the only place the runtime knows which messages have already been observed.

---

# 40. Runtime Job Recovery

A Runtime Job should never depend on in-memory-only state.

After restart, it should be possible to reconstruct current control-plane state entirely from:

```text
SQLite
+
artifact filesystem
```

External integrations may then be resynchronized.

---

# 41. Projection Reconciliation

Trello and Discord status projections should be recoverable from authoritative persistence.

Example:

```text
Trello card says Evaluation
Runtime Job says Complete
```

The runtime should repair Trello to reflect:

```text
Complete
```

not rewrite Runtime Job to match Trello.

---

# 42. Persistence Authority Levels

V3 defines three durability classes.

## Authoritative

Must survive restart/loss of integrations:

```text
Runtime Job
Professional artifacts
Artifact metadata
Executions
Events
Commands
Interactions
```

## Derived / Rebuildable

May be recreated:

```text
Indexes
Caches
Search indexes
Materialized views
Derived summaries
```

## Projection

External operational presentation:

```text
Trello board/list placement
Trello comments
Discord status messages
```

Projection loss must not destroy professional/runtime truth.

---

# 43. Repository Interfaces

Handlers and routers should not directly execute SQL or filesystem writes.

Recommended abstractions:

```text
RuntimeJobRepository

ArtifactRepository

ExecutionRepository

EventRepository

CommandRepository

InteractionRepository
```

SQLite/filesystem implementations satisfy these ports.

---

# 44. Artifact Repository Interface

Conceptually:

```python
class ArtifactRepository(Protocol):

    async def stage(...):
        ...

    async def persist(...):
        ...

    async def get(
        artifact_id,
        artifact_version,
    ):
        ...

    async def metadata(...):
        ...
```

Exact implementation should preserve immutable semantics.

---

# 45. Runtime Job Repository Interface

Conceptually:

```python
class RuntimeJobRepository(Protocol):

    async def get(job_id):
        ...

    async def compare_and_swap(
        job_id,
        expected_revision,
        mutation,
    ):
        ...
```

The repository owns runtime persistence semantics.

---

# 46. Database Schema Migrations

SQLite schema changes must be versioned.

Recommended approach:

```text
runtime database schema version
+
ordered migrations
```

On startup:

```text
detect current schema
↓
apply compatible migrations
↓
start runtime
```

Do not mutate database structure ad hoc.

A lightweight migration library or custom migration runner may be selected during implementation.

---

# 47. Professional Artifact Schema Migration

Professional artifact schemas are separate from runtime database schema.

Existing immutable professional artifacts should not be silently rewritten merely because a newer professional schema exists.

If a historical artifact requires migration for current use, migration behavior must be explicit and version-preserving.

---

# 48. Backup Model

A complete V0.1 backup should include:

```text
/data/rrs.db

/data/artifacts/
```

and configuration necessary to reconstruct deployment, excluding secrets.

Trello and Discord do not need to be treated as backup authorities.

---

# 49. SQLite Backup Safety

Do not naively copy a live SQLite database file while assuming consistency.

Use a safe SQLite backup mechanism, such as:

- SQLite backup API.
- `VACUUM INTO`.
- Controlled application shutdown.
- Other documented consistent snapshot mechanism.

The artifact directory and database snapshot should represent a reasonably consistent backup point.

---

# 50. Docker Volume Backup

Recommended deployment may use:

```yaml
volumes:
  - rrs-data:/data
```

or:

```yaml
volumes:
  - /host/path/rrs-data:/data
```

Backup strategy should capture the persistent data path.

---

# 51. Secrets

Secrets do not belong in SQLite artifact/professional records unless an integration system specifically requires encrypted secret storage in the future.

V0.1 should use environment variables or Docker secrets for:

- LLM/API credentials.
- Trello credentials.
- Discord bot token.
- Webhook secrets.

Secrets must not appear in:

- Professional artifacts.
- Event payloads.
- Runtime Job.
- Logs.
- Trello comments.
- Discord messages.
- Source control.

---

# 52. Configuration

Non-secret environment-specific configuration may include:

```text
database path
artifact root path
logging level
retry limits
worker settings
Trello board/list IDs
Discord guild/channel IDs
```

Configuration should not be embedded in professional artifact schemas.

---

# 53. Container Lifecycle

The application container should be replaceable without data loss.

Expected:

```text
docker stop
docker remove
deploy new image
mount same /data
start
↓
runtime resumes
```

Startup recovery reconciles incomplete operations.

---

# 54. Graceful Shutdown

On normal container stop:

1. Stop accepting new commands.
2. Finish or safely pause short-running operations when possible.
3. Persist current worker state.
4. Release processing leases.
5. Close SQLite connections cleanly.

Long-lived human interactions remain persisted and resume after restart.

---

# 55. Filesystem Permissions

The container process requires read/write access to:

```text
/data/rrs.db
/data/artifacts/
```

Artifact files should not be casually writable by unrelated processes.

Container user/UID/GID strategy should be documented during deployment design.

---

# 56. Disk Failure / Capacity

V3 should detect persistence failures such as:

```text
disk full
read-only filesystem
permission failure
database locked beyond policy
SQLite corruption
artifact hash mismatch
```

These are workflow-critical.

Expected behavior:

```text
health → recoverable_failure or blocked
```

depending on safe recovery.

Do not continue professional operations when authoritative persistence cannot be trusted.

---

# 57. SQLite Corruption / Integrity Checks

V0.1 should support operational integrity verification.

Potential tools:

```sql
PRAGMA integrity_check;
```

This should not run unnecessarily on every transaction, but should be available for diagnostics and maintenance.

---

# 58. Artifact Integrity Verification

On read, the runtime may optionally compare file content hash with stored metadata.

At minimum, recovery/diagnostic tooling should support:

```text
stored SHA-256
vs
actual file SHA-256
```

Mismatch should be treated as authoritative-storage integrity failure.

---

# 59. Cleanup Policy

Immutable committed professional artifacts should not be deleted automatically.

Temporary staging files may be cleaned after:

- successful commit,
- failed validation,
- stale execution,
- configured retention period.

Orphaned/diagnostic artifacts should follow an explicit retention policy.

Do not remove them while they are needed for recovery or audit.

---

# 60. Data Retention

V0.1 should favor preservation over aggressive cleanup.

Professional artifacts, Executions, routing history, and material Events are valuable for:

- debugging,
- process improvement,
- evidence provenance,
- architecture validation.

Retention optimization can occur after real storage behavior is observed.

---

# 61. Query Requirements

Persistence should efficiently support questions such as:

```text
What is JOB-0001's current state?

What is its current JEA?

What artifacts were produced by EXEC-0042?

What Execution produced Resume v4?

What Events caused the Job to return to Analysis?

Which Jobs are blocked?

Which Events are dead-lettered?

Which Interactions are waiting for human response?

Which artifacts are orphaned/stale?

What was the complete artifact lineage for this final Resume?
```

---

# 62. Observability Integration

Persistence should expose structured runtime state to observability tooling without requiring professional artifact mutation.

Runtime metrics/logs may derive from:

- Jobs.
- Executions.
- Events.
- Commands.
- Interactions.
- Projection sync state.

---

# 63. Future PostgreSQL Migration

The architecture should preserve migration capability.

Migration trigger examples:

- Multiple runtime replicas required.
- Higher concurrent write volume.
- Multi-user hosted deployment.
- Stronger transactional requirements across workers.
- Remote database hosting.

Because handlers depend on repository interfaces:

```text
SQLiteRuntimeJobRepository
```

may later become:

```text
PostgresRuntimeJobRepository
```

without redesigning professional operations.

---

# 64. No Shared SQLite Across Replicas

Explicit V0.1 constraint:

> Do not mount one SQLite database into multiple concurrently active RRS runtime containers.

SQLite over shared/network filesystems may also have locking/durability limitations depending on storage implementation.

V0.1 deployment assumes local/persistent storage owned by one active container instance.

---

# 65. Docker Health

Container health checks should eventually distinguish:

```text
process alive
database accessible
artifact root writable
runtime not catastrophically blocked
```

A healthy container does not imply every Runtime Job is healthy.

Job-level health remains in Runtime Job state.

---

# 66. V0.1 Acceptance Criteria

The Persistence Model is acceptable when:

- [ ] Runtime Job current state persists durably.
- [ ] Runtime Job revision supports optimistic concurrency.
- [ ] Routing-history append, lifecycle mutation, revision increment, and `lifecycle_changed` Event commit atomically.
- [ ] Professional artifacts persist immutably by ID/version.
- [ ] Professional artifact contents remain separate from runtime metadata.
- [ ] Artifact content hashes support integrity verification.
- [ ] Current artifact pointers reference only successfully persisted artifacts.
- [ ] JER/current collections are persistable.
- [ ] Execution history survives restart.
- [ ] Event history and retry state survive restart.
- [ ] Command/work state can survive restart.
- [ ] Event-produced deterministic Commands support a unique non-null `command_dedupe_key`.
- [ ] Reprocessing the same causal Event reuses the existing deduplicated Command rather than inserting another equivalent Command.
- [ ] Event-produced Commands and Event successful completion commit atomically when both are SQLite-resident.
- [ ] Nonprofessional SQLite-local Command mutation, required resulting Event(s), and Command completion commit atomically.
- [ ] External provider effects use durable local intent and reconciliation rather than pretending cross-system atomicity.
- [ ] Failed Event-to-Command transactions leave the Event retryable and do not lose required work.
- [ ] Human Interaction state survives restart.
- [ ] Trello and Discord remain reconstructable projections.
- [ ] Coupled Resume/WCM pointer updates are atomic in SQLite.
- [ ] Cross-filesystem/SQLite commits tolerate orphaned artifacts without exposing invalid current state.
- [ ] Crash recovery can reconcile incomplete executions.
- [ ] Duplicate Event/Command processing remains safe.
- [ ] SQLite + filesystem can run inside one Docker container.
- [ ] `/data` can be mounted persistently.
- [ ] Container replacement does not lose authoritative state.
- [ ] Repository interfaces preserve future PostgreSQL migration.
- [ ] Multiple active containers sharing one SQLite file are explicitly unsupported.
- [ ] Backup can capture SQLite plus artifact filesystem.
- [ ] Secrets remain outside authoritative professional/runtime records.

---

# Next Design Step

After this model is accepted, define the:

> **V3 Trello Projection Model**

The Trello Projection Model should specify:

- Board/list design.
- Runtime Job ↔ card relationship.
- Lifecycle-to-list mapping.
- Card fields and metadata.
- Routing comments.
- Projection synchronization.
- Allowed human control actions.
- Webhook normalization.
- Drift repair.
- Manual Review presentation.