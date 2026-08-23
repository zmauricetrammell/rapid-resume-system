# RRS V3 Discord Interaction Model

## Status
Draft V0.3 — FIX-016 and FIX-017 applied

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

Each continuation uses:

```text
Evidence Request
+
persisted ordered conversation
+
latest unprocessed human response
+
Interviewer contract
+
investigate_evidence_request task
+
Evidence Response schema
```

and produces either:

```text
next conversational turn
```

or:

```text
completed Evidence Response
```

Professional continuity comes from persistence.

## 6. Message Record

```yaml
message:
  message_id: MSG-0091
  interaction_id: INT-0004
  provider: discord
  provider_message_id: "..."
  direction: human
  message_type: answer
  content: "..."
  created_at: ...
  processed_at: null

  delivery:
    status: delivered
```

Recommended directions:

```text
human
interviewer
```

Recommended message types:

```text
question
answer
clarification
confirmation
system_notice
```

For MVP, storing conversation text in SQLite is acceptable.

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
persist immutable Evidence Response
↓
append pointer to unintegrated_evidence_responses
↓
mark Interaction completed
↓
emit events
```

Only then is the investigation professionally complete.

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

Recommended fields include:

```text
thread_id
last_seen_provider_message_id
last_seen_provider_created_at
```

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