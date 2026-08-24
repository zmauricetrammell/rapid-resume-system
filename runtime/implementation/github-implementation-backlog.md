# RRS V3 GitHub Implementation Backlog

## Status

Implementation Planning — Phase 9

## Purpose

This document converts the completed V3 implementation plans into an actionable GitHub backlog.

It defines:

- implementation milestones,
- issue ordering,
- dependency relationships,
- issue scope,
- acceptance criteria,
- test expectations,
- architecture traceability,
- implementation gates.

The backlog is designed so development can begin without reopening settled architecture decisions.

The governing rule is:

```text
architecture
→ implementation plan
→ GitHub issue
→ code
→ tests
```

---

# 1. Backlog Principles

1. Issues should implement one bounded responsibility.
2. Foundational infrastructure precedes integrations.
3. Vertical slices prove behavior before broad feature expansion.
4. Every transaction-owning issue includes rollback and crash/recovery tests.
5. Every issue references the relevant implementation-planning artifact.
6. External integrations must implement established ports rather than redefine runtime semantics.
7. Architecture changes discovered during coding are surfaced explicitly rather than hidden inside implementation.
8. Issues should be small enough to review but large enough to produce coherent behavior.
9. Gate milestones are not complete until their required tests pass.
10. The `integrate_evidence` professional-task binding remains an explicit dependency.

---

# 2. Recommended Labels

Create or reuse labels equivalent to:

```text
type:implementation
type:test
type:integration
type:infrastructure
type:architecture-gap
type:documentation

area:domain
area:persistence
area:transactions
area:commands-events
area:execution
area:commit
area:routing
area:operations
area:interactions
area:discord
area:evidence
area:provider
area:recovery
area:cli
area:deployment

priority:p0
priority:p1
priority:p2

gate:a
gate:b
gate:c

blocked
```

Exact naming may follow repository conventions.

---

# 3. Recommended Milestones

```text
M1 — Runtime Foundation
M2 — Runtime Core
M3 — First Professional Vertical Slice
M4 — Recovery Core
M5 — Remaining Professional Operations
M6 — Human Interaction
M7 — External Integrations
M8 — End-to-End MVP
M9 — Operator Controls and Hardening
```

---

# 4. M1 — Runtime Foundation

## Goal

Create the Python runtime skeleton, canonical domain model, Operation Specification core, and persistent storage foundation.

---

## ISSUE-001 — Scaffold Python runtime project

### Labels

```text
type:implementation
area:domain
priority:p0
```

### Scope

Create:

```text
runtime/pyproject.toml
runtime/src/rrs/
runtime/tests/
runtime/migrations/
```

Initial package directories:

```text
domain
ports
application
infrastructure
integrations
cli
bootstrap
```

Configure:

```text
Python version
test runner
type checking
lint/format
coverage
```

### Acceptance

- runtime package installs;
- empty test suite runs;
- package imports resolve;
- CI can execute runtime tests.

### Depends On

```text
none
```

### Traceability

```text
package-interface-plan.md
implementation-dependency-graph.md P0
```

---

## ISSUE-002 — Implement canonical IDs and enums

### Scope

Implement:

```text
JobId
ExecutionId
CommandId
EventId
InteractionId
MessageId
FailureId
ArtifactId
OperationKey
RuntimeInstanceId
InvocationId
RoutingDecisionId
CommitGroupId
```

and canonical enums from `python-domain-model.md`.

### Acceptance

- canonical persisted string values defined once;
- ID types are distinct;
- unit tests verify enum/string stability;
- no duplicate enum definitions elsewhere.

### Depends On

```text
ISSUE-001
```

---

## ISSUE-003 — Implement artifact and resource domain values

### Scope

Implement:

```text
ArtifactVersion
ArtifactRef
ArtifactMetadata
ArtifactCommitGroup
StagedArtifact
ResourceRef
SchemaRef
```

### Acceptance

- immutable;
- `ArtifactVersion >= 1`;
- semantic resource hash distinct from Git provenance;
- unit tests pass.

### Depends On

```text
ISSUE-002
```

---

## ISSUE-004 — Implement RuntimeJob domain aggregate

### Scope

Implement:

```text
RuntimeJob
RuntimeJobIdentity
LifecycleState
OperationState
InteractionProjection
HealthState
ProfessionalState
RoutingDecision
```

### Acceptance

- immutable aggregate;
- revision invariant enforced;
- RuntimeJob contains artifact references, not bodies;
- interaction and health consistency checks implemented;
- deterministic collection representation.

### Depends On

```text
ISSUE-002
ISSUE-003
```

---

## ISSUE-005 — Implement RuntimeJob mutation contracts

### Scope

Implement typed mutations:

```text
SetPointerMutation
CollectionAddMutation
CollectionRemoveMutation
CollectionReplaceMutation
CollectionUpsertVersionMutation
LifecycleTransitionMutation
OperationStateMutation
InteractionProjectionMutation
HealthMutation
```

### Acceptance

- no generic untyped RuntimeJob write API;
- invalid pointer/collection combinations rejected;
- unit tests cover semantic mutation construction.

### Depends On

```text
ISSUE-004
```

---

## ISSUE-006 — Implement Execution, Event, Command, Interaction, Failure domain records

### Scope

Implement domain records from `python-domain-model.md`.

### Acceptance

- immutable;
- terminal-state validation;
- Event/Command envelopes support typed payload evolution;
- Failure distinct from exceptions;
- tests cover construction invariants.

### Depends On

```text
ISSUE-002
ISSUE-003
```

---

## ISSUE-007 — Implement Operation Specification domain model

### Scope

Implement:

```text
OperationSpecification
ProfessionalBinding
RetrievalSpecification
OutputContract
PointerMutationAuthority
InputSnapshot
DependencyFingerprint
```

### Acceptance

- immutable;
- exact lifecycle/input/output/mutation declarations represented;
- semantic specification hash field represented.

### Depends On

```text
ISSUE-002
ISSUE-003
```

---

## ISSUE-008 — Implement Operation Specification Registry and validation

### Scope

Implement:

```text
OperationSpecificationRegistry
RegistryValidator
OperationSpecificationHasher
OperationRegistryHasher
```

### Acceptance

Registry rejects:

```text
duplicate operation_type
missing handler
missing resource
invalid lifecycle
invalid output group
invalid pointer target
invalid mutation type
invalid retrieval config
```

Hashing:

```text
semantic resource change → new hash
Git-only change → same semantic hash
```

### Depends On

```text
ISSUE-007
```

---

## ISSUE-009 — Add six V0.1 Operation Specifications

### Scope

Define:

```text
generate_analysis
request_evidence
investigate_evidence_request
integrate_evidence
generate_resume
evaluate_resume
```

### Acceptance

- registry loads all six;
- all validate;
- lifecycle/input/output/mutation authority matches `operation-specifications.md`;
- `integrate_evidence` real professional task binding remains explicitly marked unresolved if not yet confirmed.

### Depends On

```text
ISSUE-008
```

---

## ISSUE-010 — Implement SQLite migration runner and base schema

### Scope

Implement migration runner and initial schema from `sqlite-schema.md`.

### Acceptance

- empty DB migrates;
- migration history recorded;
- WAL enabled;
- foreign keys enabled;
- startup failure blocks readiness;
- schema tests pass.

### Depends On

```text
ISSUE-001
ISSUE-006
```

---

## ISSUE-011 — Implement core SQLite repositories

### Scope

Implement repositories for:

```text
RuntimeJob
Artifacts
Executions
Events
Commands
Interactions
InteractionMessages
Failures
RoutingDecisions
InvocationProvenance
RuntimeInstances
```

### Acceptance

- domain round trips;
- no SQLite rows leak outward;
- deterministic RuntimeJob reconstruction;
- partial unique indexes enforced.

### Depends On

```text
ISSUE-004
ISSUE-006
ISSUE-010
```

---

## ISSUE-012 — Implement SQLite UnitOfWork

### Scope

Implement one transaction-bound connection exposing all repositories.

### Acceptance

- multiple repository writes commit together;
- rollback restores all;
- no repository autocommit inside active UoW;
- concurrency conflict mapping works.

### Depends On

```text
ISSUE-011
```

---

# 5. M2 — Runtime Core

## Goal

Implement deterministic Event/Command processing, professional Execution, artifact commit, and routing.

---

## ISSUE-013 — Implement Clock and deterministic ID ports/fakes

### Scope

Implement:

```text
Clock
SystemClock
FakeClock
IdGenerator
DeterministicIdGenerator
production ID generator
```

### Acceptance

- runtime services can be tested without global time/randomness;
- generated IDs satisfy canonical format.

### Depends On

```text
ISSUE-002
```

---

## ISSUE-014 — Implement Event repository claim/recovery semantics

### Scope

Implement atomic Event claim, lease, retry, processed state.

### Acceptance

- duplicate provider identity blocked;
- expired lease reclaimable;
- claim is atomic;
- integration tests pass.

### Depends On

```text
ISSUE-011
ISSUE-012
```

---

## ISSUE-015 — Implement Command repository claim/dedupe semantics

### Scope

Implement Command claim, dedupe, retry, completion.

### Acceptance

- dedupe key unique;
- lease claim atomic;
- expired lease reclaimable;
- completed Commands not reclaimed.

### Depends On

```text
ISSUE-011
ISSUE-012
```

---

## ISSUE-016 — Implement EventProcessor and Event→Command transaction

### Scope

Implement TX-005.

### Acceptance

- required Commands and Event processed state commit together;
- duplicate Event processing reuses Commands;
- crash tests prove no processed Event without durable required Command.

### Depends On

```text
ISSUE-014
ISSUE-015
```

---

## ISSUE-017 — Implement CommandProcessor

### Scope

Implement Command worker dispatch and handler registry.

### Acceptance

- claims Commands;
- dispatches to deterministic handler;
- failed processing becomes retry/failure state correctly;
- Command lease not held beyond intended handler boundary.

### Depends On

```text
ISSUE-015
```

---

## ISSUE-018 — Implement create_job Command

### Scope

Implement TX-001.

### Acceptance

Creates atomically:

```text
Target Job metadata
RuntimeJob revision 1
Target Job pointer
pinned JER set
job_created Event
Command completion
```

- same Command retry never creates second Job;
- orphan file case recoverable.

### Depends On

```text
ISSUE-012
ISSUE-017
filesystem primitives from ISSUE-024
```

---

## ISSUE-019 — Implement OperationKeyBuilder and FreshnessChecker

### Scope

Implement semantic operation identity and commit freshness.

### Acceptance

- identity/freshness dependencies remain distinct;
- Git/runtime instance does not affect operation_key;
- unrelated Job revision does not imply stale;
- material dependency changes behave correctly.

### Depends On

```text
ISSUE-007
ISSUE-009
```

---

## ISSUE-020 — Implement ExecutionRepository active-operation rules

### Scope

Complete Execution behavior beyond generic persistence.

### Acceptance

- one nonterminal active Execution per `operation_key`;
- attempt numbers unique;
- completed history retained;
- dead runtime ownership identifiable.

### Depends On

```text
ISSUE-011
ISSUE-019
```

---

## ISSUE-021 — Implement schedule_operation Command

### Scope

Implement TX-006.

### Acceptance

- eligible Operation Specification resolved;
- operation_key built;
- compatible Execution reused or new attempt created;
- RuntimeJob operation projection consistent;
- Command completed atomically with durable scheduling state.

### Depends On

```text
ISSUE-009
ISSUE-017
ISSUE-019
ISSUE-020
```

---

## ISSUE-022 — Implement ExecutionWorker and BaseOperationHandler

### Scope

Implement shared professional execution framework.

### Acceptance

- Execution marked running before provider call;
- provider call outside write transaction;
- handler receives resolved Operation Specification;
- no routing inside handler;
- no direct current-pointer mutation.

### Depends On

```text
ISSUE-021
ISSUE-026
```

---

## ISSUE-023 — Implement ArtifactFileStore port and local filesystem store

### Scope

Implement:

```text
stage
finalize
verify
read
staging cleanup primitives
```

Canonical:

```text
/data/artifacts
/data/staging/<execution_id>
```

### Acceptance

- immutable finalization;
- existing artifact version never overwritten;
- content hash verification;
- path traversal blocked.

### Depends On

```text
ISSUE-003
```

---

## ISSUE-024 — Implement artifact version allocation and commit groups

### Scope

Implement transaction-safe artifact version allocation and commit-group persistence.

### Acceptance

- no out-of-transaction MAX+1 race;
- coupled artifact metadata supported;
- commit groups retained for diagnostics/recovery.

### Depends On

```text
ISSUE-011
ISSUE-012
ISSUE-023
```

---

## ISSUE-025 — Implement PointerMutationValidator

### Scope

Validate requested mutations against Operation Specification authority.

### Acceptance

- unauthorized target rejected;
- wrong mutation type rejected;
- role identity grants no mutation rights;
- unit tests cover every operation's allowed mutations.

### Depends On

```text
ISSUE-005
ISSUE-009
```

---

## ISSUE-026 — Implement FakeProfessionalInvoker and output extractor fixtures

### Scope

Implement fake professional adapter and deterministic output extraction.

### Acceptance

Can simulate:

```text
valid output
invalid schema
malformed output
timeout
provider failure
```

No runtime code special-cases fake behavior.

### Depends On

```text
ISSUE-006
ISSUE-007
```

---

## ISSUE-027 — Implement CommitCoordinator single-output commit

### Scope

Implement TX-008.

### Acceptance

Atomically commits:

```text
artifact metadata
authorized pointer/collection mutation
RuntimeJob revision
Execution committed
artifact_committed
```

Tests:

```text
stale
CAS conflict
unauthorized mutation
schema failure
missing file
rollback/crash
```

### Depends On

```text
ISSUE-012
ISSUE-019
ISSUE-023
ISSUE-024
ISSUE-025
```

---

## ISSUE-028 — Implement Router and predicate registry

### Scope

Implement deterministic routing engine and all core predicates.

### Acceptance

- only current committed state used;
- no prose inference;
- all core predicates covered by unit tests;
- Router does not invoke professional provider.

### Depends On

```text
ISSUE-004
ISSUE-009
```

---

## ISSUE-029 — Implement evaluate_routing Command transactions

### Scope

Implement TX-012 and TX-013.

### Acceptance

Transition path atomically commits:

```text
RoutingDecision
lifecycle
revision
lifecycle_changed
Command completion
```

No-op path:

```text
Command completion only
```

CAS conflict recomputes predicate.

### Depends On

```text
ISSUE-017
ISSUE-028
ISSUE-012
```

---

# 6. Gate A — Runtime Core

## ISSUE-030 — Gate A runtime-core conformance test suite

### Labels

```text
type:test
gate:a
priority:p0
```

### Acceptance

All pass:

```text
Operation registry validation
SQLite migrations
UoW atomicity
Event→Command
Command dedupe/leases
Execution operation identity
single-output professional commit
routing transactions
import boundaries
no network in write transactions
```

### Depends On

```text
ISSUE-013 through ISSUE-029
```

---

# 7. M3 — First Professional Vertical Slice

## ISSUE-031 — Implement `generate_analysis` handler

### Scope

Implement operation-specific input resolution/retrieval query mechanics for `generate_analysis`.

### Acceptance

- uses specification authority;
- no direct routing;
- no hidden output declaration;
- outputs staged JEA only.

### Depends On

```text
ISSUE-009
ISSUE-022
ISSUE-027
```

---

## ISSUE-032 — Implement FakeEvidenceSource

### Scope

Deterministic provider-neutral evidence retrieval fake.

### Acceptance

Supports:

```text
matches
zero matches
unavailable
timeout
```

### Depends On

```text
domain retrieval types
```

---

## ISSUE-033 — Complete `generate_analysis` vertical slice

### Scope

Implement and test:

```text
create_job
→ routing
→ schedule generate_analysis
→ Execution
→ FakeEvidenceSource
→ FakeProfessionalInvoker
→ JEA
→ commit
→ artifact_committed
→ routing
```

### Acceptance

- real SQLite;
- real filesystem;
- restart reconstruction;
- duplicate Event/Command safe;
- provenance persisted;
- exactly one current JEA.

### Depends On

```text
ISSUE-030
ISSUE-031
ISSUE-032
```

---

## ISSUE-034 — Gate B crash/restart suite for first professional round trip

### Labels

```text
type:test
gate:b
priority:p0
```

### Acceptance

Crash/restart tested at:

```text
Execution running
provider return
file finalization
professional commit
artifact_committed processing
routing
```

Converges without duplicate current professional state.

### Depends On

```text
ISSUE-033
```

---

# 8. M4 — Recovery Core

## ISSUE-035 — Implement runtime startup identity and recovery coordinator

### Scope

Implement runtime instance persistence and recovery-before-ready sequencing.

### Acceptance

- new runtime instance per daemon start;
- recovery runs before workers accept new work;
- dead prior instance identifiable.

### Depends On

```text
ISSUE-034
```

---

## ISSUE-036 — Implement interrupted Execution recovery

### Scope

Implement TX-021.

### Acceptance

- dead-owned running Execution becomes terminal interrupted/failed;
- old provider call not resumed;
- retry creates new attempt under same operation_key;
- old attempt retained.

### Depends On

```text
ISSUE-035
ISSUE-020
```

---

## ISSUE-037 — Implement Event and Command lease recovery

### Scope

Implement TX-022/TX-023.

### Acceptance

- expired/dead ownership becomes retryable;
- schedule_operation reconciles existing Execution before retry;
- dedupe prevents duplicate downstream work.

### Depends On

```text
ISSUE-035
ISSUE-014
ISSUE-015
```

---

## ISSUE-038 — Implement professional commit recovery

### Scope

Implement TX-025.

### Acceptance

Handles:

```text
finalized orphan file
stale finalized output
pointer advanced / terminal metadata mismatch
staging from failed attempt
```

Never advances current pointer based solely on file presence.

### Depends On

```text
ISSUE-035
ISSUE-027
```

---

## ISSUE-039 — Implement FailureService and health transitions

### Scope

Implement TX-018/TX-019.

### Acceptance

- material Failure persistent;
- Job health/failure pointer atomic;
- resolved Failure retained;
- health recomputed from unresolved material failures.

### Depends On

```text
ISSUE-011
ISSUE-012
```

---

## ISSUE-040 — Recovery crash-injection conformance suite

### Acceptance

Covers:

```text
Event lease
Command lease
Execution ownership
professional commit
routing
startup reconstruction
```

### Depends On

```text
ISSUE-036
ISSUE-037
ISSUE-038
ISSUE-039
```

---

# 9. M5 — Remaining Professional Operations

## ISSUE-041 — Implement `request_evidence`

### Acceptance

- current JEA required;
- current ERQs optionally supplied;
- ERQ schema validated;
- `active_erqs ADD/UPSERT_VERSION` only;
- routing after commit.

### Depends On

```text
Gate B
recovery core
```

---

## ISSUE-042 — Implement coupled Resume/WCM CommitCoordinator path

### Scope

Implement TX-009.

### Acceptance

- both files finalized;
- both metadata rows;
- commit group;
- both current pointers;
- one Job revision;
- one `artifact_committed`;
- never mixed old/new pair.

### Depends On

```text
ISSUE-027
```

---

## ISSUE-043 — Implement `generate_resume`

### Acceptance

- Writer receives only authorized evidence/resources;
- Resume + WCM both produced;
- coupled commit used;
- no evidence retrieval by Writer.

### Depends On

```text
ISSUE-042
```

---

## ISSUE-044 — Implement `evaluate_resume`

### Acceptance

- current Resume/WCM/JEA/Target required;
- Evaluation schema validated;
- only `evaluation SET`;
- routing uses Evaluation schema fields.

### Depends On

```text
ISSUE-043
```

---

## ISSUE-045 — Resolve approved `integrate_evidence` professional task binding

### Labels

```text
type:documentation
area:operations
priority:p0
```

### Scope

Confirm exact approved Researcher task resource or create/review one through normal architecture/professional-governance process.

### Acceptance

- one exact contract/task binding exists;
- Operation Specification validates;
- no hidden professional instructions in Python.

### Depends On

```text
none technically
```

This should be resolved before ISSUE-047.

---

## ISSUE-046 — Implement evidence integration multi-artifact transaction

### Scope

Implement TX-010.

### Acceptance

- multiple JER versions atomic;
- consumed Evidence Responses removed atomically;
- one revision;
- one `artifact_committed`;
- no partial integration.

### Depends On

```text
ISSUE-027
```

---

## ISSUE-047 — Implement `integrate_evidence`

### Acceptance

- exact approved task used;
- authorized input/output only;
- integration transaction used;
- re-analysis, not integration itself, decides evidence sufficiency.

### Depends On

```text
ISSUE-045
ISSUE-046
```

---

## ISSUE-048 — Straight-through non-human workflow vertical test

### Scope

Test:

```text
analysis
→ resume
→ evaluation
→ complete/product loop
```

and evidence-request branch where no human Interaction is yet executed.

### Depends On

```text
ISSUE-041
ISSUE-043
ISSUE-044
ISSUE-047
```

---

# 10. M6 — Human Interaction

## ISSUE-049 — Implement authoritative Interaction repositories and projection service

### Scope

Finalize:

```text
InteractionRepository behavior
InteractionMessageRepository behavior
InteractionProjectionSynchronizer
```

### Acceptance

- one active Interaction per Job;
- exact provider message dedupe;
- authoritative/projection distinctions preserved.

### Depends On

```text
ISSUE-011
ISSUE-012
```

---

## ISSUE-050 — Implement `open_interaction` Command

### Acceptance

Atomic:

```text
Interaction creation
RuntimeJob projection
revision
Event
Command completion
```

### Depends On

```text
ISSUE-049
ISSUE-017
```

---

## ISSUE-051 — Implement human-message batching

### Scope

Resolve exact ordered unprocessed authorized human-message batch.

### Acceptance

- provider chronology used;
- exact message IDs returned;
- persisted-at order does not control batch order;
- duplicate messages excluded by uniqueness.

### Depends On

```text
ISSUE-049
```

---

## ISSUE-052 — Implement Interviewer conversational continuation

### Scope

Implement TX-015 for `ConversationTurn`.

### Acceptance

Atomic:

```text
exact human batch processed
next Interviewer outbound turn persisted
```

Discord delivery occurs after commit.

### Depends On

```text
ISSUE-022
ISSUE-051
```

---

## ISSUE-053 — Implement completed Evidence Response commit

### Scope

Implement TX-011.

### Acceptance

Atomic:

```text
Evidence Response metadata
unintegrated response ADD
exact human messages processed
Execution committed
RuntimeJob revision
artifact_committed
```

### Depends On

```text
ISSUE-027
ISSUE-051
```

---

## ISSUE-054 — Implement `complete_interaction` Command

### Scope

Implement TX-016.

### Acceptance

Atomic:

```text
Interaction completed
RuntimeJob projection completed
revision
interaction_completed
Command completed
```

### Depends On

```text
ISSUE-050
ISSUE-053
```

---

## ISSUE-055 — Implement Interaction recovery

### Scope

Handle:

```text
committed Evidence Response + active Interaction
projection mismatch
paused/resume recovery
```

### Acceptance

- safe state repairs deterministically;
- ambiguous state enters Failure/manual review.

### Depends On

```text
ISSUE-049
ISSUE-054
ISSUE-039
```

---

## ISSUE-056 — Fake Interaction vertical test

### Scope

Use synthetic inbound messages + FakeProfessionalInvoker/FakeDiscordDelivery.

### Acceptance

Test:

```text
ERQ
→ Interaction
→ conversation turns
→ Evidence Response
→ complete_interaction
→ integration handoff
```

with crash between Evidence Response commit and Interaction completion.

### Depends On

```text
ISSUE-052
ISSUE-053
ISSUE-054
ISSUE-055
```

---

# 11. M7 — External Integrations

## ISSUE-057 — Implement Google Drive EvidenceSource adapter

### Acceptance

Provider-neutral output for:

```text
matches
zero matches
auth failure
timeout
invalid source read
```

Stable retrieval fingerprint.

### Depends On

```text
EvidenceSource port
Gate B
```

---

## ISSUE-058 — Implement real professional provider adapter

### Scope

Implement selected provider behind `ProfessionalInvoker`.

### Acceptance

- translates InvocationBundle;
- records provider/model/request provenance;
- normalizes timeout/rate-limit/provider failures;
- no session memory required for correctness.

### Depends On

```text
Gate B
operation resources
```

---

## ISSUE-059 — Implement Discord message normalization and ingress

### Acceptance

- provider IDs/timestamps preserved;
- duplicates converge;
- inbound human message transaction used;
- authorization filtering enforced.

### Depends On

```text
ISSUE-049
```

---

## ISSUE-060 — Implement durable Discord outbound delivery

### Scope

Implement local delivery intent and acknowledgement/reconciliation semantics.

### Acceptance

- outbound turn locally durable before send;
- ambiguous timeout reconciled;
- duplicate send avoided where safely possible.

### Depends On

```text
ISSUE-052
```

---

## ISSUE-061 — Implement Discord reconnect reconciler

### Acceptance

- unseen messages fetched after downtime;
- local dedupe applied;
- canonical chronology preserved;
- Interaction resumes from SQLite authority.

### Depends On

```text
ISSUE-059
ISSUE-060
ISSUE-055
```

---

## ISSUE-062 — External adapter contract test suite

### Scope

Contract tests for:

```text
ProfessionalInvoker
EvidenceSource
Discord
```

### Depends On

```text
ISSUE-057
ISSUE-058
ISSUE-061
```

---

# 12. M8 — End-to-End MVP

## ISSUE-063 — Full fake-provider end-to-end workflow

### Scope

Real runtime, SQLite, filesystem; fake external services.

Flow:

```text
Target Job
→ analysis
→ evidence request
→ investigation
→ Evidence Response
→ integration
→ re-analysis
→ Resume/WCM
→ Evaluation
→ complete
```

### Acceptance

- no hidden in-memory state required;
- all authoritative artifacts persisted;
- routing correct;
- all recoverable states converge.

### Depends On

```text
M5
M6
```

---

## ISSUE-064 — Full failure/recovery scenario suite

### Required scenarios

```text
professional timeout
EvidenceSource failure
invalid professional output
stale output
duplicate Event
duplicate Command
duplicate Discord message
crash during Execution
crash after file finalization
crash during professional commit
crash between Evidence Response and Interaction completion
expired leases
manual-review escalation
```

### Depends On

```text
ISSUE-063
M4
```

---

## ISSUE-065 — Gate C conformance review

### Labels

```text
gate:c
priority:p0
```

### Acceptance

- all Gate C tests pass;
- architecture import rules pass;
- no deferred Analyst/Custodian/Trello semantics introduced;
- complete E2E succeeds;
- recovery suite succeeds.

### Depends On

```text
ISSUE-064
```

---

# 13. M9 — Operator Controls and Hardening

## ISSUE-066 — Implement Job query services

### Scope

Implement:

```text
JobQueryService
ArtifactQueryService
FailureQueryService
```

### Depends On

```text
core repositories
```

---

## ISSUE-067 — Implement RuntimeControlService

### Scope

Mutating control facade that persists Commands.

### Acceptance

- no direct authoritative state mutation;
- create/retry/cancel actions enter normal runtime flow.

### Depends On

```text
Command control plane
```

---

## ISSUE-068 — Implement CLI

### Commands

```text
rrs job create
rrs job show
rrs job list
rrs job artifacts
rrs job retry
rrs job cancel
rrs job review
```

### Acceptance

- writes issue Commands;
- reads use query services;
- exact IDs shown;
- secrets not exposed.

### Depends On

```text
ISSUE-066
ISSUE-067
```

---

## ISSUE-069 — Implement startup/readiness and worker supervision

### Scope

Complete:

```text
StartupCoordinator
worker supervisor
runtime readiness
graceful shutdown
```

### Acceptance

Startup order follows deployment model and recovery completes before ready.

### Depends On

```text
M4
```

---

## ISSUE-070 — Add structured logging and diagnostic context

### Required context

```text
job_id
command_id
event_id
execution_id
operation_key
interaction_id
failure_id
runtime_instance_id
```

### Acceptance

- diagnostics useful;
- authoritative state not dependent on logs;
- sensitive content not dumped unnecessarily.

---

## ISSUE-071 — Implement Docker MVP packaging

### Scope

Single-container image and persistent `/data` volume.

### Acceptance

- migrations run;
- recovery runs;
- readiness correct;
- SQLite/artifact paths durable;
- runtime restarts cleanly.

### Depends On

```text
ISSUE-069
```

---

## ISSUE-072 — Define backup and restore procedure

### Scope

Document/test safe preservation of:

```text
/data/rrs.db
/data/artifacts/
```

### Acceptance

- WAL-safe database backup approach;
- restored instance reconstructs Runtime Jobs/artifacts correctly.

### Depends On

```text
ISSUE-071
```

---

## ISSUE-073 — Staging garbage collection

### Scope

Clean terminal/reconciled `/data/staging/<execution_id>` safely.

### Acceptance

- never deletes active/unreconciled staging;
- stale/orphan diagnostics preserved where policy requires.

### Depends On

```text
commit recovery
```

---

## ISSUE-074 — Final implementation conformance audit

### Scope

Compare implemented MVP against:

```text
11 architecture models
implementation planning documents
Operation Specifications
transaction matrix
test plan
```

### Acceptance

Result:

```text
PASS
or
explicit architecture/implementation discrepancy register
```

No silent divergence accepted.

### Depends On

```text
M8
M9 implementation issues
```

---

# 14. Critical Path

Primary critical path:

```text
ISSUE-001
→ 002
→ 004
→ 010
→ 011
→ 012
→ 014/015
→ 016/017
→ 019/020/021
→ 022
→ 023/024/025
→ 027
→ 028/029
→ 030
→ 031/032/033
→ 034
```

After Gate B, development can branch more aggressively.

---

# 15. Parallelizable Work

After domain stabilization:

```text
Operation Registry
SQLite Persistence
Filesystem Artifact Store
```

can proceed in parallel.

After Gate B:

```text
Recovery
Google Drive adapter
real professional provider
remaining operation handlers
```

can proceed in parallel with controlled interface stability.

Discord should wait until Interaction Core exists.

---

# 16. Backlog Blockers

Known explicit blocker:

```text
integrate_evidence real invocation
→ approved Researcher integration task binding
```

Other external prerequisites may include:

```text
provider credentials
Google Drive credentials/access
Discord bot/workspace configuration
```

These should not block fake-provider runtime implementation.

---

# 17. Issue Template for Implementation Work

Recommended body:

```text
## Objective

## Architecture / Planning References

## Scope

## Out of Scope

## Dependencies

## Implementation Requirements

## Transaction Boundary
(if applicable)

## Failure / Recovery Requirements

## Tests Required

## Acceptance Criteria

## Architecture Change Trigger
```

---

# 18. Issue Template — Transaction Owner

For transaction-owning issues, add:

```text
## Atomic Writes

## Pre-Transaction External/File Work

## CAS / Concurrency Behavior

## Idempotency

## Crash Injection Points

## Recovery Interpretation
```

This keeps transaction semantics visible during code review.

---

# 19. Pull Request Expectations

Each implementation PR should include:

```text
linked issue
tests
type/static checks
architecture/import checks
migration changes where relevant
planning-doc update only if implementation detail legitimately changes
```

If code requires architecture semantic change:

```text
do not merge as implementation-only PR
```

Open architecture discrepancy/change first.

---

# 20. Milestone Exit Criteria

## M1

```text
domain + registry + persistence + UoW stable
```

## M2

```text
Gate A passes
```

## M3

```text
Gate B passes
```

## M4

```text
crash/restart recovery converges
```

## M5

```text
all non-human professional operations work
```

## M6

```text
human Interaction works with fakes
```

## M7

```text
external adapters satisfy ports/contracts
```

## M8

```text
Gate C passes
```

## M9

```text
operator/deployment hardening complete
```

---

# 21. Recommended Immediate First Sprint

Do not start all issues at once.

Start with:

```text
ISSUE-001  scaffold runtime
ISSUE-002  IDs/enums
ISSUE-003  artifact/resource values
ISSUE-004  RuntimeJob aggregate
ISSUE-005  mutation contracts
ISSUE-006  Execution/Event/Command/Interaction/Failure records
```

Then proceed to:

```text
ISSUE-007
ISSUE-008
ISSUE-010
ISSUE-011
ISSUE-012
```

That establishes the software foundation without external-service noise.

---

# 22. Backlog Traceability

| Planning Artifact | Backlog Use |
|---|---|
| `implementation-inventory.md` | component completeness |
| `python-domain-model.md` | ISSUE-002–009 domain contracts |
| `sqlite-schema.md` | ISSUE-010–012 persistence |
| `transaction-matrix.md` | transaction-owning issues and crash tests |
| `package-interface-plan.md` | package ownership/import boundaries |
| `operation-specifications.md` | six professional operation issues |
| `implementation-dependency-graph.md` | milestone/order/dependencies |
| `test-plan.md` | test requirements and Gate A/B/C |

---

# 23. Planning Phase Completion

With this backlog, implementation planning has produced:

```text
implementation-inventory.md
python-domain-model.md
sqlite-schema.md
transaction-matrix.md
package-interface-plan.md
operation-specifications.md
implementation-dependency-graph.md
test-plan.md
github-implementation-backlog.md
```

The implementation phase can now begin without another design phase.

---

# 24. Phase 9 Acceptance Criteria

The GitHub backlog is complete when:

- [ ] every major implementation component has an issue;
- [ ] issues are dependency ordered;
- [ ] Gate A/B/C are represented explicitly;
- [ ] transaction-owning issues require transaction tests;
- [ ] recovery is implemented before external integration is considered complete;
- [ ] external adapters remain replaceable;
- [ ] `integrate_evidence` task-resource dependency is explicit;
- [ ] operator/deployment hardening is scheduled after functional MVP;
- [ ] final implementation conformance audit exists;
- [ ] first sprint can begin immediately.

## Result

**IMPLEMENTATION PLANNING COMPLETE — READY TO CREATE GITHUB ISSUES AND BEGIN DEVELOPMENT**