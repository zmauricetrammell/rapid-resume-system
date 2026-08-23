# RRS V3 MVP Runtime and Deployment Model

## Status
Draft V0.1

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
10. Discord and Google Drive failures degrade affected capabilities without corrupting professional state.
11. No inbound HTTP server is required for MVP.
12. Trello, Redis, Celery, RabbitMQ, PostgreSQL, Kubernetes, and a web UI are post-MVP.

## 1. Deployment Shape

```text
Docker Host
└── RRS Container
    ├── Python Runtime Daemon
    │   ├── Runtime Control Service
    │   ├── Command Processor
    │   ├── Event Processor
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

### Handler Registry
Maps `operation_type` to the correct OperationHandler.

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

### Discord Adapter
Owns Discord provider ingress/egress only; no professional reasoning.

### Recovery / Maintenance Service
Handles expired leases, stuck processing state, retry deadlines, paused Interactions, and staging cleanup.

## 5. Command Flow

```text
SQLite Command Store
→ claim Command
→ validate
→ dispatch
→ handler/runtime service
→ persist resulting state/Events
→ mark completed
```

Commands survive restart.

## 6. Event Flow

```text
SQLite Event Store
→ claim Event
→ process normalized fact
→ persist resulting Command(s)
→ mark processed
```

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
Discord connects only after persistence initialization and recovery. Temporary disconnects should reconnect automatically and should not require daemon restart.

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

```text
CLI
→ RuntimeControlService
→ durable Command / defined Job-creation transaction
→ CLI exits
→ daemon processes pending work
```

## 14. CLI Read Path

```text
CLI
→ RuntimeControlService
→ repositories
→ SQLite/artifact metadata
→ output
```

## 15. SQLite Role
SQLite stores:
- Runtime Jobs
- Events
- Commands
- Executions
- Interactions
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

## 21. Runtime Build Identity
Track:
- RRS version
- Git SHA
- Docker image tag/version
- build timestamp if useful

Executions should be traceable to this build identity.

## 22. Startup Sequence

```text
1. Load config.
2. Validate secrets/config.
3. Verify /data exists and is writable.
4. Open SQLite.
5. Apply pragmas.
6. Apply DB migrations.
7. Validate artifact/staging paths.
8. Run lightweight persistence checks.
9. Recover incomplete Executions.
10. Recover Events.
11. Recover Commands.
12. Recover Interactions.
13. Repair stale runtime references/leases.
14. Start worker loops.
15. Connect Discord.
16. Mark runtime ready.
```

New work is not accepted before recovery completes.

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
Inspect persisted artifacts, metadata, Runtime Job pointers, and input freshness. Recover by finishing commit, repairing Execution state, marking stale, retrying safely, or entering Manual Review. Do not blindly re-invoke AI.

## 25. Event / Command Recovery
Expired processing ownership returns work to a claimable retry state. Idempotency protects duplicate processing.

## 26. Interaction Recovery
After restart:

```text
load active/paused Interactions
→ reconcile Discord thread state
→ find unprocessed human messages
→ resume Interviewer continuation
```

No provider-side chat memory is required.

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

## 32. Model Configuration
Model/provider settings belong to runtime configuration. Later Analyst/Custodian mappings may replace Researcher without changing deployment topology.

## 33. EvidenceSource Configuration
V0.1 selects `google_drive`; future deployments may select local filesystem/index/vector implementations.

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
CLI create Job
→ durable command/state
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

- [ ] One Docker container runs the MVP.
- [ ] One Python daemon owns runtime processing.
- [ ] Internal workers are async components inside the daemon.
- [ ] No inbound HTTP server is required.
- [ ] Short-lived CLI processes safely use the same SQLite persistence.
- [ ] CLI does not start a second daemon.
- [ ] SQLite persists Jobs, Commands, Events, Executions, Interactions, and metadata.
- [ ] Professional artifacts persist under `/data/artifacts`.
- [ ] `/data` survives container recreation.
- [ ] Runtime resources are baked into the image from a known Git revision.
- [ ] Secrets remain outside image/repo/artifacts.
- [ ] Migrations and recovery finish before normal work starts.
- [ ] Incomplete Executions/Events/Commands recover safely.
- [ ] Active Discord investigation resumes after restart.
- [ ] Command/Event processors use durable SQLite records.
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
10. MVP Runtime and Deployment Model
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