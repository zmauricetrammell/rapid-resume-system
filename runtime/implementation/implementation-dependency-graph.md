# RRS V3 Implementation Dependency Graph

## Status

Implementation Planning — Phase 7

## Purpose

This document converts the frozen architecture and the preceding implementation plans into an ordered build graph.

It answers:

```text
What must exist before something else can be implemented safely?
What can be built in parallel?
What is the smallest executable vertical slice?
Where should real external integrations enter?
What gates must pass before advancing?
```

This is not a calendar estimate. It is a dependency model.

The goal is to prevent implementation from starting at the visible edges—Discord, provider SDKs, CLI polish—before the authoritative runtime core exists.

---

# 1. Governing Build Principle

Implementation proceeds from the inside outward:

```text
domain vocabulary
→ persistence primitives
→ transaction boundaries
→ runtime control plane
→ professional execution
→ vertical slice
→ recovery
→ remaining operations
→ human interaction
→ external integrations
→ operational hardening
```

The architecture is already the authority.

Implementation should discover coding details, not redesign runtime semantics.

---

# 2. Dependency Graph Legend

```text
[A] → [B]
```

means:

```text
B depends on A
```

Parallel branches are shown as:

```text
      → [B]
[A] ─┤
      → [C]
```

A gate is a required verification point before dependent work begins.

---

# 3. Top-Level Graph

```text
P0 Repository / Tooling Foundation
        ↓
P1 Domain Model
        ↓
P2 Operation Specification Core
        ↓
P3 SQLite Persistence + Migrations
        ↓
P4 UnitOfWork + Transaction Primitives
        ↓
P5 Event / Command Control Plane
        ↓
P6 Execution Framework
        ↓
P7 Artifact Store + Commit Coordinator
        ↓
P8 Routing
        ↓
GATE A — Runtime Core
        ↓
P9 First Vertical Slice: generate_analysis
        ↓
GATE B — First Professional Round Trip
        ↓
P10 Recovery Core
        ↓
P11 Remaining Non-Human Operations
        ↓
P12 Interaction Core
        ↓
P13 Discord Integration
        ↓
P14 Evidence Source Integration
        ↓
P15 Real Professional Provider
        ↓
GATE C — End-to-End MVP
        ↓
P16 CLI / Operator Controls
        ↓
P17 Hardening / Conformance / Packaging
```

Some phases contain parallel work, described below.

---

# 4. P0 — Repository and Tooling Foundation

## Purpose

Create the minimum Python project capable of running tests and enforcing package boundaries.

## Deliverables

```text
runtime/pyproject.toml
runtime/src/rrs/__init__.py
runtime/tests/
runtime/migrations/
runtime/src/rrs/{domain,ports,application,infrastructure,integrations,cli,bootstrap}/
```

Recommended development capabilities:

```text
Python version pinned
test runner
type checker
formatter/linter
coverage
architecture/import-boundary tests
```

Exact tools may be selected during implementation.

## Dependencies

```text
none
```

## Gate

```text
empty project installs
tests execute
package imports resolve
```

---

# 5. P1 — Domain Model

## Implement First

```text
domain/ids.py
domain/enums.py
domain/artifacts.py
domain/jobs.py
domain/operations.py
domain/executions.py
domain/events.py
domain/commands.py
domain/interactions.py
domain/failures.py
domain/retrieval.py
domain/invocation.py
domain/routing.py
domain/mutations.py
domain/results.py
domain/errors.py
```

## Supporting Ports

In parallel:

```text
ports/clock.py
ports/id_generator.py
```

with deterministic test implementations.

## Dependencies

```text
P0
```

## Required Tests

```text
value equality
immutability
enum persistence values
domain validation
ID parsing/generation contracts
RuntimeJob construction
mutation value construction
```

## Gate

No infrastructure import is permitted from `domain`.

---

# 6. P2 — Operation Specification Core

## Deliverables

```text
application/operations/registry.py
application/operations/validator.py
application/operations/hasher.py
application/operations/resource_resolver.py
```

Initial six specifications:

```text
generate_analysis
request_evidence
investigate_evidence_request
integrate_evidence
generate_resume
evaluate_resume
```

## Dependencies

```text
P1
```

## Parallelizable

Resource-loading infrastructure can begin here:

```text
infrastructure/resources/resource_loader.py
infrastructure/resources/schema_loader.py
```

## Gate

Startup validation must reject:

```text
unknown handler
missing schema
missing task/contract
invalid lifecycle
invalid pointer target
invalid mutation authority
bad coupled-output declaration
duplicate operation_type
```

The unresolved `integrate_evidence` task binding must be explicitly resolved before its real invocation path is enabled.

---

# 7. P3 — SQLite Persistence and Migrations

## Deliverables

```text
migrations/0001_core.sql
migrations/0002_indexes.sql
migrations/0003_provenance.sql

infrastructure/sqlite/connection.py
infrastructure/sqlite/migrations.py
infrastructure/sqlite/mappers.py
```

Repository implementations:

```text
jobs.py
artifacts.py
executions.py
events.py
commands.py
interactions.py
messages.py
failures.py
routing.py
provenance.py
runtime_instances.py
```

## Dependencies

```text
P1
```

P3 can proceed partly in parallel with P2.

## Required Tests

```text
fresh database migration
migration replay
foreign keys enabled
WAL enabled
schema compatibility
repository round trips
unique constraints
partial unique indexes
RuntimeJob reconstruction
```

## Gate

All persistent domain records round-trip without losing semantic information.

---

# 8. P4 — UnitOfWork and Transaction Primitives

## Deliverables

```text
ports/unit_of_work.py
infrastructure/sqlite/unit_of_work.py
```

Supporting services:

```text
CAS helper
transaction mode selection
SQLite exception mapping
artifact version allocation primitive
```

## Dependencies

```text
P3
```

## Critical Tests

```text
multi-repository commit
rollback
CAS conflict
one active Execution constraint
Command dedupe
Event provider dedupe
InteractionMessage provider dedupe
one active Interaction per Job
```

## Gate

One UnitOfWork must prove that multiple repositories share one actual SQLite transaction.

---

# 9. P5 — Event / Command Control Plane

## Deliverables

```text
application/events/processor.py
application/events/command_factory.py

application/commands/processor.py
application/commands/create_job.py
application/commands/schedule_operation.py
application/commands/evaluate_routing.py
application/commands/cancel_job.py
```

Initial scope may omit interaction-specific handlers until P12.

## Dependencies

```text
P1
P4
```

## Required Transactions

Implement first:

```text
TX-001 Create Job
TX-002 Claim Command
TX-003 Complete SQLite-local Command
TX-004 Claim Event
TX-005 Event → Command
```

## Required Tests

```text
Event cannot be processed without required Command durability
duplicate Event processing reuses Command
Command lease recovery shape
create_job idempotency
Command completion means authoritative effect exists
```

## Gate

A persisted `create_job` Command can create a Job and drive a durable Event→Command chain without professional execution.

---

# 10. P6 — Execution Framework

## Deliverables

```text
application/execution/framework.py
application/execution/worker.py
application/execution/operation_key.py
application/execution/freshness.py
application/execution/handlers/base.py
```

Ports:

```text
ports/professional_invoker.py
ports/output_extractor.py
```

Fake:

```text
integrations/professional/fake.py
```

## Dependencies

```text
P2
P4
P5
```

## Required Transactions

```text
TX-006 schedule_operation creates/reuses Execution
TX-007 begin Execution
```

## Required Tests

```text
same logical inputs → same operation_key
material identity change → new operation_key
only one active Execution per operation_key
provider call occurs after running state is durable
Command lease is not held during provider call
freshness is independent of unrelated Job revision changes
```

## Gate

A scheduled professional operation reaches a fake provider deterministically.

---

# 11. P7 — Artifact Store and Commit Coordinator

## Deliverables

```text
ports/artifact_store.py

infrastructure/filesystem/artifact_store.py
infrastructure/filesystem/staging.py
infrastructure/filesystem/hashing.py

application/commit/coordinator.py
application/commit/mutation_validator.py
application/commit/artifact_versions.py
application/commit/commit_groups.py
```

## Dependencies

```text
P1
P4
P6
```

## Required Transactions

```text
TX-008 single-output professional commit
TX-009 coupled Resume/WCM commit
TX-010 evidence integration commit
TX-011 Evidence Response commit
```

Not every transaction needs to be exercised immediately, but the coordinator design must support them.

## Required Tests

```text
file finalizes before SQLite authority
orphan file is safe
missing finalized file blocks commit
schema failure blocks commit
unauthorized mutation blocks commit
freshness conflict blocks/reevaluates commit
artifact_committed is atomic with current-state mutation
```

## Gate

A fake professional artifact can become current only through CommitCoordinator.

---

# 12. P8 — Routing

## Deliverables

```text
application/routing/router.py
application/routing/predicates.py
application/routing/registry.py
```

Initial predicates:

```text
has_unresolved_material_evidence_needs
has_missing_active_erqs
has_active_erqs
has_erqs_awaiting_evidence_response
has_unintegrated_evidence_responses
has_blocking_product_defects
has_blocking_evidence_uncertainties
is_ready_to_submit
```

## Dependencies

```text
P1
P4
P5
P7
```

## Required Transactions

```text
TX-012 Routing Transition
TX-013 Routing No-Op Completion
```

## Required Tests

```text
routing uses committed current state only
history + lifecycle + Event + Command completion atomic
CAS conflict recomputes predicate
duplicate routing checks do not create meaningless history
```

---

# 13. GATE A — Runtime Core

Before any real external integration, verify:

```text
[ ] Domain model stable enough for vertical slice
[ ] Operation registry validates
[ ] SQLite migrations pass from empty DB
[ ] UnitOfWork atomicity proven
[ ] Event→Command chain durable
[ ] Execution scheduling/idempotency proven
[ ] fake provider invocation works
[ ] artifact staging/finalization works
[ ] CommitCoordinator is sole artifact_committed producer
[ ] Router transition is atomic
[ ] no network calls occur inside write transactions
```

Failure at Gate A means:

```text
fix runtime core before adding Discord/Google Drive/real provider complexity
```

---

# 14. P9 — First Vertical Slice: `generate_analysis`

## Goal

Prove one complete professional loop.

Flow:

```text
create_job
→ job_created
→ evaluate_routing
→ lifecycle analysis
→ schedule_operation(generate_analysis)
→ Execution
→ FakeProfessionalInvoker
→ deterministic JEA
→ schema validation
→ file finalization
→ CommitCoordinator
→ JEA current pointer
→ artifact_committed
→ evaluate_routing
→ next lifecycle decision
```

## Scope

Use:

```text
fake professional invoker
fixture Target Job
fixture JER set
fixture retrieval result or FakeEvidenceSource
real SQLite
real filesystem staging/finalization
real CommitCoordinator
real Router
```

## Dependencies

```text
Gate A
```

## Required Assertions

```text
Job revision changes correctly
Execution history persists
JEA pointer references exact artifact version
artifact file hash matches metadata
artifact_committed exists exactly once
routing sees committed JEA
replaying duplicate Events/Commands converges
restart after completion reconstructs same state
```

---

# 15. GATE B — First Professional Round Trip

Required:

```text
[ ] first vertical slice passes
[ ] duplicate delivery tests pass
[ ] CAS conflict tests pass
[ ] crash before/after professional commit has deterministic outcome
[ ] restart reconstructs current Job
[ ] operation provenance is persisted
[ ] no hidden in-memory state is required for correctness
```

Once Gate B passes, the architecture has been demonstrated in executable form.

---

# 16. P10 — Recovery Core

## Deliverables

```text
application/recovery/coordinator.py
application/recovery/executions.py
application/recovery/events.py
application/recovery/commands.py
application/recovery/commits.py
application/recovery/projections.py
```

Interaction recovery may be added at P12.

## Dependencies

```text
Gate B
```

## Required Transactions

```text
TX-021 interrupted Execution recovery
TX-022 Event lease recovery
TX-023 Command lease recovery
TX-025 commit recovery completion
TX-028 runtime startup identity
```

## Required Tests

Crash injection around:

```text
Event claim
Command claim
Execution running
provider return
file finalization
professional commit
routing commit
```

## Gate

Killing and restarting the runtime at supported crash points converges without duplicating authoritative professional state.

---

# 17. P11 — Remaining Non-Human Professional Operations

Implement:

```text
request_evidence
integrate_evidence
generate_resume
evaluate_resume
```

`investigate_evidence_request` waits for Interaction Core.

## Dependencies

```text
P10
resolved Operation Specification resources
```

## Suggested Order

```text
1. request_evidence
2. generate_resume
3. evaluate_resume
4. integrate_evidence
```

Reason:

- `request_evidence` is single/limited output and extends Researcher flow.
- `generate_resume` proves coupled Resume/WCM commit.
- `evaluate_resume` completes the product loop.
- `integrate_evidence` is the most complex non-human multi-artifact mutation and depends on its approved task binding.

## Gates Per Operation

Each must pass:

```text
operation identity
freshness
schema validation
mutation authority
commit atomicity
routing after commit
restart/replay
```

---

# 18. P12 — Interaction Core

## Deliverables

```text
application/interactions/processor.py
application/interactions/projection.py
application/interactions/continuation.py
application/interactions/batching.py

application/commands/open_interaction.py
application/commands/complete_interaction.py
```

Add interaction recovery:

```text
application/recovery/interactions.py
```

## Dependencies

```text
P10
Operation Specification for investigate_evidence_request
```

## Required Transactions

```text
TX-014 inbound human message persistence
TX-015 conversational continuation
TX-016 complete Interaction
TX-017 pause/resume projection
TX-024 Interaction projection repair
```

## Fake Integration

Use:

```text
FakeDiscordDelivery
synthetic inbound messages
FakeProfessionalInvoker
```

before real Discord.

## Critical Tests

```text
provider message dedupe
canonical message ordering
exact batch consumption
ConversationTurn consumes batch + persists outbound turn atomically
Evidence Response commit consumes exact batch atomically
Evidence Response commit and Interaction completion remain separate
crash between them recovers safely
```

---

# 19. P13 — Discord Integration

## Deliverables

```text
integrations/discord/adapter.py
integrations/discord/normalizer.py
integrations/discord/delivery.py
integrations/discord/reconciler.py
```

## Dependencies

```text
P12
```

## Required External Transactions

```text
TX-026 external delivery intent
TX-027 external delivery acknowledgement
```

## Rules

Discord remains:

```text
human interaction surface
not orchestration authority
not professional state store
```

## Gate

Disconnect/reconnect and duplicate-delivery scenarios converge from SQLite authority.

---

# 20. P14 — Evidence Source Integration

## Initial Provider

```text
Google Drive
```

Deliverables:

```text
integrations/evidence/google_drive.py
```

## Dependencies

```text
P6
P9 fake EvidenceSource behavior already proven
```

Can be built in parallel with P12/P13 once the EvidenceSource port is stable.

## Required Tests

```text
successful retrieval
successful zero-match retrieval
authentication failure
provider timeout
partial read failure
stable result fingerprint
required retrieval failure blocks invocation
```

The Google Drive adapter returns provider-neutral retrieval domain objects.

---

# 21. P15 — Real Professional Provider

## Deliverables

```text
integrations/professional/<provider>.py
```

## Dependencies

```text
P6
P7
Gate B
Operation Specification resources
```

Can begin earlier experimentally, but should not become the runtime dependency until fake-provider vertical slices pass.

## Required Tests

```text
InvocationBundle translation
resource attachment
schema/output contract handling
provider request ID provenance
timeout normalization
rate-limit normalization
malformed response
usage/latency provenance
no provider session memory required for correctness
```

## Rule

The provider adapter does not own:

```text
routing
pointer mutation
freshness
artifact commit
Job lifecycle
```

---

# 22. GATE C — End-to-End MVP

Required scenario:

```text
Target Job
→ create Job
→ Researcher analysis
→ evidence request if required
→ human Interviewer interaction
→ Evidence Response
→ evidence integration
→ re-analysis
→ Writer Resume + WCM
→ Evaluator
→ deterministic routing
→ ready_to_submit or bounded loop
```

Required failure scenarios:

```text
provider timeout
required retrieval failure
invalid professional output
stale professional output
duplicate Event
duplicate Command
duplicate Discord message
process crash during Execution
process crash around artifact commit
process crash between Evidence Response and Interaction completion
restart with expired leases
manual-review escalation
```

Only after these pass is the orchestration MVP functionally demonstrated.

---

# 23. P16 — CLI and Operator Controls

## Deliverables

```text
cli/app.py
cli/job.py
application/queries/jobs.py
application/queries/artifacts.py
application/queries/failures.py
RuntimeControlService
```

Commands:

```text
rrs job create
rrs job show
rrs job list
rrs job artifacts
rrs job retry
rrs job cancel
rrs job review
```

## Dependencies

Read-only query work can begin earlier.

Mutation commands depend on the durable Command control plane.

## Rule

CLI mutation:

```text
operator request
→ persist Command
→ normal runtime processing
```

not direct repository mutation.

---

# 24. P17 — Hardening and Packaging

## Areas

```text
structured logging
metrics
health/readiness
Docker image
volume layout
backup procedure
migration safety
configuration validation
secret handling
resource/build provenance
graceful shutdown
staging garbage collection
```

## Dependencies

```text
Gate C
```

Some observability can be added earlier, but hardening is not allowed to redefine architecture semantics.

---

# 25. Parallel Work Map

After P1:

```text
                 → P2 Operation Registry
P1 Domain ───────┼→ P3 SQLite
                 → filesystem artifact primitives
```

After P4/P5:

```text
                 → P6 Execution Framework
Control Plane ───┼→ P8 Routing foundations
                 → CLI read/query foundations
```

After Gate B:

```text
                 → P10 Recovery
                 → P14 Google Drive adapter
Gate B ──────────┼→ P15 real provider adapter
                 → P11 operation handlers
```

After P12:

```text
Interaction Core → P13 Discord
```

---

# 26. What Must Not Be Built First

Avoid beginning implementation with:

```text
Discord bot
Google Drive integration
OpenAI/provider prompt calls
full CLI
Trello projection
Docker deployment polish
```

before the authoritative core is executable.

Those are replaceable edges.

The hard part is:

```text
state
transactions
idempotency
commit authority
routing
recovery
```

Build those first.

---

# 27. Critical Path

The minimum critical path to prove the architecture is:

```text
P0
→ P1
→ P3
→ P4
→ P5
→ P2
→ P6
→ P7
→ P8
→ P9
→ Gate B
```

P2 and P3 may overlap, but both must be ready before the first professional slice.

---

# 28. Recommended Pull Request Sequence

A practical PR sequence:

```text
PR-01  Python runtime scaffold
PR-02  Domain model + enums + IDs
PR-03  Operation Specification registry
PR-04  SQLite migrations + repositories
PR-05  UnitOfWork + CAS + persistence tests
PR-06  Event/Command control plane
PR-07  Execution framework + fake invoker
PR-08  Artifact store + CommitCoordinator
PR-09  Router + predicates
PR-10  generate_analysis vertical slice
PR-11  recovery core + crash injection
PR-12  request_evidence
PR-13  generate_resume coupled commit
PR-14  evaluate_resume
PR-15  integrate_evidence
PR-16  Interaction core
PR-17  Discord adapter
PR-18  Google Drive EvidenceSource
PR-19  real professional provider
PR-20  end-to-end MVP conformance
PR-21  CLI/operator controls
PR-22  deployment/operational hardening
```

This is a dependency order, not a requirement that every PR be exactly this size.

---

# 29. Definition of Done Per Implementation Node

A node is not complete merely because code exists.

Each node requires:

```text
implementation
unit tests
relevant integration tests
type/static checks
architecture/import conformance
documentation/config update
failure-path coverage
```

For transaction-owning nodes:

```text
rollback test
duplicate/replay test
crash-boundary test where applicable
```

---

# 30. Architecture Change Trigger

During implementation, a discovery becomes an architecture issue when satisfying it would require changing:

```text
authority boundary
persistent state meaning
lifecycle semantics
operation semantics
transaction atomicity
routing authority
professional role authority
recovery guarantees
```

Such a change should not be hidden inside implementation.

Instead:

```text
stop
document discrepancy
update/review architecture
then implement
```

Normal coding decisions such as library selection do not require architecture revision.

---

# 31. Implementation Planning Exit Criteria

Implementation planning is ready to transition into coding when the remaining planning artifacts define:

```text
test strategy
GitHub backlog/issues
```

and the known professional-resource gap for `integrate_evidence` has an explicit resolution task.

The current implementation model already defines:

```text
domain contracts
physical persistence
transaction boundaries
package/interfaces
operation specifications
dependency order
```

---

# 32. Phase 7 Acceptance Criteria

The Implementation Dependency Graph is complete when:

- [ ] build order follows dependency direction;
- [ ] authoritative core precedes external integrations;
- [ ] first vertical slice is explicitly bounded;
- [ ] Gate A verifies runtime-core invariants;
- [ ] Gate B proves a professional round trip;
- [ ] recovery follows the first vertical slice rather than being deferred to the end;
- [ ] remaining operations have a safe implementation order;
- [ ] Interaction core is testable without Discord;
- [ ] Google Drive and professional-provider adapters are replaceable edges;
- [ ] Gate C defines an end-to-end MVP;
- [ ] practical PR sequencing is identified;
- [ ] architecture-change triggers are explicit;
- [ ] `integrate_evidence` resource resolution is carried forward as a dependency.

## Result

**READY FOR PHASE 8 — TEST PLAN**