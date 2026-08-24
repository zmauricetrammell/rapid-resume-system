# RRS V3 Test Plan

## Status

Implementation Planning — Phase 8

## Purpose

This document defines the test architecture for the RRS V3 MVP runtime.

It translates the frozen architecture and implementation plans into executable verification categories.

The test strategy must prove not only that the happy path works, but that the runtime preserves correctness across:

- duplicate delivery,
- retries,
- stale inputs,
- compare-and-swap conflicts,
- partial failures,
- process crashes,
- restart/recovery,
- provider outages,
- malformed professional output,
- human-interaction interruption,
- filesystem/SQLite boundary failures.

The design goal is:

```text
architecture invariant
→ executable test
→ regression protection
```

---

# 1. Test Principles

1. Test architecture invariants directly.
2. Prefer deterministic fakes for core runtime tests.
3. External providers are integration edges, not prerequisites for core tests.
4. Every authoritative transaction needs rollback and crash-boundary coverage.
5. Duplicate/replay behavior must be tested wherever idempotency is required.
6. SQLite and filesystem behavior must be tested together for professional commit.
7. Restart tests must reconstruct state from durable storage only.
8. Tests must not depend on hidden in-memory provider session state.
9. Professional output validation must use the same schemas/resources as production.
10. Import/dependency boundaries should be enforced automatically.
11. Unit tests prove local logic; integration tests prove persistence/transactions; vertical tests prove orchestration.
12. End-to-end tests are not substitutes for transaction-level failure tests.

---

# 2. Test Layers

Recommended:

```text
unit
integration
transaction
vertical
recovery
provider-contract
conformance
end-to-end
```

Each layer has a distinct purpose.

---

# 3. Recommended Test Structure

```text
runtime/tests/
├── unit/
│   ├── domain/
│   ├── operations/
│   ├── routing/
│   ├── commit/
│   └── recovery/
│
├── integration/
│   ├── sqlite/
│   ├── filesystem/
│   ├── commands/
│   ├── events/
│   ├── executions/
│   ├── interactions/
│   └── providers/
│
├── transaction/
│   ├── job_creation/
│   ├── professional_commit/
│   ├── routing/
│   ├── interaction/
│   ├── failures/
│   └── recovery/
│
├── vertical/
│   ├── generate_analysis/
│   ├── resume_evaluation/
│   └── investigation/
│
├── recovery/
│   ├── crash_injection/
│   └── restart/
│
├── conformance/
│   ├── imports/
│   ├── architecture/
│   └── schemas/
│
└── e2e/
```

---

# 4. Core Test Fixtures

Build reusable deterministic fixtures early.

## Time

```text
FakeClock
```

Supports explicit time advancement.

## IDs

```text
DeterministicIdGenerator
```

Produces predictable IDs.

## Professional Provider

```text
FakeProfessionalInvoker
```

Can return:

```text
valid response
schema-invalid response
timeout
rate-limit error
provider error
malformed output
different deterministic fixture by operation
```

## Evidence Source

```text
FakeEvidenceSource
```

Can return:

```text
valid matches
successful zero matches
unavailable
timeout
invalid normalized result
```

## Discord

```text
FakeDiscordDelivery
FakeDiscordReconciler
```

Can simulate:

```text
successful send
duplicate inbound message
disconnect
timeout after external success
reconnect with unseen messages
```

## Filesystem

Temporary test root:

```text
/tmp/.../data/
```

with real filesystem operations unless a specific unit test only needs a fake.

## SQLite

Use a real temporary SQLite database for integration/transaction tests.

Avoid mocking SQLite behavior for correctness tests.

---

# 5. Unit Test — Domain IDs and Value Types

Required:

```text
ArtifactVersion rejects 0
ArtifactVersion rejects negative values
ID wrappers preserve type distinction
domain objects are immutable
UTC timestamp validation where enforced
hash value validators accept canonical format
```

---

# 6. Unit Test — RuntimeJob Invariants

Required:

```text
revision >= 1
healthy state rejects non-null failure_id
interaction none rejects active interaction metadata
operation idle rejects active Execution fields
ProfessionalState requires Target Job
collections are immutable
collection ordering canonicalization deterministic
```

---

# 7. Unit Test — Mutation Types

Required:

```text
SET pointer mutation valid only for scalar target
ADD valid only for collection target
REMOVE valid only for collection target
UPSERT_VERSION preserves one logical artifact ID
unknown mutation target rejected
```

---

# 8. Unit Test — Operation Specification Validation

For every specification:

```text
unique operation_type
valid handler_key
valid lifecycle phases
required task/contract resources exist
schema refs exist
required outputs declared
coupled groups reference required outputs
pointer authority targets valid
mutation types valid
identity dependencies authorized
freshness dependencies authorized
retrieval requirement valid
```

Negative tests:

```text
missing handler
missing schema
invalid pointer
duplicate operation_type
undeclared output in coupled group
retrieval required with no source
```

---

# 9. Unit Test — Operation Specification Hashing

Required:

```text
same canonical specification → same hash
field-order differences do not change hash
material semantic resource change → different hash
Git SHA-only change → same semantic specification hash
operation_registry_hash deterministic by canonical operation order
```

---

# 10. Unit Test — OperationKeyBuilder

Required:

```text
same identity dependencies → same operation_key
freshness-only unrelated state change → same operation_key
material identity dependency change → different operation_key
resource hash change → different operation_key when declared
retrieval fingerprint change → different operation_key when declared
runtime_instance_id change → no change
Git SHA-only change → no change unless semantic resource changed
```

---

# 11. Unit Test — FreshnessChecker

Required:

```text
all declared freshness dependencies current → fresh
one declared dependency changed → stale
unrelated Runtime Job revision change → still fresh
undeclared artifact change → still fresh
missing required dependency → invalid/stale according to contract
```

---

# 12. Unit Test — PointerMutationValidator

Required:

```text
authorized SET allowed
unauthorized SET rejected
authorized ADD allowed
wrong mutation type rejected
professional role name alone grants no authority
handler cannot widen specification authority
```

---

# 13. Unit Test — Routing Predicates

Each predicate gets focused tests.

## `has_unresolved_material_evidence_needs`

```text
no open needs → false
open need → true
partially_resolved → true
resolved/no_longer_material only → false
```

## `has_missing_active_erqs`

```text
all open needs mapped → false
one open need missing ERQ → true
free-text similarity without schema mapping → not sufficient
```

## ERQ predicates

```text
active ERQ set correct
awaiting response correct
unintegrated response correct
```

## Product/Evaluation predicates

```text
blocking product defect
blocking evidence uncertainty
ready_to_submit
```

Routing tests must use schema-defined fields, not prose inference.

---

# 14. Integration Test — SQLite Migrations

Required:

```text
empty DB migrates
all migrations recorded
restarting migration runner is safe
foreign_keys enabled
WAL enabled
required indexes exist
partial unique indexes active
schema mismatch blocks readiness
```

---

# 15. Integration Test — RuntimeJobRepository

Required:

```text
create revision 1
get reconstructs exact aggregate
scalar pointers round-trip
collections round-trip
routing history round-trip
deterministic collection ordering
CAS success increments once
CAS conflict raises ConcurrencyConflict
no database row types leak
```

---

# 16. Integration Test — ArtifactRepository

Required:

```text
artifact metadata round-trip
exact version lookup
multiple versions retained
storage_uri unique
prior committed versions remain committed
currentness not inferred from artifact status
```

---

# 17. Integration Test — ExecutionRepository

Required:

```text
create attempt 1
same operation_key attempt number uniqueness
one active Execution partial unique index
committed Execution can coexist with later attempt if policy permits
owner runtime instance round-trip
terminal timestamps persist
```

---

# 18. Integration Test — EventRepository

Required:

```text
persist Event
provider_event_id dedupe
claim atomic
lease fields set
expired lease reclaimable
processed Event not claimable
dead-letter state round-trip
```

---

# 19. Integration Test — CommandRepository

Required:

```text
persist Command
dedupe_key reuses existing Command
claim atomic
lease expiration
completed Command not claimable
retry_pending claimable
```

---

# 20. Integration Test — InteractionMessageRepository

Required:

```text
provider_message_id dedupe
canonical provider chronology ordering
unprocessed batch retrieval exact
processed message excluded
exact batch marking
```

---

# 21. Integration Test — UnitOfWork

Critical:

```text
two repository writes commit together
rollback restores all
exception auto-rolls back
all repositories share one transaction connection
nested autocommit impossible
```

Test with a deliberate failure after one repository write.

Expected:

```text
zero partial durable state
```

---

# 22. Transaction Test — TX-001 Create Job

Happy path:

```text
Target Job file finalized
artifact metadata
Runtime Job revision 1
Target Job pointer
pinned JER set
job_created Event
create_job completed
```

all durable.

Failure injection:

```text
before file finalize
after file finalize
after artifact metadata
after Runtime Job insert
after pointer insert
after Event insert
before COMMIT
after COMMIT before caller returns
```

Expected recovery:

```text
never duplicate Job
same command_id converges
orphan file tolerated
partial SQLite state not visible
```

---

# 23. Transaction Test — TX-005 Event → Command

Required:

```text
Event processing creates required Commands and marks Event processed atomically
```

Crash injection:

```text
after Command insert before Event processed
before COMMIT
after COMMIT
```

Expected:

```text
no processed Event without durable Command
duplicate processing reuses Command by dedupe key
```

---

# 24. Transaction Test — TX-006 schedule_operation

Required:

```text
same operation_key reuses compatible active/committed Execution
one active Execution database constraint enforced
RuntimeJob operation projection consistent
Command completion atomic with durable Execution creation/reuse
```

---

# 25. Transaction Test — TX-007 Begin Execution

Required:

```text
Execution running durable before provider call
runtime instance ownership persisted
provider invocation not inside write transaction
```

Kill process immediately after commit.

Recovery should identify interrupted physical attempt.

---

# 26. Transaction Test — TX-008 Single-Output Professional Commit

Required:

```text
artifact metadata
authorized Job pointer/collection
Job revision
Execution committed
artifact_committed
```

all atomic.

Failure injection after each write.

Expected:

```text
none commit partially
```

Test:

```text
unauthorized mutation
schema-invalid output
stale dependency
CAS conflict
missing file
artifact hash mismatch
duplicate retry after successful commit
```

---

# 27. Transaction Test — TX-009 Resume/WCM Coupled Commit

Required:

```text
both files finalized
both metadata rows
commit group
both pointers
one revision increment
Execution committed
exactly one artifact_committed
```

Negative cases:

```text
Resume valid/WCM invalid
Resume file exists/WCM missing
WCM metadata conflict
crash between pointer operations
```

Expected:

```text
never expose mixed old/new product
```

---

# 28. Transaction Test — TX-010 Evidence Integration

Required:

```text
multiple new JER versions commit together
all consumed Evidence Responses removed together
one revision increment
Execution committed
one artifact_committed
```

Failure:

```text
one JER invalid
one JER file finalization fails
Evidence Response already consumed
freshness conflict
```

Expected:

```text
no partial integration
```

---

# 29. Transaction Test — TX-011 Completed Evidence Response

Critical invariant test:

```text
Evidence Response current
↔ exact source human messages processed
```

Happy path:

```text
Evidence Response metadata
unintegrated response ADD
exact messages processed
Execution committed
Job revision
artifact_committed
```

Crash injection after:

```text
artifact insert
collection ADD
message processing
Execution finalization
Event insert
```

Expected before COMMIT:

```text
nothing authoritative
messages remain unprocessed
```

After COMMIT:

```text
all authoritative
```

---

# 30. Transaction Test — TX-012 Routing Transition

Required:

```text
RoutingDecision
lifecycle phase
entered_at
revision +1
lifecycle_changed
evaluate_routing completion
```

atomic.

Test CAS conflict:

```text
load old Job
concurrent authoritative mutation
attempt route
→ recompute predicate
```

Old decision must not replay blindly.

---

# 31. Transaction Test — TX-013 Routing No-Op

Required:

```text
Command completes
no routing history
no lifecycle Event
no revision change
```

when state genuinely requires no transition.

---

# 32. Transaction Test — TX-014 Inbound Human Message

Required:

```text
provider duplicate does not duplicate local message
human_input_received Event durable with message
canonical chronology independent of arrival order
```

Test out-of-order provider timestamps.

---

# 33. Transaction Test — TX-015 Conversational Continuation

Required:

```text
exact consumed human batch processed
next Interviewer outbound turn durable
```

atomically.

Crash before Discord delivery:

```text
outbound turn remains durable
delivery can retry/reconcile
```

Never:

```text
messages processed + next turn absent
```

---

# 34. Transaction Test — TX-016 Complete Interaction

Required:

```text
Interaction completed
RuntimeJob projection completed
revision +1
interaction_completed
Command completed
```

atomic.

Crash between Evidence Response commit and completion:

```text
safe state
→ recovery reschedules complete_interaction
```

---

# 35. Transaction Test — TX-018 Material Failure

Required:

```text
Failure row
Job health
failure pointer
revision
health Event if required
```

atomic when locally caused together.

Never:

```text
blocked Job without material Failure pointer
```

---

# 36. Recovery Test — Abandoned Execution

Setup:

```text
Execution running
owner runtime instance no longer active
```

On restart:

```text
old Execution terminal interrupted/failed
Failure persisted as required
retry creates new Execution attempt
same operation_key
old attempt retained
```

Provider call is not resumed.

---

# 37. Recovery Test — Event Lease

Setup:

```text
Event processing
lease expired
owner runtime dead
```

Expected:

```text
retry_pending
claimable
no duplicate required Command beyond dedupe
```

---

# 38. Recovery Test — Command Lease

Setup:

```text
Command processing
lease expired
```

Expected:

```text
retry_pending
```

For `schedule_operation`:

```text
existing Execution checked before creating another
```

---

# 39. Recovery Test — Professional Commit Windows

Cases:

```text
file finalized, no SQLite metadata
file finalized + metadata absent + stale now
current pointer advanced + Execution terminal mismatch
staging directory exists for failed Execution
```

Expected classification:

```text
retry
stale_output
orphaned_output
repair terminal metadata
```

Never advance pointer based solely on finding a file.

---

# 40. Recovery Test — Interaction Projection

Setup:

```text
Interaction completed
RuntimeJob projection active
```

Expected:

```text
deterministic projection repair
revision increment
```

Ambiguous mismatch:

```text
manual-review/failure path
```

---

# 41. Recovery Test — Discord Reconnect

Setup:

```text
runtime offline
Discord receives human messages
runtime restarts
```

Expected:

```text
reconciler finds unseen provider messages
dedupe persistence
canonical ordering
normal human_input_received processing
```

No reliance on webhook continuity.

---

# 42. Provider Contract Test — FakeProfessionalInvoker

Must prove fake implements the same port semantics as real providers.

Scenarios:

```text
valid structured output
raw text output
malformed output
timeout
provider exception
```

Application behavior should not special-case the fake beyond configuration.

---

# 43. Provider Contract Test — Real Professional Provider

Run against controlled fixtures or recorded provider responses where possible.

Verify:

```text
InvocationBundle translated correctly
resources supplied correctly
provider request ID captured
model/provider provenance stored
malformed output normalized
timeouts normalized
rate limits normalized
```

Do not make every CI run depend on live API access.

Use a separate opt-in integration test class for live provider verification.

---

# 44. Provider Contract Test — EvidenceSource

Required:

```text
successful matches
successful zero matches
provider auth failure
provider timeout
invalid provider payload
stable source identity
stable normalized result fingerprint
```

Required retrieval failure:

```text
professional invocation not started
```

---

# 45. Provider Contract Test — Discord

Required:

```text
message normalization
provider ID preservation
chronology timestamps
delivery acknowledgement
timeout after provider may have acted
reconciliation
duplicate provider message
```

Use local/unit adapter tests plus a smaller optional live integration suite.

---

# 46. Conformance Test — Import Boundaries

Automate rules:

```text
domain cannot import infrastructure
domain cannot import integrations
ports cannot import infrastructure
application cannot import concrete integrations
application cannot import sqlite library
cli cannot import sqlite repositories directly
bootstrap may compose all layers
```

Fail CI on dependency inversion violations.

---

# 47. Conformance Test — Event Ownership

Search/static/runtime tests should prove:

```text
CommitCoordinator is canonical artifact_committed producer
handlers do not emit artifact_committed after commit
execution_committed does not trigger routing
Router/lifecycle transactions own lifecycle_changed
```

---

# 48. Conformance Test — Operation Authority

For each Operation Specification:

```text
handler output contract == specification output contract
requested mutations subset of pointer authority
invalid lifecycle rejected
role binding does not grant extra mutation authority
```

---

# 49. Conformance Test — Deferred Scope

Assert MVP does not accidentally implement authoritative runtime state for:

```text
Information Request
Information Response
Target Role
Trello
```

Tests may allow future enum/storage extensibility but no current routing/pointers/required services.

---

# 50. Vertical Test — `generate_analysis`

Required complete path:

```text
create_job
→ job_created
→ evaluate_routing
→ analysis
→ schedule_operation(generate_analysis)
→ Execution
→ FakeEvidenceSource
→ FakeProfessionalInvoker
→ JEA staging
→ validation
→ file finalize
→ CommitCoordinator
→ artifact_committed
→ evaluate_routing
```

Assertions:

```text
all durable IDs/provenance correct
only one committed JEA current
duplicate Event safe
duplicate Command safe
restart reconstructs exact Job
```

---

# 51. Vertical Test — Resume / Evaluation Loop

Path:

```text
resume_production
→ generate_resume
→ coupled Resume/WCM commit
→ evaluation
→ evaluate_resume
→ Resume Evaluation
→ route
```

Branches:

```text
is_ready_to_submit = true
→ complete

blocking product defect
→ resume_production

blocking evidence uncertainty
→ evidence_request / analysis path according to routing model
```

---

# 52. Vertical Test — Investigation Loop

Path:

```text
Evidence Request
→ open Interaction
→ human message(s)
→ Interviewer ConversationTurn(s)
→ Evidence Response
→ commit + exact message consumption
→ complete_interaction
→ evidence_integration
→ re-analysis
```

Include restart at:

```text
before Interviewer invocation
after conversation turn persisted before Discord send
after Evidence Response commit before Interaction completion
```

---

# 53. End-to-End MVP Test

Run full deterministic fake-provider workflow:

```text
Target Job
→ analysis
→ evidence request
→ investigation
→ evidence response
→ integration
→ re-analysis
→ resume
→ evaluation
→ complete
```

Use real:

```text
SQLite
filesystem
application runtime
routing
transactions
recovery
```

Use fake:

```text
professional provider
EvidenceSource
Discord delivery
```

This proves runtime semantics independently of external service reliability.

---

# 54. End-to-End Live Smoke Test

Optional/manual or protected CI:

```text
real professional provider
real Google Drive EvidenceSource
real Discord test environment
```

Purpose:

```text
integration compatibility
```

not core correctness proof.

---

# 55. Crash Injection Framework

Introduce explicit test-only crash hooks.

Conceptual:

```python
crash_injector.hit("professional_commit.after_pointer_write")
```

Test runtime can raise:

```text
InjectedCrash
```

at named points.

Production builds may use no-op implementation.

Recommended hook categories:

```text
job_creation.*
event_processing.*
command_processing.*
execution.*
professional_commit.*
routing.*
interaction.*
failure.*
external_delivery.*
```

This is preferable to nondeterministic process-kill timing for most tests.

A smaller set of true subprocess kill/restart tests should validate real process durability.

---

# 56. True Process Restart Tests

Use a test harness that:

```text
starts runtime subprocess
drives state to known checkpoint
kills process
starts fresh runtime process against same /data
waits for recovery
asserts convergence
```

Critical checkpoints:

```text
Execution running
file finalized before commit
Evidence Response committed before Interaction completion
expired Command/Event lease
```

---

# 57. Property / Generative Tests

Useful candidates:

```text
RuntimeJob mutation sequences preserve revision monotonicity
collection ADD/REMOVE/UPSERT_VERSION semantics
Event duplicate ordering convergence
Command dedupe convergence
random crash point in professional commit never exposes partial current state
```

Optional but valuable after core implementation.

---

# 58. Test Data Strategy

Keep small deterministic professional fixtures under:

```text
runtime/tests/fixtures/
```

Suggested:

```text
target_jobs/
jer/
jea/
erq/
evidence_responses/
resume/
wcm/
evaluations/
provider_responses/
```

Fixtures should be minimal but schema-valid.

Avoid using personal production career data as a requirement for runtime correctness tests.

---

# 59. Schema Conformance Tests

For every structured professional artifact:

```text
known-valid fixture passes
known-invalid fixture fails
runtime validator and provider-supplied schema identity match
schema content hash captured correctly
```

Resume document validation gets its own format/template tests.

---

# 60. Migration Tests

For each migration:

```text
apply from prior schema
result matches expected schema
data preservation tested when relevant
```

Before first release, test:

```text
empty DB → latest
```

After releases begin:

```text
each supported prior release → latest
```

---

# 61. Performance / Load Tests

Not a primary MVP gate, but verify basic assumptions:

```text
hundreds/thousands of Events
hundreds of Commands
multiple historical artifact versions
large Interaction message history
multiple Runtime Jobs
```

Ensure indexes prevent obvious full-scan bottlenecks in queue claims/current state lookups.

Professional provider latency dominates normal runtime timing, so correctness remains higher priority than micro-optimization.

---

# 62. Security-Focused Tests

Required minimum:

```text
path traversal rejected in artifact store
artifact finalization cannot overwrite existing immutable version
CLI does not expose secrets in normal output
provider errors/logs do not dump sensitive professional content unnecessarily
Discord authorization filtering rejects unauthorized human messages
SQLite foreign keys remain on
```

Detailed security hardening can expand later.

---

# 63. Test Environment Matrix

## Fast CI

```text
unit
SQLite integration
transaction tests
fake-provider vertical tests
import conformance
schema tests
```

No network.

## Extended CI

```text
subprocess restart tests
larger recovery suite
migration compatibility
```

## Optional Live Integration

```text
real professional provider
real Google Drive
Discord test workspace
```

Protected secrets required.

---

# 64. Gate A Test Checklist — Runtime Core

Required:

```text
[ ] domain unit tests
[ ] Operation Specification validation/hash tests
[ ] SQLite migration/repository tests
[ ] UnitOfWork rollback/atomicity tests
[ ] Event→Command transaction tests
[ ] Command claim/dedupe tests
[ ] Execution operation_key tests
[ ] CommitCoordinator single-output transaction tests
[ ] routing transaction tests
[ ] import-boundary tests
```

---

# 65. Gate B Test Checklist — First Professional Round Trip

Required:

```text
[ ] generate_analysis vertical test
[ ] fake EvidenceSource
[ ] fake professional provider
[ ] real artifact filesystem
[ ] real SQLite
[ ] duplicate Event/Command replay
[ ] CAS conflict
[ ] stale output
[ ] file-finalization crash window
[ ] professional-commit crash window
[ ] process restart and reconstruction
```

---

# 66. Gate C Test Checklist — End-to-End MVP

Required:

```text
[ ] request_evidence operation tests
[ ] Resume/WCM coupled commit tests
[ ] evaluation routing tests
[ ] integrate_evidence atomicity tests
[ ] Interaction batching tests
[ ] Evidence Response exact message consumption tests
[ ] complete_interaction transaction tests
[ ] Discord reconnect/reconciliation tests
[ ] EvidenceSource failure tests
[ ] full fake-provider E2E
[ ] manual-review/failure escalation
[ ] startup recovery suite
```

---

# 67. Definition of Done for a Runtime Feature

A runtime feature is done only when:

```text
implementation exists
happy-path unit/integration tests pass
invalid input tested
duplicate/replay tested when relevant
transaction rollback tested
crash/recovery tested when relevant
architecture conformance tests remain green
no forbidden dependency introduced
```

---

# 68. Test Naming Convention

Recommended:

```text
test_<subject>__<condition>__<expected>()
```

Examples:

```text
test_commit__stale_jer_dependency__does_not_advance_jea_pointer()
test_event_processing__duplicate_event__reuses_command()
test_interviewer_commit__success__marks_exact_message_batch_processed()
```

Readable test names are part of architecture documentation.

---

# 69. Failure Diagnostics

When a test fails, output should include relevant durable IDs:

```text
job_id
revision
command_id
event_id
execution_id
operation_key
interaction_id
failure_id
```

Transaction/recovery tests should print or persist temporary DB state only on failure.

---

# 70. Coverage Expectations

Do not use line coverage as the sole quality metric.

Priority coverage:

```text
architecture invariants
transaction branches
failure paths
recovery paths
dedupe paths
CAS conflicts
stale output
```

High line coverage with untested crash windows is insufficient.

---

# 71. Test Traceability

Each major test module should reference the implementation-plan transaction/architecture concept it proves.

Example:

```text
tests/transaction/professional_commit/test_single_output.py
→ TX-008
→ Artifact & Execution Commit Model
```

This may be expressed in test docstrings/comments or test-plan mappings.

---

# 72. Known Test Dependency — `integrate_evidence`

Real professional invocation tests for `integrate_evidence` remain blocked until the approved Researcher integration task resource is confirmed.

Runtime transaction tests for evidence integration can proceed using deterministic fake outputs.

This distinction allows runtime engineering to continue without inventing professional instructions.

---

# 73. Decisions Made in This Phase

This plan establishes:

1. Real SQLite is required for persistence/transaction correctness tests.
2. Real filesystem operations are required for commit-boundary tests.
3. External providers are replaced by deterministic fakes for core CI.
4. Crash injection is a first-class test mechanism.
5. A smaller true subprocess restart suite validates real process durability.
6. Every architecture transaction has dedicated test coverage.
7. Gate A/B/C are test gates, not only implementation milestones.
8. Import/dependency boundaries are CI-enforced.
9. Live external integrations are smoke/compatibility tests, not the foundation of correctness.
10. `integrate_evidence` runtime tests can proceed before its real professional task binding is resolved.

---

# 74. Open Decisions

Still to choose during implementation:

- pytest vs alternative test framework;
- Hypothesis/property-test usage;
- import-boundary enforcement tool;
- crash-injection implementation;
- subprocess test harness;
- live provider test cadence;
- coverage threshold;
- CI platform/workflow structure;
- fixture document generation strategy.

These are tooling choices, not architecture questions.

---

# 75. Phase 8 Acceptance Criteria

The Test Plan is complete when:

- [ ] every authoritative transaction has explicit tests;
- [ ] domain invariants have unit tests;
- [ ] repository and SQLite constraints have integration tests;
- [ ] duplicate/replay behavior is tested;
- [ ] CAS conflicts are tested;
- [ ] stale professional output is tested;
- [ ] filesystem/SQLite crash windows are tested;
- [ ] restart recovery is tested from durable state only;
- [ ] completed Evidence Response exact message consumption is tested;
- [ ] Interaction projection consistency is tested;
- [ ] provider failures are normalized and tested;
- [ ] import/dependency conformance is testable;
- [ ] Gate A, Gate B, and Gate C have explicit test checklists;
- [ ] fake-provider E2E proves runtime correctness without live services;
- [ ] live-provider tests are optional compatibility smoke tests.

## Result

**READY FOR PHASE 9 — GITHUB IMPLEMENTATION BACKLOG**