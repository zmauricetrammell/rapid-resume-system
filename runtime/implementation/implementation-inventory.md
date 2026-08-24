# RRS V3 Implementation Inventory and Architecture Traceability Matrix

## Status
Implementation Planning — Phase 1

## Purpose
This document translates the frozen V3 MVP runtime architecture into an implementation inventory. It answers what must exist in code, what owns it, what it depends on, which architecture model defines it, and what later planning artifact must make it concrete.

This document does **not** choose final Python syntax, SQLite columns, package names, or implementation libraries. Those belong to later implementation-planning phases.

---

# 1. Implementation Boundaries

V3 implementation separates six major concerns:

```text
Domain Types
Runtime Control Plane
Professional Execution
Persistence
Integrations / Human Interaction
Deployment / Operations
```

The architecture-to-code rule is:

```text
Professional architecture
→ Operation Specifications
→ deterministic runtime components
→ repositories / persistence
→ adapters
```

Professional agents remain outside deterministic runtime reasoning.

---

# 2. Domain Types Inventory

| Component | Implementation Target | Primary Responsibility | Architecture Source |
|---|---|---|---|
| `JobId` | immutable ID type | Runtime Job identity | Job Model |
| `ExecutionId` | immutable ID type | Physical professional-attempt identity | Artifact & Execution Commit Model |
| `OperationKey` | immutable semantic identity type | Logical professional-operation idempotency | Artifact & Execution Commit Model |
| `CommandId` | immutable ID type | Durable requested runtime action identity | Event Model |
| `EventId` | immutable ID type | Durable fact identity | Event Model |
| `InteractionId` | immutable ID type | Human-interaction identity | Discord Interaction Model |
| `MessageId` | immutable ID type | Persisted Interaction Message identity | Discord Interaction Model |
| `FailureId` | immutable ID type | Persistent runtime failure identity | Persistence / Control Surface Models |
| `ArtifactId` | immutable ID type | Professional artifact logical identity | Commit / Persistence Models |
| `ArtifactVersion` | positive integer value type | Exact immutable artifact version | Job / Persistence Models |
| `RuntimeInstanceId` | immutable ID type | One daemon-process lifetime | Deployment / Persistence Models |
| `ArtifactRef` | frozen value object | Exact immutable professional artifact pointer | Job Model |
| `ResourceRef` | frozen value object | Versioned contract/task/template/resource identity | Professional Invocation Model |
| `SchemaRef` | frozen value object | Exact schema supplied and validated | Professional Invocation Model |
| `InputSnapshot` | frozen value object | Exact professional dependencies used by Execution | Commit Model |
| `InvocationBundle` | frozen aggregate | Exact professional invocation context | Handler / Invocation Models |
| `RuntimeBuildIdentity` | frozen value object | Git/image/registry provenance | Deployment / Registry Models |

---

# 3. Canonical Enum Inventory

These should become one authoritative Python vocabulary rather than scattered strings.

| Enum | Values / Role | Architecture Source |
|---|---|---|
| `LifecyclePhase` | new, analysis, evidence_request, investigation, evidence_integration, resume_production, evaluation, complete, manual_review, cancelled | Job Model |
| `OperationType` | generate_analysis, request_evidence, investigate_evidence_request, integrate_evidence, generate_resume, evaluate_resume | Job / Registry Models |
| `RuntimeOperationStatus` | idle, queued, running, validating, committing | Job Model |
| `ExecutionStatus` | created, queued, running, output_received, validating, validated, stale, committing, committed, failed, cancelled | Commit Model |
| `CommandStatus` | durable command processing lifecycle | Event / Persistence Models |
| `EventStatus` | received, processing, processed, ignored, retry_pending, dead_letter | Event / Persistence Models |
| `InteractionStatus` | authoritative Interaction lifecycle | Discord / Persistence Models |
| `InteractionProjectionStatus` | none, pending, active, paused, completed | Job Model |
| `InteractionType` | evidence_investigation, manual_review | Job / Discord Models |
| `HealthStatus` | healthy, degraded, recoverable_failure, blocked | Job Model |
| `FailureClass` | normalized runtime failure vocabulary including `EVIDENCE_SOURCE_UNAVAILABLE` | Handler / Persistence Models |
| `ArtifactType` | V0.1 professional artifact vocabulary | Job / Invocation / Persistence Models |
| `ArtifactRuntimeStatus` | committed, stale_output, orphaned_output, diagnostic | Commit / Persistence Models |
| `MutationType` | SET, ADD, REMOVE, REPLACE, UPSERT_VERSION | Job / Registry Models |
| `RetrievalRequirement` | none, optional, required | Registry / Invocation Models |
| `EventCriticality` | workflow_critical, integration_only | Event Model |
| `InterviewerContinuationKind` | conversation_turn, completed_professional_artifact | Discord / Invocation Models |

---

# 4. Runtime Job Domain Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `RuntimeJob` | frozen aggregate | Canonical current runtime state | Job Model |
| `RuntimeJobIdentity` | value object | ID, revision, timestamps | Job Model |
| `LifecycleState` | value object | Current lifecycle phase | Job Model |
| `OperationState` | value object | Current automated professional operation projection | Job Model |
| `InteractionProjection` | value object | Coarse projection of authoritative Interaction | Job / Persistence Models |
| `HealthState` | value object | Current runtime health and material failure pointer | Job Model |
| `ProfessionalState` | value object | Current artifact pointers and collections | Job Model |
| `RoutingDecision` | immutable historical record | Why lifecycle transition occurred | Job / Routing Models |
| `RuntimeJobMutation` | typed mutation contract | Authorized CAS mutation request | Job / Persistence Models |
| `RuntimeJobRepository` | repository protocol | Load canonical aggregate and enforce revision/CAS mutation | Job / Persistence Models |

Key invariant:

```text
RuntimeJobRepository
→ returns canonical aggregate
→ callers never depend on SQLite table layout
```

---

# 5. Operation Specification Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `OperationSpecification` | frozen declarative model | Complete runtime contract for one operation | Operation Specification Registry Model |
| `OperationSpecificationRegistry` | validated registry service | `operation_type → effective specification` | Registry Model |
| `HandlerRegistry` | deterministic registry | `handler_key → Python handler implementation` | Handler / Registry Models |
| `ProfessionalBinding` | value object | Role + contract + task/resource binding | Registry / Invocation Models |
| `OutputContract` | value object | Required outputs, coupled groups, schemas | Registry Model |
| `PointerAuthority` | value object / set | Exact authorized Runtime Job mutations | Registry / Job Models |
| `DependencyDeclaration` | value object | Identity vs freshness dependencies | Registry / Commit Models |
| `RetryPolicyRef` | config reference | Operation retry policy binding | Registry / Deployment Models |
| `RegistryValidator` | startup service | Structural/reference/semantic validation | Registry / Deployment Models |
| `OperationSpecificationHasher` | deterministic service | Semantic specification identity | Registry Model |
| `OperationRegistryHasher` | deterministic service | Registry build identity | Registry Model |

The Registry is configuration authority. Handler classes must not duplicate these declarations.

---

# 6. Command / Event Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `Command` | durable domain record | Requested runtime action | Event Model |
| `CommandRepository` | repository protocol | Persist, claim, lease, complete, retry commands | Event / Persistence Models |
| `CommandProcessor` | runtime worker | Claim and execute deterministic command work | Event / Deployment Models |
| `CommandDedupeKey` | deterministic value | Prevent duplicate event-produced Commands | Event Model |
| `Event` | durable immutable body + processing state | Fact that already occurred | Event Model |
| `EventRepository` | repository protocol | Persist, claim, retry, mark processed/dead-letter | Event / Persistence Models |
| `EventProcessor` | runtime worker | Convert Events into Commands atomically | Event Model |
| `EventNormalizer` | integration boundary | Provider payload → canonical Event | Event Model |
| `QueueLease` | persistence concept/value object | Short-lived Event/Command work ownership | Event / Deployment Models |

Canonical separation:

```text
Event = fact
Command = requested deterministic action
Execution = physical professional attempt
```

---

# 7. Execution and Professional Operation Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `Execution` | persistent domain record | One physical professional-operation attempt | Commit Model |
| `ExecutionRepository` | repository protocol | Attempts, active uniqueness, recovery, history | Commit / Persistence Models |
| `OperationKeyBuilder` | deterministic service | Logical professional-operation identity | Commit / Registry Models |
| `FreshnessChecker` | deterministic service | Validate declared freshness dependencies before commit | Commit / Handler Models |
| `BaseOperationHandler` | shared execution framework | Common professional-operation mechanics | Handler Model |
| concrete `OperationHandler`s | operation-specific implementations | Only mechanics not declarative in specification | Handler Model |
| `ExecutionWorker` | async runtime worker | Run/recover professional Execution attempts | Deployment Model |
| `ExecutionResult` | result value object | Stable operation attempt outcome | Handler Model |
| `FailureMapper` | deterministic service | Exception/provider failure → normalized FailureClass | Handler / Persistence Models |

---

# 8. Professional Invocation Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `ProfessionalInvoker` | protocol | Invoke configured professional model/provider | Professional Invocation Model |
| provider adapter | implementation | Provider-specific API/tool call | Invocation Model |
| `RawProfessionalResponse` | provider-neutral value | Untrusted raw model result | Invocation Model |
| `OutputExtractor` | protocol | Parse required staged outputs from raw result | Invocation Model |
| operation output extractors | implementations | JEA/ERQ/ERESP/Resume/WCM/Eval candidates | Invocation Model |
| `StagedArtifact` | value object | Candidate output before authority | Commit / Invocation Models |
| `SchemaValidator` | service | Validate exact authoritative schema | Invocation / Commit Models |
| `ProfessionalResourceLoader` | service | Load exact contract/task/schema/templates | Invocation Model |
| `ProviderConfigResolver` | config service | Professional role → provider/model/settings | Invocation / Deployment Models |
| `InvocationProvenance` | persistent metadata/value object | Exact spec/build/resource/provider identity | Invocation Model |

V0.1 should support a **FakeProfessionalInvoker** before the real provider adapter so the runtime kernel can be tested without AI behavior.

---

# 9. Evidence Retrieval Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `EvidenceSource` | protocol | Provider-neutral professional evidence retrieval | Invocation / Handler Models |
| `EvidenceQuery` | frozen value object | Normalized retrieval intent | Invocation Model |
| `EvidenceSearchResult` | frozen value object | Successful normalized retrieval response | Invocation Model |
| `RetrievedEvidenceItem` | frozen value object | Provider-neutral selected evidence | Invocation Model |
| `EvidenceSourceRegistry` | configuration/service | Resolve configured evidence provider | Invocation / Deployment Models |
| Google Drive adapter | EvidenceSource implementation | Search/read Drive-backed career evidence | Invocation Model |
| retrieval fingerprint builder | deterministic service | Identity of evidence supplied downstream | Invocation / Commit Models |

Critical distinction:

```text
successful retrieval with zero matches
≠
EvidenceSource failure
```

---

# 10. Artifact Storage and Commit Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `ArtifactMetadata` | persistent domain record | Runtime metadata for immutable artifact version | Persistence Model |
| `ArtifactRepository` | repository protocol | Metadata lookup/history | Persistence Model |
| `ArtifactFileStore` | filesystem service | Immutable professional artifact bytes | Persistence Model |
| `StagingStore` | filesystem service | `/data/staging/<execution_id>/` temporary outputs | Commit Model |
| `ArtifactCommitGroup` | persistent domain record | Coupled output atomicity | Commit Model |
| `CommitCoordinator` | authoritative service | Validate and atomically commit professional state | Commit Model |
| `PointerMutationValidator` | deterministic service | Enforce Operation Specification authority | Registry / Commit Models |
| `ArtifactHasher` | service | SHA-256 content identity | Persistence Model |
| `ArtifactVersionAllocator` | deterministic/repository service | Safe immutable next version | Persistence / Commit Models |
| orphan/stale classifier | deterministic service | Noncurrent output classification | Commit Model |

Canonical professional SQLite commit includes:

```text
artifact metadata / commit group
+
authorized Runtime Job mutation
+
Runtime Job revision
+
Execution finalization
+
artifact_committed Event
```

---

# 11. Routing Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `Router` | deterministic service | Evaluate current committed state and select lifecycle | Routing Model |
| `RoutingPredicate` | protocol/function contract | One deterministic schema-grounded condition | Routing Model |
| `RoutingPredicateRegistry` | registry | Predicate name → implementation | Routing Model |
| predicate implementations | pure functions/services | Core V0.1 routing conditions | Routing Model |
| `RoutingDecisionBuilder` | deterministic service | Append-only reason/basis record | Routing Model |
| routing mutation service | repository/coordinator path | Atomic lifecycle + history + revision + event | Routing / Persistence Models |

Initial predicate inventory:

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

# 12. Interaction Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `Interaction` | persistent domain record | Authoritative human-interaction lifecycle | Discord Interaction Model |
| `InteractionMessage` | persistent domain record | Durable conversational message | Discord / Persistence Models |
| `InteractionRepository` | repository protocol | Interaction lifecycle and lookup | Persistence / Discord Models |
| `InteractionMessageRepository` | repository protocol | Message dedupe/order/processing | Discord / Persistence Models |
| `InteractionProcessor` | runtime worker/service | Resolve exact message batch and continue Interviewer | Discord Model |
| `InterviewerContinuationResult` | tagged union | ConversationTurn or CompletedProfessionalArtifact | Discord / Invocation Models |
| `ConversationTurn` | value object | Next interviewer conversational turn | Discord Model |
| `CompletedProfessionalArtifact` | value object | Completed Evidence Response candidate | Discord Model |
| `InteractionProjectionSynchronizer` | deterministic service | Keep RuntimeJob coarse projection consistent | Persistence Model |
| `CompleteInteractionCommandHandler` | command handler | Deterministic post-Evidence-Response completion | Event / Discord Models |

---

# 13. Discord Integration Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `DiscordAdapter` | provider adapter | Provider I/O and normalization | Discord Model |
| `DiscordMessageNormalizer` | adapter/service | Raw provider message → InteractionMessage/Event | Discord / Event Models |
| `DiscordDeliveryService` | external side-effect service | Deliver durable outbound interviewer message | Discord Model |
| `DiscordReconciler` | recovery service | Fetch unseen messages after restart/reconnect | Discord / Deployment Models |
| provider-message dedupe | DB constraint/service | Prevent duplicate human message insertion | Discord / Persistence Models |
| provider chronology ordering | query/service | deterministic conversation order | Discord Model |

---

# 14. Failure / Recovery Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `Failure` | persistent record | Material runtime failure history | Persistence Model |
| `FailureRepository` | repository protocol | Create/read/resolve failures | Persistence Model |
| `RecoveryCoordinator` | startup service | Orchestrate recovery before readiness | Deployment / Persistence Models |
| `ExecutionRecoveryService` | recovery component | Reconcile abandoned Execution attempts | Commit / Persistence Models |
| `CommandRecoveryService` | recovery component | Reclaim expired/abandoned Command work | Event / Deployment Models |
| `EventRecoveryService` | recovery component | Reclaim retryable Event work | Event / Persistence Models |
| `InteractionRecoveryService` | recovery component | Reconstruct active human investigation | Persistence / Discord Models |
| `CommitRecoveryService` | recovery component | Repair incomplete staging/commit state | Commit / Persistence Models |
| projection recovery | recovery component | Repair RuntimeJob.interaction / provider projections | Persistence Model |
| manual-review escalator | deterministic service | Enter blocked/manual-review state when unsafe | Job / Control Surface Models |

---

# 15. Runtime / Deployment Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| runtime daemon | application process | Own runtime worker loops | Deployment Model |
| startup coordinator | application service | config → migrations → validation → recovery → ready | Deployment Model |
| `RuntimeInstance` record | persistence/domain | One daemon process lifetime and ownership | Deployment / Persistence Models |
| migration runner | persistence bootstrap | Apply SQLite schema migrations | Deployment Model |
| configuration loader | infrastructure service | Load paths/provider/runtime settings | Deployment Model |
| secret loader | infrastructure service | Secure provider credentials | Deployment Model |
| structured logging | infrastructure | stdout/stderr runtime diagnostics | Deployment Model |
| health service | application service | Container readiness vs Job health | Deployment Model |
| worker supervisor | application component | Run/restart async Event/Command/Execution/Interaction workers | Deployment Model |
| concurrency limiter | service/config | Global professional-invocation concurrency | Deployment Model |
| Docker image/config | deployment artifact | Single-container V0.1 runtime | Deployment Model |
| persistent `/data` volume | deployment requirement | SQLite + artifact/staging durability | Deployment Model |

---

# 16. CLI / Control Surface Inventory

| Component | Implementation Target | Responsibility | Source |
|---|---|---|---|
| `rrs` CLI application | CLI package | Operator-facing V0.1 control surface | Control Surface Model |
| `job create` | CLI command | Persist deterministic `create_job` Command | Control Surface Model |
| `job show` | CLI command | Read canonical Job state | Control Surface Model |
| `job list` | CLI command | List Jobs | Control Surface Model |
| `job artifacts` | CLI command | Inspect current artifact refs | Control Surface Model |
| `job retry` | CLI command | Request recoverable retry via Command | Control Surface Model |
| `job cancel` | CLI command | Persist cancellation Command | Control Surface Model |
| `job review` | CLI command | Inspect manual review / Failure state | Control Surface Model |
| Runtime Control Service | application service | Shared read/write control API behind CLI | Control Surface Model |
| Job Query Service | application service | Read-only aggregate/diagnostic views | Control Surface Model |

---

# 17. Initial Concrete Operation Inventory

| Operation | Current Professional Binding | Required Implementation |
|---|---|---|
| `generate_analysis` | Researcher | specification + handler + extractor + JEA validation/commit |
| `request_evidence` | Researcher | specification + handler + ERQ extractor/commit |
| `investigate_evidence_request` | Interviewer | specification + continuation handling + Evidence Response commit |
| `integrate_evidence` | Researcher | specification + handler + atomic multi-JER / Evidence Response reconciliation |
| `generate_resume` | Writer | specification + handler + coupled Resume/WCM output commit |
| `evaluate_resume` | Evaluator | specification + handler + Resume Evaluation commit |

The Researcher bindings are V2-compatible professional bindings, not permanent runtime architecture.

---

# 18. Architectural Transaction Inventory

These transactions must become explicit implementation contracts in the later Transaction Matrix.

| Transaction | Atomic Contents |
|---|---|
| Job creation | Runtime Job revision 1 + target pointer + initial JER snapshot + `job_created` + `create_job` completion |
| Event → Command | resulting Command(s) + Event processed |
| Routing transition | routing history + lifecycle state + revision + `lifecycle_changed` |
| Professional artifact commit | artifact metadata/group + authorized state mutation + revision + Execution finalization + `artifact_committed` |
| Coupled Resume/WCM commit | both artifact metadata + commit group + both pointers + revision + Execution + one `artifact_committed` |
| Evidence integration commit | all required new JER versions + consumed Evidence Response mutations + revision + Execution + `artifact_committed` |
| Inbound human message | InteractionMessage + `human_input_received` Event |
| Conversational continuation | exact consumed human messages + next Interviewer message/state |
| Completed Evidence Response | Evidence Response metadata/state + exact consumed human messages + Execution + `artifact_committed` |
| Interaction completion | authoritative Interaction + RuntimeJob interaction projection + revision + `interaction_completed` + Command completion |
| Material failure transition | Failure record + applicable Job health/failure pointer mutation |
| SQLite-local nonprofessional Command | authoritative mutation + resulting Event(s) + Command completion |

---

# 19. Implementation Traceability by Architecture Model

| Architecture Model | Primary Implementation Homes |
|---|---|
| Runtime Job Model | domain/job types, RuntimeJobRepository, CAS mutations |
| Artifact & Execution Commit Model | Execution, operation key, staging, CommitCoordinator, freshness, artifact groups |
| Routing Model | Router, predicates, RoutingDecision |
| Event Model | Event, Command, processors, leases/deduplication |
| Handler Interface Model | OperationHandler protocol, base handler, handler registry |
| Persistence Model | SQLite repositories, filesystem artifact store, migrations, recovery |
| Discord Interaction Model | Interaction, messages, continuation processor, Discord adapter/reconciliation |
| MVP Control Surface Model | CLI, Runtime Control Service, query service |
| Professional Invocation Model | InvocationBundle, ProfessionalInvoker, extractors, EvidenceSource, provenance |
| Operation Specification Registry Model | OperationSpecification, registry, validation, hashing |
| MVP Runtime & Deployment Model | daemon, startup/recovery, worker supervision, config, Docker |

No architecture model is currently without an implementation home.

---

# 20. First Implementation Dependency View

```text
1. Primitive IDs / enums / value objects
2. RuntimeJob + core domain aggregates
3. OperationSpecification domain + registry interfaces
4. SQLite migrations + repository implementations
5. Artifact filesystem / staging infrastructure
6. Event + Command persistence and processors
7. Execution persistence / operation-key mechanics
8. CommitCoordinator
9. Router + predicates
10. FakeProfessionalInvoker + generic handler framework
11. generate_analysis vertical slice
12. remaining straight-through professional operations
13. Interaction / Discord path
14. startup recovery / crash reconciliation hardening
15. CLI completeness + Docker production packaging
```

This is provisional until the Python Domain Model, SQLite Schema, and Transaction Matrix are completed.

---

# 21. Planning Gaps Intentionally Deferred

Later implementation planning must still decide:

- Exact Python package/module names.
- Dataclass vs Pydantic vs another domain representation.
- Sync vs async repository method boundaries.
- SQLite physical normalization details.
- Exact Command processing status vocabulary.
- Exact authoritative Interaction status vocabulary.
- Foreign-key and cascade policies.
- Artifact ID/version allocation mechanism.
- SQL migration framework.
- Concrete retry counts/backoff/timeouts.
- Provider SDK and model configuration.
- Discord SDK.
- Google Drive EvidenceSource implementation mechanism.
- Test framework and crash-injection utilities.
- Dependency injection/bootstrap mechanism.
- CLI framework.

These are implementation decisions, not missing architecture.

---

# 22. Phase 1 Disposition

**PASS — IMPLEMENTATION INVENTORY COMPLETE**

The eleven frozen architecture models map to concrete code responsibilities without requiring another architectural subsystem.

The next planning artifact is the **Python Domain Model**, which will turn this inventory into exact IDs, enums, frozen value objects, domain aggregates, protocols, result types, mutation types, and error/failure types without yet implementing production services.