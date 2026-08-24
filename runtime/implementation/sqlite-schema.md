# RRS V3 SQLite Physical Schema and Migration Model

## Status

Implementation Planning — Phase 3

## Purpose

This document translates the frozen V3 persistence architecture and Python domain model into a concrete SQLite physical design.

It defines authoritative tables, keys, constraints, indexes, compare-and-swap fields, leases, persistence normalization, migration strategy, and transaction-relevant storage boundaries.

It does **not** yet define every cross-table transaction sequence. Those belong to `transaction-matrix.md`.

The design goal is:

```text
Python domain contracts
→ stable relational representation
→ repository implementations
→ architecture-defined atomic transactions
```

---

# 1. SQLite Baseline

V0.1 standard:

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;
PRAGMA busy_timeout=5000;
```

Exact tuning may change during implementation, but WAL and foreign keys are required for the single-container MVP.

Canonical database path:

```text
/data/rrs.db
```

One active runtime container owns the database.

---

# 2. Migration Strategy

Recommended:

```text
runtime/
└── migrations/
    ├── 0001_core.sql
    ├── 0002_indexes.sql
    ├── 0003_provenance.sql
    └── ...
```

Migration tracking:

```sql
CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);
```

Rules:

- migrations are strictly ordered;
- applied migrations are immutable;
- migration failure prevents runtime readiness;
- destructive changes never run silently.

---

# 3. Timestamp and JSON Rules

Store authoritative timestamps as UTC ISO-8601 `TEXT`.

Use normalized columns for data involved in joins, uniqueness, indexes, routing, claims, CAS, recovery, or referential integrity.

Use JSON only for structured payloads not required for relational correctness, such as:

```text
event payload
command payload
provider metadata
input snapshot serialization
invocation provenance details
```

Do not hide authority fields in JSON.

---

# 4. Runtime Instances

```sql
CREATE TABLE runtime_instances (
    runtime_instance_id TEXT PRIMARY KEY,
    git_sha TEXT NOT NULL,
    image_digest TEXT,
    operation_registry_hash TEXT NOT NULL,
    built_at TEXT,
    started_at TEXT NOT NULL,
    stopped_at TEXT
);
```

Index:

```sql
CREATE INDEX idx_runtime_instances_started_at
ON runtime_instances(started_at);
```

---

# 5. Runtime Jobs

```sql
CREATE TABLE runtime_jobs (
    job_id TEXT PRIMARY KEY,

    revision INTEGER NOT NULL CHECK (revision >= 1),

    lifecycle_phase TEXT NOT NULL,
    lifecycle_entered_at TEXT NOT NULL,

    operation_status TEXT NOT NULL,
    operation_type TEXT,
    operation_execution_id TEXT,
    operation_started_at TEXT,

    interaction_status TEXT NOT NULL,
    interaction_type TEXT,
    interaction_id TEXT,
    interaction_started_at TEXT,
    interaction_last_activity_at TEXT,

    health_status TEXT NOT NULL,
    health_failure_id TEXT,
    health_retry_count INTEGER NOT NULL DEFAULT 0 CHECK (health_retry_count >= 0),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT
);
```

Indexes:

```sql
CREATE INDEX idx_runtime_jobs_lifecycle_phase
ON runtime_jobs(lifecycle_phase);

CREATE INDEX idx_runtime_jobs_health_status
ON runtime_jobs(health_status);

CREATE INDEX idx_runtime_jobs_operation_status
ON runtime_jobs(operation_status);

CREATE INDEX idx_runtime_jobs_interaction_status
ON runtime_jobs(interaction_status);
```

CAS mutation:

```sql
UPDATE runtime_jobs
SET revision = revision + 1,
    updated_at = ?,
    ...
WHERE job_id = ?
  AND revision = ?;
```

`rowcount == 0` maps to `ConcurrencyConflict`.

---

# 6. Professional Artifact Metadata

```sql
CREATE TABLE artifacts (
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL CHECK (artifact_version >= 1),
    artifact_type TEXT NOT NULL,
    storage_uri TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    runtime_status TEXT NOT NULL,

    committed_by_execution_id TEXT,
    operation_key TEXT,
    committed_at TEXT,
    created_at TEXT NOT NULL,

    PRIMARY KEY (artifact_id, artifact_version),
    UNIQUE (storage_uri)
);
```

Indexes:

```sql
CREATE INDEX idx_artifacts_type
ON artifacts(artifact_type);

CREATE INDEX idx_artifacts_operation_key
ON artifacts(operation_key);

CREATE INDEX idx_artifacts_execution
ON artifacts(committed_by_execution_id);

CREATE INDEX idx_artifacts_runtime_status
ON artifacts(runtime_status);
```

Currentness is derived from Runtime Job pointers. There is no `superseded` status.

---

# 7. Runtime Job Scalar Artifact Pointers

```sql
CREATE TABLE job_artifact_pointers (
    job_id TEXT NOT NULL,
    pointer_type TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,

    PRIMARY KEY (job_id, pointer_type),

    FOREIGN KEY (job_id)
        REFERENCES runtime_jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (artifact_id, artifact_version)
        REFERENCES artifacts(artifact_id, artifact_version)
);
```

Canonical pointers:

```text
target_job
jea
resume
wcm
evaluation
```

---

# 8. Runtime Job Artifact Collections

```sql
CREATE TABLE job_artifact_collection_members (
    job_id TEXT NOT NULL,
    collection_type TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,

    PRIMARY KEY (job_id, collection_type, artifact_id),

    FOREIGN KEY (job_id)
        REFERENCES runtime_jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (artifact_id, artifact_version)
        REFERENCES artifacts(artifact_id, artifact_version)
);
```

Canonical collections:

```text
jer_set
active_erqs
unintegrated_evidence_responses
```

Using `artifact_id` in the primary key supports `UPSERT_VERSION` semantics for one logical artifact in a collection.

---

# 9. Routing History

```sql
CREATE TABLE routing_decisions (
    decision_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    decided_at TEXT NOT NULL,

    from_phase TEXT NOT NULL,
    to_phase TEXT NOT NULL,

    predicate_name TEXT NOT NULL,
    predicate_result INTEGER NOT NULL CHECK (predicate_result IN (0,1)),

    reason TEXT NOT NULL,
    execution_id TEXT,
    basis_json TEXT NOT NULL,

    FOREIGN KEY (job_id)
        REFERENCES runtime_jobs(job_id)
        ON DELETE CASCADE
);
```

Index:

```sql
CREATE INDEX idx_routing_decisions_job_time
ON routing_decisions(job_id, decided_at);
```

---

# 10. Executions

```sql
CREATE TABLE executions (
    execution_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    owner_runtime_instance_id TEXT NOT NULL,

    operation_type TEXT NOT NULL,
    operation_key TEXT NOT NULL,
    attempt_number INTEGER NOT NULL CHECK (attempt_number >= 1),

    status TEXT NOT NULL,

    input_snapshot_json TEXT NOT NULL,
    staged_outputs_json TEXT NOT NULL DEFAULT '[]',
    committed_outputs_json TEXT NOT NULL DEFAULT '[]',

    failure_id TEXT,

    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,

    FOREIGN KEY (job_id)
        REFERENCES runtime_jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (owner_runtime_instance_id)
        REFERENCES runtime_instances(runtime_instance_id),

    UNIQUE (operation_key, attempt_number)
);
```

Indexes:

```sql
CREATE INDEX idx_executions_job
ON executions(job_id);

CREATE INDEX idx_executions_operation_key
ON executions(operation_key);

CREATE INDEX idx_executions_status
ON executions(status);

CREATE INDEX idx_executions_owner_status
ON executions(owner_runtime_instance_id, status);
```

One active Execution per logical operation:

```sql
CREATE UNIQUE INDEX uq_executions_one_active_per_operation_key
ON executions(operation_key)
WHERE status IN (
    'created',
    'queued',
    'running',
    'output_received',
    'validating',
    'validated',
    'committing'
);
```

---

# 11. Artifact Commit Groups

```sql
CREATE TABLE artifact_commit_groups (
    commit_group_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    committed_at TEXT,

    FOREIGN KEY (execution_id)
        REFERENCES executions(execution_id)
        ON DELETE CASCADE
);
```

```sql
CREATE TABLE artifact_commit_group_members (
    commit_group_id TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,

    PRIMARY KEY (commit_group_id, artifact_id, artifact_version),

    FOREIGN KEY (commit_group_id)
        REFERENCES artifact_commit_groups(commit_group_id)
        ON DELETE CASCADE,

    FOREIGN KEY (artifact_id, artifact_version)
        REFERENCES artifacts(artifact_id, artifact_version)
);
```

Recommended status vocabulary:

```text
pending
committed
abandoned
```

---

# 12. Events

```sql
CREATE TABLE events (
    event_id TEXT PRIMARY KEY,

    event_type TEXT NOT NULL,
    job_id TEXT,

    payload_json TEXT NOT NULL,
    source_category TEXT NOT NULL,
    source_provider TEXT NOT NULL,
    provider_event_id TEXT,

    correlation_id TEXT,
    causation_id TEXT,

    criticality TEXT NOT NULL,
    status TEXT NOT NULL,

    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    last_error TEXT,

    owner_runtime_instance_id TEXT,
    lease_expires_at TEXT,

    created_at TEXT NOT NULL,
    processed_at TEXT,

    FOREIGN KEY (job_id)
        REFERENCES runtime_jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (owner_runtime_instance_id)
        REFERENCES runtime_instances(runtime_instance_id)
);
```

Provider dedupe:

```sql
CREATE UNIQUE INDEX uq_events_provider_identity
ON events(source_provider, provider_event_id)
WHERE provider_event_id IS NOT NULL;
```

Claim/recovery indexes:

```sql
CREATE INDEX idx_events_status_created
ON events(status, created_at);

CREATE INDEX idx_events_job
ON events(job_id);

CREATE INDEX idx_events_owner_lease
ON events(owner_runtime_instance_id, lease_expires_at);
```

---

# 13. Commands

```sql
CREATE TABLE commands (
    command_id TEXT PRIMARY KEY,

    command_type TEXT NOT NULL,
    job_id TEXT,

    payload_json TEXT NOT NULL,
    status TEXT NOT NULL,

    dedupe_key TEXT,
    causation_event_id TEXT,

    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    last_error TEXT,

    owner_runtime_instance_id TEXT,
    lease_expires_at TEXT,

    created_at TEXT NOT NULL,
    completed_at TEXT,

    FOREIGN KEY (job_id)
        REFERENCES runtime_jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (causation_event_id)
        REFERENCES events(event_id),

    FOREIGN KEY (owner_runtime_instance_id)
        REFERENCES runtime_instances(runtime_instance_id)
);
```

Dedupe:

```sql
CREATE UNIQUE INDEX uq_commands_dedupe_key
ON commands(dedupe_key)
WHERE dedupe_key IS NOT NULL;
```

Indexes:

```sql
CREATE INDEX idx_commands_status_created
ON commands(status, created_at);

CREATE INDEX idx_commands_job
ON commands(job_id);

CREATE INDEX idx_commands_owner_lease
ON commands(owner_runtime_instance_id, lease_expires_at);
```

---

# 14. Interactions

```sql
CREATE TABLE interactions (
    interaction_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,

    interaction_type TEXT NOT NULL,
    provider TEXT NOT NULL,

    provider_context_json TEXT NOT NULL,
    professional_context_json TEXT NOT NULL,

    status TEXT NOT NULL,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,

    FOREIGN KEY (job_id)
        REFERENCES runtime_jobs(job_id)
        ON DELETE CASCADE
);
```

Indexes:

```sql
CREATE INDEX idx_interactions_job_status
ON interactions(job_id, status);

CREATE INDEX idx_interactions_provider
ON interactions(provider);
```

One active Interaction per Job:

```sql
CREATE UNIQUE INDEX uq_interactions_one_active_per_job
ON interactions(job_id)
WHERE status IN ('pending', 'active', 'paused');
```

---

# 15. Interaction Messages

```sql
CREATE TABLE interaction_messages (
    message_id TEXT PRIMARY KEY,
    interaction_id TEXT NOT NULL,

    provider TEXT NOT NULL,
    provider_message_id TEXT,
    provider_created_at TEXT,

    direction TEXT NOT NULL,
    message_type TEXT NOT NULL,

    content_text TEXT,
    content_ref TEXT,

    persisted_at TEXT NOT NULL,
    processed_at TEXT,
    processed_by_continuation_id TEXT,

    FOREIGN KEY (interaction_id)
        REFERENCES interactions(interaction_id)
        ON DELETE CASCADE
);
```

Provider dedupe:

```sql
CREATE UNIQUE INDEX uq_interaction_messages_provider_id
ON interaction_messages(provider, provider_message_id)
WHERE provider_message_id IS NOT NULL;
```

Batch index:

```sql
CREATE INDEX idx_interaction_messages_unprocessed
ON interaction_messages(
    interaction_id,
    processed_at,
    provider_created_at,
    provider_message_id
);
```

Canonical inbound ordering:

```sql
ORDER BY provider_created_at ASC, provider_message_id ASC;
```

---

# 16. Failures

```sql
CREATE TABLE failures (
    failure_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,

    execution_id TEXT,
    event_id TEXT,
    command_id TEXT,
    interaction_id TEXT,

    failure_class TEXT NOT NULL,
    message TEXT NOT NULL,
    details_ref TEXT,

    created_at TEXT NOT NULL,
    resolved_at TEXT,
    resolution_message TEXT,

    FOREIGN KEY (job_id)
        REFERENCES runtime_jobs(job_id)
        ON DELETE CASCADE
);
```

Indexes:

```sql
CREATE INDEX idx_failures_job_resolved
ON failures(job_id, resolved_at);

CREATE INDEX idx_failures_execution
ON failures(execution_id);

CREATE INDEX idx_failures_event
ON failures(event_id);

CREATE INDEX idx_failures_command
ON failures(command_id);

CREATE INDEX idx_failures_interaction
ON failures(interaction_id);
```

Failure history persists after resolution.

---

# 17. Invocation Provenance

```sql
CREATE TABLE invocation_provenance (
    invocation_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL UNIQUE,

    operation_type TEXT NOT NULL,
    operation_specification_hash TEXT NOT NULL,
    operation_registry_hash TEXT NOT NULL,

    runtime_git_sha TEXT NOT NULL,
    runtime_image_digest TEXT,

    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    provider_request_id TEXT,

    resources_json TEXT NOT NULL,
    usage_json TEXT,
    latency_ms INTEGER,

    started_at TEXT NOT NULL,
    completed_at TEXT,

    FOREIGN KEY (execution_id)
        REFERENCES executions(execution_id)
        ON DELETE CASCADE
);
```

Index:

```sql
CREATE INDEX idx_invocation_provider_request
ON invocation_provenance(provider, provider_request_id);
```

Semantic Operation Specification identity and Git/build provenance remain separate.

---

# 18. Optional Operation-Spec Build Table

Not required for MVP, but available for diagnostics:

```sql
CREATE TABLE operation_specification_builds (
    operation_registry_hash TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    operation_specification_hash TEXT NOT NULL,
    loaded_at TEXT NOT NULL,

    PRIMARY KEY (operation_registry_hash, operation_type)
);
```

Recommendation:

```text
optional V0.1
```

---

# 19. Queue Claim Semantics

Event and Command claims must be atomic.

Conceptual pattern:

```sql
BEGIN IMMEDIATE;

SELECT command_id
FROM commands
WHERE status IN ('pending', 'retry_pending')
  AND (
      owner_runtime_instance_id IS NULL
      OR lease_expires_at < :now
  )
ORDER BY created_at
LIMIT 1;

UPDATE commands
SET status = 'processing',
    owner_runtime_instance_id = :runtime_instance_id,
    lease_expires_at = :lease_expires_at,
    attempt_count = attempt_count + 1
WHERE command_id = :command_id;

COMMIT;
```

If deployed SQLite supports `UPDATE ... RETURNING` cleanly, implementation may use that instead.

Professional provider calls do not remain protected by Event/Command leases. Execution ownership is separate.

---

# 20. Cross-Record Transaction Support

The schema must allow these architecture-defined mutations within one SQLite transaction:

```text
Job creation
Event → Command
Routing transition
Professional commit
Coupled Resume/WCM commit
Evidence integration commit
Inbound human message
Conversational continuation
Completed Evidence Response
Interaction completion
Material failure transition
```

All relevant control-plane tables therefore share one SQLite database.

Exact transaction contents belong in `transaction-matrix.md`.

---

# 21. Foreign-Key Cycle Handling

Conceptual references include cycles such as:

```text
RuntimeJob.operation_execution_id
→ Execution

Execution.job_id
→ RuntimeJob
```

Recommended implementation approach:

- nullable current-projection foreign keys;
- insert Runtime Job first;
- insert Execution second;
- update current projection transactionally;
- keep referential integrity rather than removing FKs for convenience.

---

# 22. Delete Policy

Production V0.1 should strongly prefer no hard delete for authoritative history.

Retain:

```text
Runtime Jobs
artifacts
Executions
Events
Commands
Interactions/messages
Failures
Routing decisions
Invocation provenance
```

`ON DELETE CASCADE` is mainly useful for development/test cleanup, not normal production lifecycle.

---

# 23. Artifact Version Allocation

Do not perform `MAX(version) + 1` outside a transaction.

For the single-writer MVP, recommended approach:

```text
transaction-scoped version allocation under SQLite write lock
```

A dedicated allocator table can be introduced later if implementation pressure justifies it.

---

# 24. Retrieval Result Persistence

V0.1 does not require standalone retrieval tables.

Retrieval identity/provenance can live in:

```text
Execution.input_snapshot_json
+
invocation_provenance.resources_json
```

If retrieval needs independent querying later, add dedicated tables in a future migration.

---

# 25. Runtime Job Reconstruction

`RuntimeJobRepository.get(job_id)` reads:

```text
runtime_jobs
job_artifact_pointers
job_artifact_collection_members
routing_decisions
```

It does not load professional artifact bodies.

Returned collection ordering must be deterministic.

Recommended:

```sql
ORDER BY collection_type, artifact_id, artifact_version;
```

---

# 26. SQLite Error Mapping

Normalize infrastructure failures:

```text
Runtime Job CAS rowcount 0
→ ConcurrencyConflict

active operation unique violation
→ active Execution conflict / idempotency reconciliation

artifact primary-key conflict with different content
→ ArtifactStorageConflict

foreign-key violation
→ RuntimeIntegrityError

busy/locked beyond configured timeout
→ PersistenceFailure
```

Raw SQLite exceptions should not leak into professional handlers.

---

# 27. Repository Mapping

| Repository | Primary Tables |
|---|---|
| RuntimeJobRepository | runtime_jobs, job_artifact_pointers, job_artifact_collection_members, routing_decisions |
| ArtifactRepository | artifacts, artifact_commit_groups, artifact_commit_group_members |
| ExecutionRepository | executions |
| EventRepository | events |
| CommandRepository | commands |
| InteractionRepository | interactions |
| InteractionMessageRepository | interaction_messages |
| FailureRepository | failures |
| InvocationProvenanceRepository | invocation_provenance |
| RuntimeInstanceRepository | runtime_instances |

Cross-repository authoritative mutations require a shared transaction context.

---

# 28. Unit-of-Work Requirement

The schema confirms the need for:

```text
one SQLite connection
→ multiple repository operations
→ one atomic transaction
```

Conceptual later interface:

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

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

Final interface belongs in `package-interface-plan.md`.

---

# 29. Staging Storage

Staging remains filesystem state:

```text
/data/staging/<execution_id>/
```

SQLite records enough Execution/staged-output metadata to reconcile after restart.

Staging is garbage-collected only after safe terminal reconciliation.

---

# 30. Backup Boundary

Authoritative durable state is:

```text
/data/rrs.db
+
/data/artifacts/
```

A valid backup must preserve both.

Use the SQLite online backup API or another WAL-safe method rather than naively copying a live database file.

---

# 31. Constraint Summary

Database-enforced invariants:

```text
RuntimeJob revision >= 1
ArtifactVersion >= 1
Execution attempt_number >= 1
one active Execution per operation_key
one provider Event per provider_event_id
one Command per dedupe_key
one provider InteractionMessage per provider_message_id
one active Interaction per Job
artifact pointers reference real artifact versions
collection members reference real artifact versions
```

Service-enforced invariants:

```text
Operation Specification authority
professional freshness
coupled-output semantics
routing predicates
Interaction projection semantics
Failure severity policy
artifact hash/content correctness
```

SQLite should enforce what it can know without embedding professional reasoning.

---

# 32. Initial Migration Decomposition

Recommended MVP decomposition:

```text
0001_core.sql
0002_indexes.sql
0003_provenance.sql
```

A more granular split is also acceptable, but correctness and reviewability matter more than one-file-per-table purity.

---

# 33. Startup Validation

Before runtime readiness:

- migrations complete successfully;
- `foreign_keys` is enabled;
- WAL is enabled;
- required tables exist;
- required indexes exist;
- database is writable;
- schema version is compatible with the runtime build.

Failure means:

```text
runtime not ready
```

---

# 34. Open Decisions

Still deferred:

- final migration library;
- exact Command status enum;
- exact FailureClass completeness;
- whether routing basis stays JSON;
- whether operation-spec build rows are persisted;
- exact artifact version allocator algorithm;
- exact UnitOfWork API;
- async SQLite library;
- busy-timeout tuning;
- staging garbage collection.

None require architecture redesign.

---

# 35. Phase 3 Acceptance Criteria

The SQLite schema plan is complete when:

- [ ] every persistent V0.1 domain record has a table or explicit non-table persistence decision;
- [ ] Runtime Job CAS has a concrete storage mechanism;
- [ ] one active Execution per `operation_key` is database-enforced;
- [ ] Event provider dedupe is database-enforced;
- [ ] Command dedupe is database-enforced;
- [ ] Interaction Message provider dedupe is database-enforced;
- [ ] one active Interaction per Job is database-enforced;
- [ ] artifact pointers and collections reference exact immutable versions;
- [ ] Failure history is persistent;
- [ ] Invocation provenance separates semantic spec identity from Git/build provenance;
- [ ] architecture-defined cross-record transactions can share one SQLite transaction;
- [ ] filesystem artifact content remains outside SQLite ACID;
- [ ] migration failure prevents runtime readiness;
- [ ] deferred Analyst/Custodian state is not introduced.

## Result

**READY FOR PHASE 4 — TRANSACTION MATRIX**