# RRS V3 Package and Interface Plan

## Status

Implementation Planning — Phase 5

## Purpose

This document defines the recommended Python package structure, module ownership, dependency direction, public interfaces, and composition boundaries for the RRS V3 MVP runtime.

It translates the frozen architecture, Python domain model, SQLite schema, and transaction matrix into a buildable software layout.

It defines:

- package structure,
- allowed dependency direction,
- domain vs application vs infrastructure responsibilities,
- repository interfaces,
- UnitOfWork boundaries,
- runtime service interfaces,
- provider adapter boundaries,
- composition/bootstrap responsibilities,
- module ownership for each architecture concept.

It does **not** define production method bodies, concrete SQL statements, provider SDK calls, or final dependency-injection library choices.

The design goal is:

```text
architecture authority
→ package ownership
→ interface boundary
→ implementation
```

---

# 1. Structural Principle

RRS should use a layered package model with explicit dependency direction.

Recommended high-level structure:

```text
runtime/
├── src/
│   └── rrs/
│       ├── domain/
│       ├── ports/
│       ├── application/
│       ├── infrastructure/
│       ├── integrations/
│       ├── cli/
│       └── bootstrap/
│
├── migrations/
└── tests/
```

Dependency direction:

```text
domain
  ↑
ports
  ↑
application
  ↑
infrastructure / integrations / cli / bootstrap
```

More precisely:

```text
domain
← ports
← application
← infrastructure
← bootstrap
```

The domain layer knows nothing about infrastructure.

Infrastructure implements ports defined inward.

---

# 2. Recommended Repository Structure

```text
runtime/
│
├── architecture/
│   └── frozen architecture models
│
├── implementation/
│   ├── implementation-inventory.md
│   ├── python-domain-model.md
│   ├── sqlite-schema.md
│   ├── transaction-matrix.md
│   └── package-interface-plan.md
│
├── migrations/
│   ├── 0001_core.sql
│   ├── 0002_indexes.sql
│   └── 0003_provenance.sql
│
├── src/
│   └── rrs/
│       ├── domain/
│       ├── ports/
│       ├── application/
│       ├── infrastructure/
│       ├── integrations/
│       ├── cli/
│       └── bootstrap/
│
└── tests/
```

---

# 3. `domain/`

The domain package contains pure business/runtime concepts.

Recommended:

```text
rrs/domain/
├── ids.py
├── enums.py
├── artifacts.py
├── jobs.py
├── operations.py
├── executions.py
├── events.py
├── commands.py
├── interactions.py
├── failures.py
├── retrieval.py
├── invocation.py
├── routing.py
├── results.py
├── mutations.py
└── errors.py
```

The domain package may import only:

```text
Python standard library
typing
dataclasses
enum
datetime
```

and other `rrs.domain` modules.

It must not import:

```text
sqlite
aiosqlite
discord
google APIs
provider SDKs
click/typer
docker/environment config
```

---

# 4. `domain/ids.py`

Owns:

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

Also any canonical ID factories or parsers that remain pure.

ID generation itself should be behind a port if time/randomness is involved.

---

# 5. `domain/enums.py`

Owns all canonical enums:

```text
LifecyclePhase
OperationType
RuntimeOperationStatus
ExecutionStatus
InteractionProjectionStatus
InteractionStatus
InteractionType
HealthStatus
MutationType
RetrievalRequirement
ArtifactRuntimeStatus
EventStatus
EventCriticality
CommandStatus
FailureClass
ArtifactType
```

This module should be the single source for persisted enum strings.

Do not duplicate strings in repositories, handlers, or adapters.

---

# 6. `domain/artifacts.py`

Owns:

```text
ArtifactVersion
ArtifactRef
ArtifactMetadata
ArtifactCommitGroup
StagedArtifact
ResourceRef
SchemaRef
```

May also own:

```text
ProfessionalPointer
ProfessionalCollection
```

if not placed in `mutations.py`.

---

# 7. `domain/jobs.py`

Owns:

```text
RuntimeJob
RuntimeJobIdentity
LifecycleState
OperationState
InteractionProjection
HealthState
ProfessionalState
```

It should not know how a Runtime Job is persisted.

Validation/factory helpers may live here if pure.

---

# 8. `domain/operations.py`

Owns:

```text
OperationSpecification
ProfessionalBinding
RetrievalSpecification
OutputContract
PointerMutationAuthority
DependencyFingerprint
InputSnapshot
```

May also own:

```text
OperationSpecificationHash
OperationRegistryHash
```

as semantic wrappers if useful.

---

# 9. `domain/executions.py`

Owns:

```text
Execution
ExecutionStatus transition helpers
ExecutionResult
```

No provider invocation logic belongs here.

---

# 10. `domain/events.py`

Owns:

```text
Event
EventSource
Event payload tagged-union types
```

Recommended typed event payload classes:

```text
JobCreatedPayload
ArtifactCommittedPayload
LifecycleChangedPayload
HumanInputReceivedPayload
InteractionCompletedPayload
HealthChangedPayload
JobCancelledPayload
```

Avoid generic `dict` payloads in application code where practical.

---

# 11. `domain/commands.py`

Owns:

```text
Command
Command payload tagged-union types
```

Recommended payload classes:

```text
CreateJobPayload
ScheduleOperationPayload
EvaluateRoutingPayload
OpenInteractionPayload
CompleteInteractionPayload
RetryExecutionPayload
EnterManualReviewPayload
CancelJobPayload
```

---

# 12. `domain/interactions.py`

Owns:

```text
Interaction
InteractionMessage
InteractionProfessionalContext
ProviderInteractionContext
ConversationTurn
CompletedProfessionalArtifact
InterviewerContinuationResult
```

Provider-specific raw Discord types must not appear here.

---

# 13. `domain/failures.py`

Owns:

```text
Failure
FailureClass
failure severity/value helpers
```

Persistent `Failure` records are distinct from Python exceptions.

---

# 14. `domain/retrieval.py`

Owns:

```text
EvidenceQuery
RetrievedEvidenceItem
EvidenceSearchResult
EvidenceSourceRef
```

These remain provider-neutral.

---

# 15. `domain/invocation.py`

Owns:

```text
InvocationBundle
RawProfessionalResponse
InvocationProvenance
ProviderAttachment
```

Raw response is provider-neutral even if populated by an OpenAI or other adapter.

---

# 16. `domain/routing.py`

Owns:

```text
RoutingPredicateResult
RoutingDecision
RoutingOutcome
```

Pure predicate functions may live in the application layer if they need artifact loading.

---

# 17. `domain/mutations.py`

Owns typed Runtime Job mutation contracts:

```text
RuntimeJobMutation
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

No generic mutable dict mutation path should exist.

---

# 18. `domain/results.py`

Owns cross-service result values:

```text
CommitResult
RecoveryReport
ExecutionResult
RoutingOutcome
```

Keep result types immutable.

---

# 19. `domain/errors.py`

Owns normalized runtime exceptions:

```text
RRSRuntimeError
DomainValidationError
ConcurrencyConflict
StaleExecutionError
UnauthorizedMutationError
ArtifactStorageConflict
SchemaValidationError
OperationSpecificationError
EvidenceSourceUnavailable
RuntimeIntegrityError
PersistenceFailure
```

Infrastructure maps raw exceptions to these.

---

# 20. `ports/`

The ports package defines interfaces required by the application layer.

Recommended:

```text
rrs/ports/
├── repositories.py
├── unit_of_work.py
├── artifact_store.py
├── professional_invoker.py
├── evidence_source.py
├── output_extractor.py
├── clock.py
├── id_generator.py
├── provider_delivery.py
└── config.py
```

Ports may import `domain`.

They must not import concrete infrastructure implementations.

---

# 21. `ports/repositories.py`

Owns protocols:

```text
RuntimeJobRepository
ArtifactRepository
ExecutionRepository
EventRepository
CommandRepository
InteractionRepository
InteractionMessageRepository
FailureRepository
InvocationProvenanceRepository
RuntimeInstanceRepository
RoutingDecisionRepository
```

Repository protocols operate on domain objects.

They must not expose SQLite rows/cursors.

---

# 22. `ports/unit_of_work.py`

Owns the transaction boundary protocol.

Recommended:

```python
class UnitOfWork(Protocol):
    jobs: RuntimeJobRepository
    artifacts: ArtifactRepository
    executions: ExecutionRepository
    events: EventRepository
    commands: CommandRepository
    interactions: InteractionRepository
    messages: InteractionMessageRepository
    failures: FailureRepository
    provenance: InvocationProvenanceRepository
    routing: RoutingDecisionRepository

    async def __aenter__(self) -> "UnitOfWork": ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

All repositories inside one UnitOfWork are bound to the same SQLite transaction connection.

---

# 23. `ports/artifact_store.py`

Owns:

```text
ArtifactFileStore
```

Conceptual operations:

```text
stage
finalize
verify
read
exists
list_staging
cleanup_staging
```

File writes remain infrastructure.

---

# 24. `ports/professional_invoker.py`

Owns:

```python
class ProfessionalInvoker(Protocol):
    async def invoke(
        self,
        bundle: InvocationBundle,
    ) -> RawProfessionalResponse:
        ...
```

Implementations:

```text
FakeProfessionalInvoker
OpenAIProfessionalInvoker
future provider adapters
```

---

# 25. `ports/evidence_source.py`

Owns:

```python
class EvidenceSource(Protocol):
    async def search(
        self,
        query: EvidenceQuery,
    ) -> EvidenceSearchResult:
        ...
```

The initial provider may be Google Drive.

The application layer should not know that.

---

# 26. `ports/output_extractor.py`

Owns:

```text
OutputExtractor
```

Potential interface:

```python
class OutputExtractor(Protocol):
    def extract(
        self,
        response: RawProfessionalResponse,
        output_contract: OutputContract,
    ) -> tuple[StagedArtifactCandidate, ...]:
        ...
```

Operation-specific extractor selection may occur through a registry.

---

# 27. `ports/clock.py`

```python
class Clock(Protocol):
    def now(self) -> datetime: ...
```

Implementation:

```text
SystemClock
FakeClock
```

---

# 28. `ports/id_generator.py`

```python
class IdGenerator(Protocol):
    def new_job_id(self) -> JobId: ...
    def new_execution_id(self) -> ExecutionId: ...
    def new_command_id(self) -> CommandId: ...
    def new_event_id(self) -> EventId: ...
    def new_interaction_id(self) -> InteractionId: ...
    def new_message_id(self) -> MessageId: ...
    def new_failure_id(self) -> FailureId: ...
```

Implementation can use UUID/ULID/prefixed IDs.

Domain code should not care.

---

# 29. `application/`

The application layer implements deterministic runtime behavior.

Recommended:

```text
rrs/application/
├── commands/
├── events/
├── execution/
├── commit/
├── routing/
├── interactions/
├── recovery/
├── failures/
├── operations/
├── queries/
└── startup/
```

Application may import:

```text
domain
ports
```

It must not import provider SDKs or direct SQLite libraries.

---

# 30. `application/commands/`

Recommended:

```text
processor.py
create_job.py
schedule_operation.py
complete_interaction.py
retry_execution.py
enter_manual_review.py
cancel_job.py
```

Each command handler owns one deterministic transaction boundary from the Transaction Matrix.

Examples:

```text
CreateJobCommandHandler
ScheduleOperationCommandHandler
CompleteInteractionCommandHandler
CancelJobCommandHandler
```

`EvaluateRoutingCommandHandler` may delegate to `Router`.

---

# 31. `application/events/`

Recommended:

```text
processor.py
command_factory.py
dedupe.py
```

Responsibilities:

```text
claim Event
derive deterministic Command(s)
persist/reuse by dedupe key
mark Event processed
```

No professional reasoning.

---

# 32. `application/execution/`

Recommended:

```text
worker.py
operation_key.py
freshness.py
framework.py
handlers/
```

Owns:

```text
ExecutionWorker
OperationKeyBuilder
FreshnessChecker
BaseOperationHandler
HandlerRegistry
```

`handlers/` contains concrete operation-specific mechanics only.

---

# 33. `application/execution/handlers/`

Initial handlers:

```text
generate_analysis.py
request_evidence.py
investigate_evidence_request.py
integrate_evidence.py
generate_resume.py
evaluate_resume.py
```

Each handler receives the resolved Operation Specification.

Handlers must not define:

```text
allowed lifecycle phases
expected outputs
pointer authority
professional role binding
schemas
```

Those belong to the Operation Specification.

---

# 34. `application/commit/`

Recommended:

```text
coordinator.py
mutation_validator.py
artifact_versions.py
commit_groups.py
```

Owns:

```text
CommitCoordinator
PointerMutationValidator
ArtifactVersionAllocator
coupled-output commit logic
```

The Commit Coordinator is the only canonical producer of `artifact_committed`.

---

# 35. `application/routing/`

Recommended:

```text
router.py
predicates.py
registry.py
```

Owns:

```text
Router
RoutingPredicateRegistry
predicate implementations
RoutingDecisionBuilder
```

Predicates operate only on current committed state.

Initial predicate implementations:

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

---

# 36. `application/interactions/`

Recommended:

```text
processor.py
projection.py
continuation.py
batching.py
```

Owns:

```text
InteractionProcessor
InteractionProjectionSynchronizer
human-message batch resolution
Interviewer continuation orchestration
```

`DiscordAdapter` does not live here.

---

# 37. `application/recovery/`

Recommended:

```text
coordinator.py
executions.py
events.py
commands.py
interactions.py
commits.py
projections.py
```

Owns deterministic startup/recovery logic.

Recovery components use repositories and ports only.

They do not call raw SQLite or Discord directly except through ports/adapters.

---

# 38. `application/failures/`

Recommended:

```text
service.py
mapper.py
health.py
```

Owns:

```text
FailureMapper
FailureService
HealthRecalculator
ManualReviewEscalator
```

This keeps durable Failure semantics out of arbitrary handlers.

---

# 39. `application/operations/`

Recommended:

```text
registry.py
validator.py
hasher.py
resource_resolver.py
```

Owns:

```text
OperationSpecificationRegistry
RegistryValidator
OperationSpecificationHasher
OperationRegistryHasher
ProfessionalBindingResolver
```

Operation Specifications may be loaded from immutable Python/YAML configuration.

---

# 40. `application/queries/`

Recommended:

```text
jobs.py
artifacts.py
failures.py
```

Owns read-only query services for CLI/control surfaces.

Examples:

```text
JobQueryService
ArtifactQueryService
FailureQueryService
```

CLI should depend on these instead of repositories directly where practical.

---

# 41. `application/startup/`

Recommended:

```text
coordinator.py
health.py
```

Owns:

```text
StartupCoordinator
runtime readiness
recovery-before-ready sequencing
```

It coordinates infrastructure through ports/bootstrap-provided objects.

---

# 42. `infrastructure/`

Concrete local runtime implementations.

Recommended:

```text
rrs/infrastructure/
├── sqlite/
├── filesystem/
├── resources/
├── config/
├── logging/
└── runtime/
```

Infrastructure may import:

```text
domain
ports
application interfaces
```

Application must not import infrastructure.

---

# 43. `infrastructure/sqlite/`

Recommended:

```text
connection.py
unit_of_work.py
migrations.py
mappers.py
repositories/
```

Repository modules:

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

Owns all SQL.

No SQL appears in application handlers.

---

# 44. SQLite UnitOfWork

Concrete:

```text
SQLiteUnitOfWork
```

Responsibilities:

```text
open/bind one connection
BEGIN/BEGIN IMMEDIATE
expose repositories sharing that connection
commit
rollback
close
```

Transaction type may be selectable:

```text
read
write
immediate
```

if useful.

Provider/network calls must never occur while a write UoW is open.

---

# 45. `infrastructure/filesystem/`

Recommended:

```text
artifact_store.py
staging.py
hashing.py
```

Owns:

```text
LocalArtifactFileStore
staging directory layout
immutable finalization
content verification
safe cleanup helpers
```

Canonical paths:

```text
/data/artifacts/
/data/staging/<execution_id>/
```

---

# 46. `infrastructure/resources/`

Owns loading:

```text
agent contracts
task instructions
schemas
prompt/template resources
```

Recommended:

```text
resource_loader.py
schema_loader.py
```

Resources become `ResourceRef` / `SchemaRef` domain values.

---

# 47. `infrastructure/config/`

Owns environment/runtime configuration.

Recommended:

```text
settings.py
secrets.py
```

Configuration may use Pydantic Settings or another library, but domain types should remain library-independent.

---

# 48. `integrations/`

External provider adapters.

Recommended:

```text
rrs/integrations/
├── professional/
├── evidence/
└── discord/
```

---

# 49. `integrations/professional/`

Initial:

```text
fake.py
openai.py
```

`fake.py` implements:

```text
FakeProfessionalInvoker
```

This is required early for deterministic vertical-slice testing.

`openai.py` or another provider implementation translates:

```text
InvocationBundle
→ provider request
→ RawProfessionalResponse
```

Provider conversation/session memory must not be required for correctness.

---

# 50. `integrations/evidence/`

Recommended:

```text
google_drive.py
fake.py
```

Implements the `EvidenceSource` port.

Provider-specific Drive search/read details stay here.

Output becomes:

```text
EvidenceSearchResult
RetrievedEvidenceItem
```

---

# 51. `integrations/discord/`

Recommended:

```text
adapter.py
normalizer.py
delivery.py
reconciler.py
```

Owns:

```text
DiscordAdapter
DiscordMessageNormalizer
DiscordDeliveryService
DiscordReconciler
```

Discord types are mapped into domain Interaction/Event types at this boundary.

---

# 52. `cli/`

Recommended:

```text
rrs/cli/
├── app.py
└── job.py
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

CLI may import application query/control services.

CLI must not import:

```text
SQLite repositories directly
provider SDKs
domain mutation internals
```

---

# 53. `bootstrap/`

Composition root.

Recommended:

```text
rrs/bootstrap/
├── container.py
├── daemon.py
└── main.py
```

This is the **only** place where concrete infrastructure is wired to application ports.

Example responsibilities:

```text
load Settings
create SQLite connection factory
create SQLiteUnitOfWorkFactory
create LocalArtifactFileStore
create OperationSpecificationRegistry
create Fake/OpenAIProfessionalInvoker
create EvidenceSource
create DiscordAdapter
construct application services
construct workers
construct StartupCoordinator
run daemon
```

No professional/runtime business logic belongs in bootstrap.

---

# 54. Composition Root Rule

Dependency inversion should look like:

```text
application needs ProfessionalInvoker
        ↓
port defined
        ↓
bootstrap selects OpenAIProfessionalInvoker
```

not:

```text
application imports OpenAI SDK
```

Same for:

```text
EvidenceSource
ArtifactFileStore
UnitOfWork
Clock
IdGenerator
Discord delivery
```

---

# 55. Worker Structure

Recommended long-running workers:

```text
CommandProcessor
EventProcessor
ExecutionWorker
InteractionProcessor
```

Potentially:

```text
IntegrationDeliveryWorker
```

if outbound integration persistence requires a queue.

The daemon supervises them.

Each worker:

- claims only its own durable work type;
- uses short claim transactions;
- releases queue lease before long professional work;
- logs structured causal IDs;
- survives/retries independent failures.

---

# 56. Command Processing Interface

Recommended application contract:

```python
class CommandHandler(Protocol):
    async def handle(self, command: Command) -> None:
        ...
```

Registry:

```python
class CommandHandlerRegistry:
    def get(self, command_type: str) -> CommandHandler:
        ...
```

Current handlers include:

```text
create_job
schedule_operation
evaluate_routing
open_interaction
complete_interaction
retry_execution
enter_manual_review
cancel_job
```

---

# 57. Event Processing Interface

Recommended:

```python
class EventCommandPlanner(Protocol):
    async def plan(
        self,
        event: Event,
    ) -> tuple[Command, ...]:
        ...
```

Or deterministic pure planning:

```python
def derive_commands(
    event: Event,
    current_state: ...
) -> tuple[CommandSpec, ...]:
    ...
```

The Event Processor owns atomic Event→Command persistence.

---

# 58. Handler Registry Interface

```python
class HandlerRegistry(Protocol):
    def get(
        self,
        handler_key: str,
    ) -> OperationHandler:
        ...
```

The Operation Specification selects `handler_key`.

Professional role names never select handler classes directly.

---

# 59. Operation Specification Registry Interface

Recommended:

```python
class OperationSpecificationRegistry(Protocol):
    def get(
        self,
        operation_type: OperationType,
    ) -> OperationSpecification:
        ...

    def all(
        self,
    ) -> tuple[OperationSpecification, ...]:
        ...

    @property
    def registry_hash(self) -> str:
        ...
```

Registry validation completes before runtime readiness.

---

# 60. Output Extractor Registry

Recommended:

```python
class OutputExtractorRegistry(Protocol):
    def get(
        self,
        operation_type: OperationType,
    ) -> OutputExtractor:
        ...
```

This allows professional provider behavior to stay generic while operation outputs remain typed.

---

# 61. Routing Predicate Registry

Recommended:

```python
class RoutingPredicateRegistry(Protocol):
    def get(
        self,
        name: str,
    ) -> RoutingPredicate:
        ...
```

Predicate implementations remain deterministic.

---

# 62. Evidence Source Registry

If more than one EvidenceSource may be configured:

```python
class EvidenceSourceRegistry(Protocol):
    def get(
        self,
        key: str,
    ) -> EvidenceSource:
        ...
```

V0.1 may have only:

```text
google_drive
fake
```

but the application boundary remains provider-neutral.

---

# 63. Query Services

Recommended explicit read services:

```python
class JobQueryService:
    async def get_job(self, job_id: JobId) -> RuntimeJob: ...
    async def list_jobs(self, ...) -> tuple[RuntimeJobSummary, ...]: ...
```

```python
class ArtifactQueryService:
    async def current_artifacts(self, job_id: JobId) -> ...:
        ...
```

```python
class FailureQueryService:
    async def current_failure(self, job_id: JobId) -> Failure | None:
        ...
```

This avoids turning repository protocols into UI-specific APIs.

---

# 64. Runtime Control Service

Recommended application facade for mutating operator actions:

```python
class RuntimeControlService:
    async def create_job(self, request: CreateJobRequest) -> CommandId: ...
    async def retry_job(self, job_id: JobId) -> CommandId: ...
    async def cancel_job(self, job_id: JobId) -> CommandId: ...
```

The service persists Commands.

It does not directly perform authoritative runtime mutations.

---

# 65. Startup Coordinator Dependency Graph

Recommended:

```text
Settings
↓
SQLite connection / migrations
↓
Operation Specification Registry load + validate
↓
RuntimeBuildIdentity
↓
RuntimeInstance create
↓
Artifact path validation
↓
RecoveryCoordinator
↓
construct/start workers
↓
connect Discord
↓
Discord reconciliation
↓
runtime ready
```

The StartupCoordinator coordinates this sequence.

---

# 66. Import Rules

Recommended enforceable rules:

```text
rrs.domain
→ may import only stdlib + rrs.domain

rrs.ports
→ may import domain
→ may not import infrastructure/integrations

rrs.application
→ may import domain + ports
→ may not import concrete infrastructure/integrations

rrs.infrastructure
→ may import domain + ports
→ may import application types where needed
→ implements ports

rrs.integrations
→ may import domain + ports
→ provider SDKs allowed here

rrs.cli
→ may import application/query interfaces
→ must not directly import sqlite provider code

rrs.bootstrap
→ may import everything required for composition
```

These should eventually be tested with an import-boundary tool or architecture test.

---

# 67. Circular Dependency Prevention

Common danger:

```text
application.commit
↔ application.execution
```

Avoid by placing shared domain result/contracts in `domain/`.

Examples:

```text
CommitResult
ExecutionResult
RuntimeJobMutation
```

belong inward, not in one application service package.

Another danger:

```text
Discord integration
→ InteractionProcessor
→ Discord integration
```

Prevent through a delivery/reconciliation port.

---

# 68. Async Boundary

Recommended:

```text
repository ports async
provider/integration ports async
application services async
domain pure/sync
```

SQLite implementation likely uses an async adapter.

Pure functions such as:

```text
operation-key hashing
routing predicate evaluation
mutation authorization
domain validation
```

should remain synchronous unless I/O is genuinely required.

---

# 69. Transaction Boundary Rule in Code

Application service methods that own architecture-defined transactions should explicitly request a UnitOfWork.

Example:

```python
async with self.uow_factory() as uow:
    ...
    await uow.commit()
```

Do not hide a required multi-repository transaction behind nested repository methods that each commit independently.

Repository methods should not autocommit within a UnitOfWork.

---

# 70. No Network in Write Transaction Rule

The following must occur **outside** write UoW scopes:

```text
OpenAI/provider invocation
Google Drive retrieval
Discord API calls
large artifact file writes
```

Then open a short authoritative SQLite transaction.

This rule should be visible in code review and tests.

---

# 71. Operation Handler Dependency Set

Recommended BaseOperationHandler dependencies:

```text
RuntimeJobRepository or UoW factory
ExecutionRepository or UoW factory
OperationKeyBuilder
ProfessionalInvoker
EvidenceSourceRegistry
OutputExtractorRegistry
ArtifactFileStore
CommitCoordinator
Clock
IdGenerator
```

The actual handler should not depend on:

```text
Router
DiscordAdapter
CLI
Trello
raw SQLite
```

Routing happens after `artifact_committed`.

---

# 72. CommitCoordinator Dependency Set

Recommended:

```text
UnitOfWorkFactory
ArtifactFileStore
PointerMutationValidator
FreshnessChecker
ArtifactVersionAllocator
Clock
IdGenerator
```

It does not call:

```text
professional provider
Router
Discord API
```

---

# 73. Router Dependency Set

Recommended:

```text
UnitOfWorkFactory
RoutingPredicateRegistry
Artifact content/query loader
Clock
IdGenerator
```

Router may resolve exact current artifact contents needed by predicates.

It does not invoke professional agents.

---

# 74. InteractionProcessor Dependency Set

Recommended:

```text
UnitOfWorkFactory
ProfessionalInvoker
OutputExtractorRegistry
CommitCoordinator
DiscordDeliveryPort
Clock
IdGenerator
```

For conversational turn:

```text
professional invocation
→ transactionally consume messages + persist outbound turn
→ Discord delivery
```

For completed Evidence Response:

```text
professional invocation
→ CommitCoordinator consumes messages + commits Evidence Response
→ complete_interaction scheduled separately
```

---

# 75. RecoveryCoordinator Dependency Set

Recommended:

```text
UnitOfWorkFactory
ArtifactFileStore
ExecutionRecoveryService
EventRecoveryService
CommandRecoveryService
InteractionRecoveryService
CommitRecoveryService
ProjectionRecoveryService
DiscordReconciler
Clock
```

Recovery should use normal domain/service contracts where possible rather than custom SQL repair logic scattered throughout startup.

---

# 76. Fake Implementations

Before provider integrations, build:

```text
FakeProfessionalInvoker
FakeEvidenceSource
FakeDiscordDelivery
FakeClock
DeterministicIdGenerator
```

These enable deterministic vertical-slice and crash/recovery tests.

They should implement the same ports as production adapters.

---

# 77. Test Package Structure

Recommended:

```text
runtime/tests/
├── unit/
│   ├── domain/
│   ├── routing/
│   ├── operations/
│   └── commit/
│
├── integration/
│   ├── sqlite/
│   ├── commands/
│   ├── events/
│   ├── executions/
│   ├── interactions/
│   └── recovery/
│
├── vertical/
│   └── generate_analysis/
│
└── conformance/
    ├── import_boundaries/
    ├── transaction_invariants/
    └── architecture_rules/
```

Detailed test requirements belong in `test-plan.md`.

---

# 78. First Vertical Slice Package Touches

The first implementation slice:

```text
create_job
→ job_created
→ evaluate_routing
→ schedule_operation(generate_analysis)
→ Execution
→ FakeProfessionalInvoker
→ staged JEA
→ CommitCoordinator
→ artifact_committed
→ evaluate_routing
→ Router
```

requires only:

```text
domain
ports
application/commands
application/events
application/execution
application/commit
application/routing
application/operations
infrastructure/sqlite
infrastructure/filesystem
integrations/professional/fake
bootstrap
```

Discord and Google Drive are intentionally absent from Slice 1.

---

# 79. Package Ownership Traceability

| Architecture Concept | Package Owner |
|---|---|
| RuntimeJob | `domain.jobs` |
| OperationSpecification | `domain.operations` |
| Operation Specification Registry | `application.operations` |
| RuntimeJobRepository | `ports.repositories` + `infrastructure.sqlite.repositories.jobs` |
| Event | `domain.events` |
| EventProcessor | `application.events` |
| Command | `domain.commands` |
| CommandProcessor | `application.commands` |
| Execution | `domain.executions` |
| ExecutionWorker | `application.execution` |
| OperationHandler | `ports/application execution interface` |
| CommitCoordinator | `application.commit` |
| Router | `application.routing` |
| Failure | `domain.failures` |
| Failure/Health service | `application.failures` |
| Interaction | `domain.interactions` |
| InteractionProcessor | `application.interactions` |
| DiscordAdapter | `integrations.discord` |
| ProfessionalInvoker | `ports.professional_invoker` |
| OpenAI adapter | `integrations.professional` |
| EvidenceSource | `ports.evidence_source` |
| Google Drive adapter | `integrations.evidence` |
| SQLiteUnitOfWork | `infrastructure.sqlite` |
| ArtifactFileStore | `ports.artifact_store` + `infrastructure.filesystem` |
| CLI | `cli` |
| Startup/daemon | `bootstrap` + `application.startup` |

---

# 80. Decisions Made in This Phase

This plan establishes:

1. A layered `domain / ports / application / infrastructure / integrations / cli / bootstrap` structure.
2. Domain types remain infrastructure-independent.
3. Repository and external-provider contracts live in `ports`.
4. Deterministic runtime behavior lives in `application`.
5. SQL lives only in `infrastructure/sqlite`.
6. Filesystem artifact logic lives only in `infrastructure/filesystem`.
7. Provider SDKs live only in `integrations`.
8. Bootstrap is the composition root.
9. One UnitOfWork owns each authoritative SQLite transaction.
10. Long network/provider calls never occur inside write transactions.
11. Fake adapters implement production ports for early vertical-slice testing.
12. Import/dependency rules should be testable as architecture conformance tests.

---

# 81. Open Decisions for Later Phases

Still unresolved:

- exact dependency-injection framework or manual composition style;
- exact async SQLite library;
- exact CLI framework;
- exact configuration library;
- exact output-extractor strategy;
- whether Protocols live entirely in `ports` or some stay near domain modules;
- exact worker scheduling mechanism;
- exact structured logging library;
- exact provider SDK implementation.

These do not change package ownership.

---

# 82. Phase 5 Acceptance Criteria

The Package and Interface Plan is complete when:

- [ ] every implementation inventory component has a package owner;
- [ ] domain types cannot depend on infrastructure;
- [ ] application services depend on ports rather than provider SDKs;
- [ ] SQLite repositories are isolated under infrastructure;
- [ ] external providers are isolated under integrations;
- [ ] UnitOfWork is the shared transaction boundary;
- [ ] Command/Event/Execution/Interaction workers have distinct ownership;
- [ ] CommitCoordinator and Router remain separate;
- [ ] Operation Specifications remain declarative authority;
- [ ] handlers cannot import routing/provider-specific infrastructure directly;
- [ ] CLI mutations go through runtime Commands;
- [ ] bootstrap is the sole composition root;
- [ ] fake implementations can substitute for production adapters;
- [ ] the first vertical slice can be implemented without Discord or Google Drive;
- [ ] import-direction rules are explicit enough to test.

## Result

**READY FOR PHASE 6 — OPERATION SPECIFICATION DEFINITIONS**