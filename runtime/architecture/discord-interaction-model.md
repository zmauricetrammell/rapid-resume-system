# RRS V3 Discord Interaction Model

## Status
Draft V0.8 — FIX-016, FIX-017, FIX-018, FIX-019, FIX-035, FIX-037, and FIX-038 applied

## Purpose
The Discord Interaction Model defines how V3 uses Discord as the human conversation surface for Evidence Request investigation.

Discord is not authoritative professional storage. The Interaction Store is authoritative for conversational runtime state, and the schema-conformant Evidence Response is the authoritative professional result.

V0.1 standardizes on:

```text
one RRS Discord channel
+
one Discord thread per Evidence Request
+
one active Evidence Request investigation per Runtime Job at a time
```

## Core Invariants

1. Discord is a human interaction surface, not professional truth.
2. One Evidence Request maps to one Discord thread.
3. ERQs are investigated serially per Runtime Job in V0.1.
4. Interaction state persists independently from Discord.
5. Discord provider IDs remain outside professional artifacts.
6. Human messages and their `human_input_received` Events persist atomically before Interviewer continuation.
7. Duplicate Discord events/messages are safe.
8. Interviewer continuation is restart-safe and does not depend on in-memory model state.
9. Every continuation reloads the current ERQ, persisted conversation, and Interviewer resources.
10. A thread is not complete merely because conversation stops.
11. Investigation completes only when a valid Evidence Response commits.
12. Discord messages never directly modify JERs, JEA, or other professional artifacts.
13. Evidence Responses enter the normal evidence-integration path after commit.
14. Provider failures must not corrupt professional state.
15. Interaction history must survive container restart.
16. An inbound authorized human message and its `human_input_received` Event persist atomically in one SQLite transaction.
17. On reconnect/startup, every active or paused Discord Interaction reconciles provider thread history after the last known provider message so messages received during runtime downtime are not lost.
18. When Interviewer continuation produces another conversational turn, consumed human-message state and the persisted next Interviewer message commit atomically.
19. Evidence Response professional commit and Interaction completion are separate authoritative mutations; Interaction completion occurs only after the exact Evidence Response has committed successfully.
20. Each Interviewer continuation consumes one stable ordered batch containing all currently unprocessed authorized human messages available at batch resolution time.
21. Every persisted Discord Interaction Message records provider chronology fields sufficient for deterministic ordering and reconnect reconciliation.
22. Interviewer continuation produces exactly one typed result: `ConversationTurn` or `CompletedProfessionalArtifact`; V0.1 completed artifacts are Evidence Responses.

## 1. Discord Topology

```text
Discord Server
└── RRS Channel
    ├── JOB-0001 · ERQ-0011 · Direct management scope
    ├── JOB-0002 · ERQ-0015 · Azure migration dates
    └── JOB-0003 · ERQ-0018 · Vendor ownership
```

Thread naming:

```text
<JOB-ID> · <ERQ-ID> · <short investigation topic>
```

The topic should be derived from structured ERQ context and avoid unnecessary sensitive detail.

## 2. Interaction Record

```yaml
interaction:
  interaction_id: INT-0004
  job_id: JOB-0001
  interaction_type: evidence_investigation

  professional_context:
    evidence_request:
      artifact_type: evidence_request
      artifact_id: ERQ-0011
      artifact_version: 1

  provider:
    type: discord
    guild_id: "..."
    channel_id: "..."
    thread_id: "..."

  status: pending
  last_processed_message_id: null

  created_at: ...
  updated_at: ...
  completed_at: null
```

Interaction status:

```text
pending
active
paused
completed
cancelled
```

`completed` requires a committed Evidence Response. `cancelled` does not resolve the ERQ.

## 3. Serial Investigation Per Job

```text
ERQ-0011
→ investigate
→ Evidence Response commits
→ complete interaction

ERQ-0012
→ investigate
→ Evidence Response commits

ERQ-0013
→ ...
```

Different Runtime Jobs may investigate concurrently.

The next ERQ is selected deterministically. V0.1 should use a stable ordering such as oldest unresolved active ERQ first.

## 4. Interaction Creation

```text
Runtime Job enters investigation
↓
no active interaction
↓
select next active ERQ without completed response
↓
create Interaction
↓
create Discord thread
↓
persist provider IDs
↓
invoke Interviewer for first turn
↓
post first question
↓
status → active
```

If Discord thread creation fails, keep the Interaction `pending` and retry provider synchronization.

## 5. Stateless Interviewer Continuation

No long-lived in-memory model session is required.

Each continuation receives the exact persisted context and immutable human-message batch defined by the Invocation Model.

The result is:

```text
InterviewerContinuationResult
```

with exactly one tagged member:

```text
ConversationTurn
CompletedProfessionalArtifact
```

`ConversationTurn`:

```yaml
kind: conversation_turn
message:
  content: "..."
  message_type: question
```

`CompletedProfessionalArtifact`:

```yaml
kind: completed_professional_artifact
artifact:
  artifact_type: evidence_response
  content: ...
```

Rules:
- `ConversationTurn` persists as the next Interviewer Interaction Message before Discord delivery.
- `CompletedProfessionalArtifact` enters the normal professional output pipeline.
- It does not directly mark the Interaction complete.
- The Evidence Response must extract, validate, stage, pass freshness checks, and commit before `complete_interaction` may run.
- A continuation result that cannot be resolved to exactly one tagged member is invalid and retryable according to professional invocation policy.

Professional continuity comes from persistence, not provider chat-session memory.

## 6. Message Record

```yaml
message:
  message_id: MSG-0091
  interaction_id: INT-0004

  provider:
    type: discord
    provider_message_id: "..."
    provider_created_at: 2026-08-23T16:40:12.345-07:00

  direction: human
  message_type: answer
  content: "..."

  persisted_at: 2026-08-23T16:40:13.002-07:00
  processed_at: null
  processed_by_continuation_id: null

  delivery:
    status: delivered
```

Required chronology fields for Discord-backed messages:

```text
provider_message_id
provider_created_at
persisted_at
```

Meanings:

- `provider_message_id` — Discord's stable message identity. Used for deduplication and deterministic tie-breaking.
- `provider_created_at` — provider-side message creation time. Primary conversational ordering field.
- `persisted_at` — local runtime persistence time. Audit/recovery metadata only; it must not replace provider chronology for conversation ordering.

Recommended directions:

```text
human
interviewer
```

For provider-backed outbound Interviewer messages, retain the Discord `provider_message_id` and `provider_created_at` after successful delivery/reconciliation.

For locally persisted Interviewer messages awaiting Discord delivery:

```text
provider_message_id = null
provider_created_at = null
```

until provider acknowledgement/reconciliation supplies them.

Local `message_id` remains the authoritative runtime identity.

## 6.1 Deterministic Conversation Ordering

Discord-backed messages are ordered by:

```text
provider_created_at ASC
provider_message_id ASC
```

when both provider chronology fields are known.

For an outbound Interviewer message that has been persisted locally but not yet delivered to Discord, local conversation reconstruction may temporarily order it by its persisted continuation position. Once provider chronology is available, the provider fields are recorded without changing the logical continuation history.

For inbound human messages, `provider_created_at` and `provider_message_id` are required before the message is accepted into an Interviewer continuation batch.

Do not use:

```text
persisted_at
```

as the primary ordering field for inbound Discord conversation because gateway delay, reconnect recovery, or database scheduling can make local persistence order differ from provider order.


## 7. Message Authority Boundary

Interaction messages are conversational runtime records.

They do not become authoritative evidence directly.

```text
Discord conversation
↓
Evidence Response
↓
evidence integration
↓
authoritative JER state
```

## 7.1 Inbound Human Message Transaction

Discord message ingestion is durable before Interviewer continuation.

For each authorized, unseen human message:

```text
BEGIN SQLITE TRANSACTION

insert Interaction Message
persist human_input_received Event

COMMIT
```

The Event references the persisted message:

```yaml
event_type: human_input_received

payload:
  interaction_id: INT-0004
  message_ref: MSG-0091
```

The full message content remains in the Interaction Store.

The Event body does not duplicate the human message.

If the transaction fails:

```text
message is not treated as durably received
AND
human_input_received is not emitted
```

The provider event may be retried/reconciled.

If the transaction succeeds:

```text
message exists durably
AND
human_input_received exists durably
```

so restart cannot leave a stored human answer with no continuation trigger.

Duplicate provider delivery is safe because the Interaction Message store deduplicates by provider message identity before inserting another message/Event pair.

The same transaction and deduplication path is used for both live gateway messages and messages discovered during restart/reconnect reconciliation.

The runtime must not use:

```text
persist message
→ later emit human_input_received in a separate transaction
```

because a crash between those steps could permanently strand human input.

# 8. Human Message Ingress

```text
human posts message
↓
Discord event received
↓
adapter verifies + normalizes
↓
persist message
↓
persist human_input_received Event
↓
acknowledge provider
↓
schedule continuation
```

Do not invoke Interviewer before the human message is durable.

Deduplicate using Discord provider message/event identity.

## 9. Message Processing

A human message becomes processed only after it has been included in a successful Interviewer continuation.

```yaml
processed_at: ...
```

A retry must not treat the same human turn as new input twice.

## 10. Conversation Continuation

If more information is needed, Interviewer returns one next conversational action:

```text
question
clarification request
confirmation request
```

The runtime:

```text
persist interviewer message
↓
post to Discord
↓
status stays active
↓
wait for human
```

No Evidence Response is committed yet.

The integration should preserve the Interviewer task's one-primary-question-at-a-time behavior.

## 11. Evidence Response Completion

```text
Interviewer returns Evidence Response
↓
stage
↓
validate evidence-response schema
↓
validate exact ERQ ID/version
↓
freshness check
↓
professional commit transaction:
  persist immutable Evidence Response
  append pointer to unintegrated_evidence_responses
  finalize Execution
  persist artifact_committed
↓
artifact_committed is durable
↓
schedule/reuse complete_interaction Command
↓
Interaction completion transaction:
  mark Interaction completed
  persist interaction_completed
  mark complete_interaction Command completed
```

Professional Evidence Response commit and Interaction completion are separate authoritative mutations.

Investigation is professionally complete only after the Evidence Response commit succeeds and the Interaction is then completed through the deterministic runtime completion path.

## 12. ERQ Resolution Boundary

Evidence Response creation does not automatically resolve or remove an ERQ.

The ERQ remains active until evidence integration and later professional re-analysis determine its originating Material Evidence Need is:

```text
resolved
```

or:

```text
no_longer_material
```

## Human Message Batch Resolution

Before each Interviewer continuation, the Interaction Processor resolves one immutable batch containing all currently unprocessed authorized human messages for the active Interaction.

Example:

```text
MSG-101 arrives
MSG-102 arrives before continuation starts

batch:
  MSG-101
  MSG-102

→ one Interviewer continuation
```

Order the batch deterministically:

```text
provider_created_at ASC
provider_message_id ASC
```

Once continuation starts, the batch is immutable. Human messages arriving after batch resolution remain unprocessed and belong to the next continuation.

The runtime records the exact consumed message IDs in continuation provenance so duplicate wake-up Events over the same boundary resolve to the same logical continuation input.

## Continuation Commit Boundary

When the Interaction Processor invokes the Interviewer, it consumes the exact immutable batch resolved by the Human Message Batch Resolution rule.

If the Interviewer returns another conversational turn, the runtime commits:

```text
BEGIN SQLITE TRANSACTION

mark consumed human-message batch processed
persist next Interviewer message / continuation state

COMMIT
```

The next Interviewer message must be persisted before delivery to Discord.

This prevents both failure modes:

```text
human messages marked processed
→ crash
→ next Interviewer question lost
```

and:

```text
next Interviewer question persisted
→ crash
→ same human messages still appear unprocessed
→ duplicate Interviewer continuation
```

If the transaction fails:

```text
consumed human messages remain unprocessed
AND
next Interviewer message is not committed
```

The same continuation may then be retried safely.

After successful local commit:

```text
persisted Interviewer message
→ Discord delivery
```

Discord delivery remains an external side effect and may be retried/reconciled independently.

If the Interviewer instead returns a completed Evidence Response, consumed-message processing must be coordinated with the professional artifact commit path rather than treating the result as an ordinary conversational turn.

## 13. Stale ERQ Handling

If an interaction is based on:

```text
ERQ-0011 v1
```

but the current active ERQ is now:

```text
ERQ-0011 v2
```

the interaction result is stale.

The runtime must:

- preserve conversation for audit,
- prevent stale Evidence Response from becoming current,
- stop or supersede the stale interaction,
- continue against the current ERQ version.

## 14. Outbound Discord Messages

Persist an Interviewer message before provider delivery.

```text
persist
↓
post
↓
record Discord provider_message_id
```

Provider retry must not trigger a new professional Interviewer turn.

Outbound delivery should have a durable state such as:

```text
pending
delivered
failed
```

## 15. Discord Failure

Temporary provider failure must not alter professional state.

Interaction may become `paused` while delivery/input retry occurs.

Runtime health may become `degraded`. Repeated inability to conduct required human interaction may escalate according to retry/recovery policy.

## Evidence Response Commit and Interaction Completion

A completed Interviewer result is a professional Evidence Response, not merely conversation state.

The professional commit path owns:

```text
Evidence Response artifact persistence
+
RuntimeJob.unintegrated_evidence_responses ADD
+
Execution finalization
+
artifact_committed Event
```

Only after that exact Evidence Response commit succeeds may the runtime complete the Interaction.

Canonical ordering:

```text
Interviewer returns Evidence Response
↓
professional Evidence Response commit succeeds
↓
artifact_committed Event is durable
↓
complete_interaction Command
↓
BEGIN SQLite transaction
  Interaction.status = completed
  Interaction.completed_at = ...
  persist interaction_completed Event
  mark complete_interaction Command completed
COMMIT
```

The Interaction Processor does not mark the Interaction completed inside the professional artifact commit transaction.

This separation keeps professional artifact authority and conversational runtime authority distinct.

### Crash Recovery

The safe asymmetry is:

```text
Evidence Response committed
Interaction still active
```

because startup/recovery can detect:

```text
active Interaction
+
exact committed Evidence Response for current ERQ/version
```

and complete the Interaction deterministically.

The unsafe asymmetry must not occur:

```text
Interaction completed
Evidence Response not committed
```

Therefore Interaction completion must always follow successful professional commit.

Discord thread closure/status updates are projection effects and occur after authoritative Interaction completion.


## 16. Restart and Reconnect Recovery

Discord gateway delivery is not the sole durability mechanism for human input.

On daemon restart or Discord reconnect, the runtime reconciles every active or paused Discord Interaction against its provider thread.

Required flow:

```text
load active/paused Interaction
↓
load last known persisted provider message boundary
↓
fetch Discord thread messages newer than that boundary
↓
filter to authorized human messages
↓
deduplicate by provider_message_id
↓
for each unseen message:
  BEGIN SQLite transaction
    persist Interaction Message
    persist human_input_received Event
  COMMIT
↓
resume normal Interaction processing
```

The runtime must not assume that all messages sent while it was offline will later arrive through live gateway events.

### Reconciliation Boundary

Each Interaction must retain enough provider metadata to identify the recovery boundary.

Required Discord reconciliation fields include:

```text
thread_id
last_seen_provider_message_id
last_seen_provider_created_at
```

The boundary values are derived from persisted provider chronology, not local persistence timestamps.

The exact Discord pagination/cursor mechanism belongs in the adapter.

If Discord cannot query strictly after a message ID, the adapter may fetch a bounded recent window and rely on provider-message deduplication.

### Deterministic Ordering

Recovered messages are persisted in stable provider chronology.

Recommended ordering:

```text
provider_created_at
then provider_message_id as a stable tie-breaker
```

This allows live and recovered messages to reconstruct the same conversation order.

### Failure Behavior

If provider reconciliation temporarily fails:

```text
Interaction remains active/paused
→ no persisted human input is discarded
→ reconciliation retries
```

The runtime must not mark the Interaction complete or infer that no human response exists merely because Discord is temporarily unavailable.

If the provider thread no longer exists or cannot be deterministically reconciled after retry policy is exhausted:

```text
runtime health / Interaction
→ recoverable failure or manual review
```

according to the applicable recovery policy.

Discord remains an interaction surface; the Interaction Store remains authoritative for what the runtime has durably observed and processed.

## 17. Interaction Timeout

Human delay is not evidence failure.

A configurable inactivity threshold may transition:

```text
active → paused
```

New human input may resume the Interaction.

Timeout must not mark the ERQ resolved or unsupported.

## 18. Manual Cancellation

Interaction cancellation:

```text
status → cancelled
```

does not:

- resolve the ERQ,
- create negative evidence,
- generate an Evidence Response,
- complete the Runtime Job.

Runtime recovery/manual-review rules decide what happens next.

## 19. Discord Security

V0.1 should restrict accepted interaction to configured:

```text
guild_id
RRS channel_id
authorized user IDs
```

Validate provider authenticity and event identity where supported.

Discord secrets stay in environment variables or Docker secrets, never in:

- artifacts,
- Runtime Job,
- Events,
- messages,
- logs,
- source control.

## 20. Logging Boundary

Generic logs/events should reference:

```text
interaction_id
message_id
provider_message_id
```

rather than duplicate full conversation text.

The Interaction Store owns the actual conversation.

## 21. Events and Commands

Relevant normalized Events:

```text
interaction_required
interaction_started
human_input_received
interaction_paused
interaction_completed
```

Relevant Commands:

```text
open_interaction
continue_interaction
pause_interaction
close_interaction
```

Preferred flow:

```text
Discord message
↓
normalized Event
↓
continue_interaction Command
↓
Interaction Processor
↓
Interviewer invocation
```

The Discord adapter never invokes the Interviewer directly.

## 22. Interaction Processor

A long-lived Interaction Processor coordinates conversation without owning professional reasoning.

Responsibilities:

- load Interaction,
- load exact ERQ,
- load ordered conversation,
- identify unprocessed human input,
- construct Interviewer invocation,
- persist Interviewer continuation,
- identify Evidence Response output,
- submit completed Evidence Response to the normal commit framework.

The normal professional commit framework still owns:

```text
staging
schema validation
freshness
artifact persistence
pointer commit
event emission
```

## 23. Thread Finalization

After valid Evidence Response commit:

1. Interaction → `completed`.
2. Post short completion notice.
3. Archive/lock thread when appropriate.
4. Start the next ERQ thread if another active request remains.

Discord remains historical conversation, not professional authority.

## 24. Projection Reconciliation

Runtime Interaction state is authoritative.

If Discord disagrees:

```text
runtime wins
```

Examples:

- Runtime says completed, thread remains open → repair Discord.
- Thread manually archived, runtime remains active → do not mark interaction complete.

## 25. MVP Non-Goals

V0.1 does not require:

- parallel ERQ investigations within one Job,
- Trello,
- a web dashboard,
- rich Discord buttons/modals,
- multiple human collaborators,
- voice input,
- job creation through natural-language Discord messages,
- Discord artifact storage,
- Discord as a runtime database.

## 26. V0.1 Acceptance Criteria

- [ ] Interviewer continuation result is a tagged union: `ConversationTurn` or `CompletedProfessionalArtifact`.
- [ ] V0.1 completed Interviewer professional artifact is restricted to Evidence Response.
- [ ] Typed completion still enters normal professional commit processing before Interaction completion.

- [ ] One configured RRS Discord channel is used.
- [ ] One ERQ maps to one Discord thread.
- [ ] ERQs are investigated serially per Runtime Job.
- [ ] Every Interaction references an exact ERQ version.
- [ ] Interaction state persists independently from Discord.
- [ ] Human messages persist before continuation.
- [ ] Duplicate Discord events/messages are safe.
- [ ] Interviewer continuation requires no in-memory session.
- [ ] Continuation context is reconstructable after restart.
- [ ] Conversation continuation and Evidence Response completion are distinct.
- [ ] Investigation completes only after valid Evidence Response commit.
- [ ] Evidence Response references exact ERQ version.
- [ ] Stale ERQ output cannot become current.
- [ ] Evidence Response does not automatically resolve/remove ERQ.
- [ ] Outbound delivery retries do not regenerate Interviewer turns.
- [ ] Discord failure does not corrupt professional state.
- [ ] Discord messages cannot directly mutate JER/JEA.
- [ ] Interaction completion emits generic runtime Events.
- [ ] Discord projection can be repaired from runtime state.
- [ ] MVP functions without Trello.

## Next Design Step

Because Trello is deferred, the next MVP architecture artifact should be the:

> **V3 MVP Control Surface Model**

It should define the smallest CLI or HTTP interface needed to:

- create a Runtime Job,
- supply/select a Target Job,
- inspect Job state,
- inspect current artifact pointers,
- retry recoverable work,
- cancel a Job,
- inspect Manual Review state.