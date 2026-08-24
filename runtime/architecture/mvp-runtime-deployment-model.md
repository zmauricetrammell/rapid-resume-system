# RRS V3 MVP Runtime and Deployment Model

## Status
Draft V0.16 — FIX-008, FIX-009, FIX-014, FIX-015, FIX-017, FIX-018, FIX-019, FIX-022, FIX-026, FIX-029, FIX-030, and FIX-036 applied; supplemental Operation Specification Registry/startup-validation alignment retained

## Purpose
Define how the V3 MVP runs in Docker with one Python daemon, SQLite, filesystem-backed artifacts, Discord, Google Drive retrieval, and a CLI control surface.

## Core Invariants
1. One active Docker container owns the SQLite database.
2. One long-running Python daemon owns normal runtime processing.
3. Internal workers are cooperative async tasks, not separate services.
4. Short-lived CLI processes may use approved runtime services/repositories against the same SQLite DB.
5. CLI never bypasses runtime mutation rules.
6. SQLite and `/data/artifacts` are persistent; the container image is disposable.
7. Contracts, tasks, schemas, and runtime code are baked into the image from a known Git revision.
8. Secrets stay outside the image and professional/runtime artifacts.
9. Recovery completes before new work is accepted.
10. Discord and Google Drive failures do not corrupt professional state; required EvidenceSource unavailability blocks the affected professional operation as a recoverable failure rather than silently continuing with incomplete evidence.
11. No inbound HTTP server is required for MVP.
12. Trello, Redis, Celery, RabbitMQ, PostgreSQL, Kubernetes, and a web UI are post-MVP.
13. Every daemon process start receives a unique `runtime_instance_id` used for work ownership, leases, logs, and restart reconciliation.
14. The orchestration runtime binds professional roles to operations through configuration/resources; V2 Researcher ownership is not a permanent runtime dependency.
15. Professional operation semantics are loaded from a validated first-class Operation Specification Registry before runtime readiness.
16. Runtime readiness requires a finalized build identity containing Git/build provenance and the deterministic Operation Specification Registry hash.

## 1. Deployment Shape

```text
Docker Host
└── RRS Container
    ├── Python Runtime Daemon
    │   ├── Runtime Control Service
    │   ├── Command Processor
    │   ├── Event Processor
    │   ├── Operation Specification Registry
    │   ├── Handler Registry
    │   ├── Professional Invoker
    │   ├── EvidenceSource Registry
    │   ├── Router
    │   ├── Commit Coordinator
    │   ├── Interaction Processor
    │   ├── Discord Adapter
    │   └── Recovery / Maintenance Service
    └── /data
        ├── rrs.db
        ├── artifacts/
        └── staging/
```

All listed components are Python modules/services inside one process.

## 2. One Python Daemon
V0.1 uses one long-running process with cooperative async tasks.

Conceptually:

```python
async def main():
    runtime = await initialize_runtime()
    await runtime.recover()

    async with asyncio.TaskGroup() as tasks:
        tasks.create_task(command_processor.run())
        tasks.create_task(event_processor.run())
        tasks.create_task(discord_adapter.run())
        tasks.create_task(interaction_processor.run())
        tasks.create_task(maintenance_service.run())
```

The exact implementation may differ.

## 3. Why One Process
This avoids premature needs for distributed queues, service discovery, remote locking, RPC, and multi-service deployment. The architecture remains modular enough to split later.

## 4. Core Component Responsibilities

### Runtime Control Service
Supports operator actions: create/show/list Jobs, inspect artifacts, retry, cancel, review blocked Jobs.

### Command Processor
Claims durable Commands from SQLite, validates current state, dispatches work, records completion.

### Event Processor
Claims normalized Events, derives resulting Commands, and updates Event processing state. It does not invoke AI directly.

### Operation Specification Registry
Loads and validates the immutable declarative specification for each `operation_type`.

### Handler Registry
Maps each specification's `handler_key` to the Python OperationHandler implementation.

### Professional Invoker
Invokes configured AI providers using immutable Invocation Bundles.

### EvidenceSource Registry
Loads evidence-source implementations. V0.1 prefers `GoogleDriveEvidenceSource`.

### Router
Evaluates committed professional state and derives lifecycle transitions.

### Commit Coordinator
Owns staging, validation coordination, freshness checks, immutable artifact persistence, pointer commits, and Runtime Job revision updates.

### Interaction Processor
Owns long-lived Interviewer continuation using persisted ERQ and conversation state.

Before each continuation, it resolves all currently unprocessed authorized human messages into one immutable, deterministically ordered batch.

For ordinary conversational continuation, it atomically marks the exact consumed human-message batch processed and persists the next Interviewer message before Discord delivery.

### Discord Adapter
Owns Discord provider ingress/egress only; no professional reasoning.

### Recovery / Maintenance Service
Handles expired leases, stuck processing state, retry deadlines, paused Interactions, and staging cleanup.

## 5. Command Flow

```text
SQLite Command Store
→ atomically claim Command with:
     runtime_instance_id
     worker_id
     lease_expires_at
→ validate
→ dispatch
→ handler/runtime service
```

Command leases are short-lived queue-processing leases.

If processing legitimately exceeds the lease, the current worker renews it before expiry.

For SQLite-local nonprofessional Commands:

```text
BEGIN
apply authoritative local mutation
persist required resulting Event(s)
mark Command completed
COMMIT
```

For `schedule_operation`:

```text
claim schedule_operation
→ derive/reuse operation_key
→ durably create or reuse active Execution
→ persist required scheduling state/Event
→ mark Command completed
→ release Command lease
→ Execution owns the long-running professional invocation
```

The Command lease is not held through the model/API call.

For external-side-effect Commands:

```text
persist durable local intent
→ call provider
→ persist provider result/reconciliation state
→ persist resulting Event if required
→ mark Command completed
```

Commands survive restart.

A Command is never considered complete merely because a handler returned; its required durable local effects must be persisted.

## 6. Event Flow

```text
SQLite Event Store
→ atomically claim Event with lease ownership
→ process normalized fact
→ BEGIN SQLite transaction
     derive command_dedupe_key where applicable
     persist or reuse resulting Command(s)
     mark Event processed
  COMMIT
→ release Event lease
```

Event leases cover Event processing only.

They do not remain held while downstream Commands or professional Executions run.

If Event processing legitimately exceeds its lease, the worker renews it.

If the lease expires or its runtime instance dies, the Event becomes reclaimable according to recovery rules.

Events are not correctness-dependent on in-memory queues.

## 7. Professional Operation Flow

```text
schedule_operation Command
→ Handler Registry
→ Operation Handler
→ Input Resolver
→ optional EvidenceSource retrieval
→ Professional Invoker
→ Raw response
→ Output Extractor
→ staging/validation/freshness
→ Commit Coordinator
→ artifact_committed Event
```

## 8. Invocation Concurrency
Start conservatively with configurable:

```text
RRS_MAX_MODEL_INVOCATIONS=1
```

or 2 after validation.

Only one pointer-mutating professional operation may commit at a time per Runtime Job.

## 9. Async Provider Calls
Model/API calls may be awaited while unrelated Discord/Event/Command work continues. Runtime Job revision, operation-key idempotency, and commit rules protect consistency.

## 10. Discord Lifecycle
Discord connects only after persistence initialization and core runtime recovery.

After initial connection or any reconnect, the Discord adapter reconciles every active/paused Interaction thread against persisted provider-message boundaries before assuming live gateway state is complete.

Temporary disconnects should reconnect automatically and should not require daemon restart.

## 11. No Required HTTP Server
MVP uses:
- Discord persistent bot connection
- outbound model APIs
- outbound Google Drive access
- local CLI

HTTP may be added later for Trello, REST, or web UI.

## 12. CLI with Running Daemon
Short-lived CLI processes may run via:

```bash
docker exec rrs rrs job show JOB-0001
docker exec rrs rrs job create --target-job /imports/job.pdf
```

They do not start a second daemon.

## 13. CLI Write Path

All mutating CLI actions use durable Commands.

Job creation:

```text
CLI
→ RuntimeControlService
→ allocate command_id + intended job_id
→ persist create_job Command
→ CLI exits
→ daemon claims create_job
→ finalize Target Job artifact
→ resolve latest eligible JER snapshot
→ SQLite transaction:
     create Runtime Job revision 1
     set Target Job pointer
     set initial JER snapshot
     persist job_created Event
     mark create_job Command completed
```

Other mutations follow the same Command-driven control boundary.

The CLI does not directly create or mutate Runtime Job rows.

## 14. CLI Read Path

```text
CLI
→ RuntimeControlService
→ repositories
→ SQLite/artifact metadata
→ output
```

## 14.1 `create_job` Runtime Operation

`create_job` is executed by the daemon as a nonprofessional control-plane Command.

It is short-lived and does not create a professional Execution.

The intended Job ID is stable from Command creation through retries.

The Target Job body is finalized before the Runtime Job becomes authoritative.

After file finalization, the Runtime Job creation transaction includes:

```text
Runtime Job row at revision 1
Target Job artifact metadata/pointer
initial pinned JER set
job_created Event
create_job Command completion
```

If recovery finds the intended Job already created for the same Command, it reconciles and completes the Command rather than creating another Job.

## 15. SQLite Role
SQLite stores:
- Runtime Jobs
- Events
- Commands
- Executions
- Interactions
- Failures
- artifact metadata

Professional artifact bodies remain on filesystem.

Recommended pragmas:

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
```

## 16. SQLite Concurrency Boundary
One active runtime container plus short-lived CLI processes may use one local SQLite DB. Keep transactions short and never hold DB locks around model calls, Discord waits, or Google Drive retrieval.

## 17. Persistent Storage

```text
/data/
├── rrs.db
├── artifacts/
└── staging/
```

`/data` must be a Docker volume or bind mount.

## 18. Disposable Container Rule
Stopping/removing/replacing the container while remounting the same `/data` must preserve all authoritative runtime and artifact history.

## 19. Image Contents
The image should contain:
- runtime code
- agents
- schemas
- resources
- templates
- migrations
- Python dependencies

It should not contain user corpus, generated artifacts, production DB, or secrets.

## 20. Professional Resources Baked into Image
Production contracts/tasks/schemas/templates should come from the image's known Git revision, not a live-mounted repo.

## 20.1 Runtime Instance Identity

Each Python daemon process start generates a unique:

```text
runtime_instance_id
```

Example:

```text
RUN-20260823-ABC123
```

This is distinct from:
- Docker image/build identity,
- Job IDs,
- Execution IDs,
- worker IDs.

Use it for:

```text
Execution owner
Command/Event lease owner
logs
startup recovery
```

A restarted container or daemon receives a new runtime instance ID even when it mounts the same `/data`.

The runtime persists enough instance metadata to identify records owned by prior process lifetimes.

## 21. Runtime Build Identity

Every daemon instance records the immutable runtime build it is executing.

Recommended build identity:

```yaml
runtime_build:
  git_sha: abc123...
  image_digest: sha256:...
  operation_registry_hash: sha256:...
  built_at: ...
```

The registry hash is computed only after the effective Operation Specification Registry passes startup validation.

This identity should be attached to:
- runtime instance metadata,
- Execution provenance,
- Invocation provenance,
- structured logs.

A different material operation specification must produce a different `operation_registry_hash`.

A container may restart with the same build identity but always receives a new `runtime_instance_id`.

## 22. Startup Sequence

```text
1. Load configuration.
2. Validate secrets and environment configuration.
3. Verify `/data` and required persistence paths are writable.
4. Generate the current `runtime_instance_id`.
5. Open SQLite and apply required pragmas.
6. Apply database migrations.
7. Load the Operation Specification Registry.
8. Perform structural, reference, and semantic registry validation.
9. Compute operation specification hashes and `operation_registry_hash`.
10. Finalize and persist runtime build identity.
11. Validate artifact and staging paths.
12. Run lightweight persistence/integrity checks.
13. Recover incomplete Executions, including interrupted prior-runtime provider calls.
14. Recover Events and Commands.
15. Recover Interactions and repair stale runtime references/leases.
16. Reconcile incomplete professional commits and staging state.
17. Verify recovery is complete and registry/build identity remains finalized.
18. Start worker loops.
19. Connect Discord.
20. Reconcile active/paused Discord Interactions for unseen provider messages.
21. Mark runtime ready.
```

New work is not accepted before registry validation, build-identity finalization, and deterministic recovery complete.

## 23. Recovery Before New Work
Reconcile:
- running/validating/committing Executions
- processing/retry Events
- processing/retry Commands
- expired leases
- active Interactions
- staging files
- Runtime Job operation references

## 24. Execution Recovery

Recovery behavior depends on Execution state.

### `running`

A `running` Execution cannot resume a provider call after the owning daemon instance dies.

On startup:

```text
running Execution
+ owner runtime_instance_id is not current/alive
→ prior attempt failed(runtime_interrupted)
```

If retry policy permits:

```text
same operation_key
→ new execution_id
→ next attempt_number
```

Do not leave orphaned attempts marked `running`.

### `validating`

If staged output remains intact under:

```text
/data/staging/<execution_id>/
```

recovery may resume validation without another provider invocation.

Missing/corrupt staging causes the attempt to fail and normal retry policy to apply.

### `committing`

Inspect persisted artifact files, metadata, commit-group state, current Runtime Job pointers, and professional freshness dependencies.

Recover by:
- finishing/retrying the commit when still valid,
- repairing an already-completed commit,
- marking the attempt stale when professional dependencies changed,
- or entering Manual Review if deterministic recovery is unsafe.

Do not blindly re-invoke AI when the prior attempt may already have persisted valid output.


## 25. Event / Command Recovery
Event and Command claims record:

```text
runtime_instance_id
worker_id
lease_expires_at
```

Expired leases or claims owned by a prior runtime instance return work to a claimable retry state.

Active workers may renew leases for legitimate short processing overruns.

Professional model calls are not recovered through Command leases because `schedule_operation` releases its lease after durably creating/reusing the Execution.

Interrupted model work is recovered from Execution state.

Idempotency protects duplicate processing.

## 25.1 Interviewer Continuation Persistence

Before invoking the Interviewer, the Interaction Processor resolves the stable ordered batch of currently unprocessed human messages.

When the Interviewer returns another conversational turn:

```text
BEGIN SQLite transaction
  mark exact consumed human-message IDs processed
  persist next Interviewer message
  update Interaction continuation metadata
COMMIT
→ deliver persisted Interviewer message to Discord
```

A failed transaction leaves the human batch unprocessed so the continuation can retry safely.

If the Interviewer returns a completed Evidence Response, the professional commit pipeline owns the artifact result.

Only after the exact Evidence Response commit succeeds does the runtime schedule `complete_interaction`.

```text
Evidence Response commit
→ artifact_committed
→ complete_interaction
→ Interaction completed
→ interaction_completed
```

Interaction completion is therefore recoverable independently from the professional artifact commit.

## 26. Interaction Recovery

After restart or Discord reconnect:

```text
load active/paused Interactions
→ load persisted Discord thread + last known provider-message boundary
→ fetch provider messages newer than/beyond that boundary
→ deduplicate against persisted provider_message_id values
→ atomically persist each unseen human message + human_input_received Event
→ identify all unprocessed local human messages
→ resume Interviewer continuation
```

When Discord does not support exact boundary queries, fetch a bounded recent window and deduplicate locally.

Conversation continuity comes from SQLite plus provider reconciliation, not model/provider session memory or guaranteed gateway replay.

A Discord outage therefore pauses reconciliation-dependent investigation but does not destroy persisted Interaction state.

Recovery also checks for:

```text
active/paused Interaction
+
already committed Evidence Response for exact current ERQ/version
```

and schedules `complete_interaction` rather than re-running the Interviewer.

## 27. Shutdown Sequence

```text
1. Mark shutting_down.
2. Stop claiming new Commands.
3. Stop claiming new Events.
4. Stop scheduling new professional operations.
5. Stop new interaction work where possible.
6. Allow bounded in-flight work to finish.
7. Persist/release leases.
8. Persist Interaction state.
9. Disconnect Discord.
10. Close/checkpoint SQLite.
11. Exit.
```

## 28. Graceful Shutdown Timeout
Use a configurable grace period. If a model call cannot finish, persist enough Execution state for startup reconciliation and exit rather than blocking forever.

## 29. Abrupt Failure
The system must survive SIGKILL, host reboot, power loss, or process crash using SQLite WAL, immutable artifacts, durable Events/Commands, and startup recovery.

## 30. Configuration
Suggested nonsecret config:

```text
RRS_DATA_DIR=/data
RRS_DB_PATH=/data/rrs.db
RRS_ARTIFACT_ROOT=/data/artifacts
RRS_STAGING_ROOT=/data/staging
RRS_MAX_MODEL_INVOCATIONS=1
RRS_COMMAND_POLL_SECONDS=1
RRS_EVENT_POLL_SECONDS=1
RRS_MAINTENANCE_INTERVAL_SECONDS=30
DISCORD_GUILD_ID=...
DISCORD_CHANNEL_ID=...
RRS_EVIDENCE_SOURCE=google_drive
```

## 31. Secrets
Examples:
- OpenAI/API key
- Discord bot token
- Google Drive credentials/token

Use Docker secrets where convenient or environment variables for MVP. Never store them in artifacts, Runtime Jobs, generic Events, logs, Discord messages, or source control.

## 32. Professional Operation and Model Configuration

Professional operation semantics are defined in the Operation Specification Registry.

For each `operation_type`, the specification resolves:
- handler key,
- lifecycle permissions,
- input/dependency rules,
- retrieval policy,
- professional role/resources,
- schemas/output contract,
- pointer authority,
- reconciliation rules.

The Handler Registry separately resolves:

```text
handler_key → Python handler implementation
```

Provider/model settings remain independently configurable.

Current V2-compatible bindings may remain:

```text
generate_analysis → researcher
request_evidence → researcher
integrate_evidence → researcher
investigate_evidence_request → interviewer
generate_resume → writer
evaluate_resume → evaluator
```

These bindings are provisional.

The future Analyst/Custodian split can update or add Operation Specifications without redesigning deployment topology, Command/Event processing, or the common handler framework.

The runtime image may contain operation specifications, multiple professional role resource sets, handler implementations, schemas, and templates from the known build Git revision.

## 33. EvidenceSource Configuration
V0.1 selects `google_drive`; future deployments may select local filesystem/index/vector implementations.

## 33.1 EvidenceSource Availability

The configured EvidenceSource is a runtime dependency only for operations whose specification requires retrieval.

For a required retrieval operation:

```text
EvidenceSource unavailable
→ do not invoke professional model
→ mark/retry affected Execution as recoverable retrieval failure
→ preserve current professional state
```

Examples include:
- Google Drive API unavailable,
- expired/revoked credentials,
- provider timeout,
- connector failure,
- required source inaccessible.

The runtime must not substitute:

```text
[]
```

for a failed retrieval call.

An empty result is valid only after a successful EvidenceSource query.

Unrelated operations that do not require EvidenceSource access may continue running.

Repeated retrieval failure may move the affected Job to blocked/manual-review state according to normal retry policy, but it never authorizes the agent to reason from a knowingly incomplete required corpus.

## 34. Internal Polling
Simple SQLite polling is sufficient:

```text
Command/Event polling: ~0.5–2s
Maintenance: ~30–60s
```

No Redis is required.

## 35. Internal Wake-Up Optimization
In-process wake-up signals may reduce latency after local inserts, but SQLite remains the durable correctness mechanism.

## 36. Worker Claiming
Workers atomically transition durable work:

```text
pending → processing
```

with worker identity and optional lease expiry.

## 37. Worker Identity
Assign a daemon worker/process identity for leases, logs, and restart diagnostics.

## 38. Maintenance Loop
Periodically inspect expired leases, retry deadlines, dead letters, paused Interactions, orphaned staging files, and integration degradation. No professional reasoning occurs here.

## 39. Staging Cleanup
Clean abandoned staging only after recovery determines it is no longer required. Never delete committed artifact history automatically.

## 39.1 Registry Validation Failure

If the Operation Specification Registry fails startup validation:

```text
daemon initializes enough infrastructure to report failure
→ runtime does not become ready
→ no new Commands are claimed
→ no professional Executions begin
```

The error should identify:
- operation type,
- validation class,
- missing/invalid reference or rule,
- build Git SHA.

Do not allow a live Job to discover deterministic configuration defects that could have been detected at startup.

## 40. Logging
Emit structured logs to stdout/stderr with IDs such as job, execution, event, command, interaction, component. Avoid dumping professional artifact bodies, prompts, transcripts, or secrets.

## 41. Debug Logging
Debug mode may include hashes, operation keys, provider request IDs, revisions, and artifact IDs while still avoiding sensitive content duplication.

## 42. Container Health
Container health asks whether the runtime can operate safely. Check daemon liveness, SQLite access, expected DB schema, artifact-root access, and worker-loop liveness.

## 43. Job Health vs Container Health
A blocked Job does not make the whole container unhealthy.

## 44. Discord Health
Discord outage should pause investigation-dependent Jobs while straight-through Jobs may continue. Temporary disconnect should be treated as capability degradation.

## 45. Google Drive Health
Drive failure affects retrieval-dependent Executions and should normally create a recoverable failure, not daemon death.

## 46. Model Provider Health
Provider outage affects professional Executions and retries; current committed state remains safe.

## 47. Liveness vs Readiness
Conceptually separate process liveness from runtime readiness. Readiness requires startup/migrations/recovery complete.

## 48. No HTTP Health Endpoint Required
A CLI-based Docker health command is sufficient:

```bash
rrs runtime health
```

## 49. Health CLI Example

```text
Runtime: ready
SQLite: healthy
Artifact store: healthy
Command worker: healthy
Event worker: healthy
Discord: connected
Evidence source: available
```

## 50. Docker Healthcheck
Conceptually:

```dockerfile
HEALTHCHECK CMD rrs runtime health --quiet || exit 1
```

## 51. Upgrade Flow

```text
backup /data
→ stop old container
→ deploy new image
→ mount same /data
→ run migrations
→ startup recovery
→ resume
```

## 52. Migration Safety
DB migrations finish before workers start. Migration failure prevents runtime readiness.

## 53. Professional Resource Upgrade
Changes to contracts/tasks/schemas/templates/runtime code should normally produce a new Git commit and image. Historical artifacts remain associated with the resources that produced them.

## 54. Backup Boundary
Authoritative backup:
- `/data/rrs.db`
- `/data/artifacts/`

Secrets are backed up separately.

## 55. Runtime Data Authority
Authoritative:
- SQLite runtime state
- artifact filesystem

Rebuildable/projection:
- Discord thread presentation
- future Trello board
- logs
- caches/indexes

## 56. Security Boundary
No inbound HTTP port is exposed by default. Outbound dependencies are the model provider, Discord, and Google Drive.

## 57. Container User
Production should eventually run as non-root with write access only where needed, primarily `/data`.

## 58. Filesystem Permissions
Daemon and short-lived CLI must safely share access to the DB/artifact paths without broadly exposing writable permissions.

## 59. Required MVP Dependencies

```text
Docker
Python
SQLite
configured AI provider
Discord
Google Drive evidence source
persistent filesystem
```

## 60. Explicit Non-Goals

```text
Trello
PostgreSQL
Redis
Celery
RabbitMQ
Kafka
Kubernetes
multi-container workers
horizontal scaling
web dashboard
REST API
public HTTP server
parallel ERQ investigation in one Job
advanced metrics stack
distributed tracing
```

## 61. Straight-Through MVP Path

```text
CLI persists create_job
→ daemon creates Target Job + Runtime Job
→ job_created
→ analysis
→ JEA commit
→ routing
→ resume generation
→ Resume + WCM commit
→ evaluation
→ ready_to_submit
→ complete
```

## 62. Evidence MVP Path

```text
CLI create Job
→ analysis
→ ERQ
→ Discord thread
→ human + Interviewer
→ Evidence Response
→ evidence integration
→ re-analysis
→ resume
→ evaluation
→ complete
```

## 63. Restart Requirement
At any nonterminal point, restarting the container must not require manual reconstruction of normal runtime state. Persisted human answers should not need to be repeated.

## V0.1 Acceptance Criteria

- [ ] Runtime readiness requires successful registry validation and finalized registry/build identity.
- [ ] Runtime build identity includes Git/build provenance and `operation_registry_hash`.
- [ ] Invalid operation specifications prevent new work from being accepted.

- [ ] Operation Specification Registry loads and validates before runtime readiness.
- [ ] Handler Registry and Operation Specification Registry have separate responsibilities.
- [ ] Runtime professional bindings, pointer authority, retrieval rules, and output contracts come from declarative operation specifications.

- [ ] One Docker container runs the MVP.
- [ ] One Python daemon owns runtime processing.
- [ ] Internal workers are async components inside the daemon.
- [ ] No inbound HTTP server is required.
- [ ] Short-lived CLI processes safely use the same SQLite persistence.
- [ ] Job creation occurs through a durable `create_job` Command with a stable intended `job_id`.
- [ ] Retrying one `create_job` Command cannot create duplicate Runtime Jobs.
- [ ] CLI does not start a second daemon.
- [ ] SQLite persists Jobs, Commands, Events, Executions, Interactions, and metadata.
- [ ] Professional artifacts persist under `/data/artifacts`.
- [ ] `/data` survives container recreation.
- [ ] Runtime resources are baked into the image from a known Git revision.
- [ ] Secrets remain outside image/repo/artifacts.
- [ ] Migrations and recovery finish before normal work starts.
- [ ] Incomplete Executions/Events/Commands recover safely.
- [ ] Every daemon start generates a unique `runtime_instance_id`.
- [ ] Execution and lease ownership records the daemon instance that owns the work.
- [ ] Event and Command leases are short-lived, renewable, and reclaimable after expiry or daemon loss.
- [ ] `schedule_operation` releases its Command lease after durable Execution creation/reuse.
- [ ] Long model/API calls are owned by Execution lifecycle rather than queue leases.
- [ ] Startup recovery can reclaim work owned by prior runtime instances.
- [ ] A provider invocation cannot remain `running` after its owning runtime instance dies.
- [ ] Runtime interruption retries professional work through a new Execution attempt under the same logical `operation_key`.
- [ ] Intact staged output may resume validation after restart without unnecessary model re-invocation.
- [ ] Active Discord investigation resumes after restart.
- [ ] Interviewer continuation atomically consumes its exact human-message batch and persists the next conversational turn.
- [ ] Evidence Response commit and Interaction completion remain separate recoverable steps.
- [ ] An Interaction cannot complete before the exact Evidence Response for its current ERQ/version is committed.
- [ ] Discord delivery occurs only after the next Interviewer message is durable.
- [ ] Discord startup/reconnect fetches unseen messages for active/paused Interactions using the persisted provider boundary.
- [ ] Messages sent during daemon downtime do not depend on live gateway replay for recovery.
- [ ] Command/Event processors use durable SQLite records.
- [ ] Deterministic Event-produced Commands use dedupe keys so Event replay does not duplicate requested runtime actions.
- [ ] Event-produced Commands and successful Event completion commit atomically in SQLite.
- [ ] SQLite-local nonprofessional Command effects, required resulting Event(s), and Command completion are atomic.
- [ ] External-side-effect Commands use durable local intent plus reconciliation instead of assuming cross-system atomicity.
- [ ] Professional invocations may run asynchronously.
- [ ] Global professional-invocation concurrency is configurable.
- [ ] Per-Job pointer mutation remains protected.
- [ ] Discord failure does not corrupt professional state.
- [ ] Google Drive failure does not crash the runtime.
- [ ] Provider failure is isolated to affected Executions.
- [ ] Container health is distinct from Job health.
- [ ] Logs use stdout/stderr.
- [ ] Runtime works without Trello, Redis, PostgreSQL, or a web UI.
- [ ] Future HTTP/Trello/distributed deployment can be added without changing professional-state semantics.

## MVP Architecture Design Completion

The planned V3 MVP runtime architecture now consists of:

```text
1. Runtime Job Model
2. Artifact and Execution Commit Model
3. Routing Model
4. Event Model
5. Handler Interface and Responsibility Model
6. Persistence Model
7. Discord Interaction Model
8. MVP Control Surface Model
9. Professional Invocation Model
10. Operation Specification Registry Model
11. MVP Runtime and Deployment Model
```

## Next Phase

Proceed to **architecture reconciliation and implementation planning**.

Before production Python, audit the ten models together for:
- duplicated concepts,
- contradictory state names,
- missing interfaces,
- Analyst/Custodian impacts,
- MVP vs post-MVP boundaries,
- required schemas,
- package/repository structure,
- implementation dependency order.

Then translate the reconciled architecture into Python types, SQLite migrations, interfaces, and tests.