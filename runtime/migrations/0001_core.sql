CREATE TABLE runtime_instances (
    runtime_instance_id TEXT PRIMARY KEY,
    git_sha TEXT NOT NULL,
    image_digest TEXT,
    operation_registry_hash TEXT NOT NULL,
    built_at TEXT,
    started_at TEXT NOT NULL,
    stopped_at TEXT
);

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

CREATE TABLE job_artifact_pointers (
    job_id TEXT NOT NULL,
    pointer_type TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,
    PRIMARY KEY (job_id, pointer_type),
    FOREIGN KEY (job_id) REFERENCES runtime_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (artifact_id, artifact_version)
        REFERENCES artifacts(artifact_id, artifact_version)
);

CREATE TABLE job_artifact_collection_members (
    job_id TEXT NOT NULL,
    collection_type TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,
    PRIMARY KEY (job_id, collection_type, artifact_id),
    FOREIGN KEY (job_id) REFERENCES runtime_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (artifact_id, artifact_version)
        REFERENCES artifacts(artifact_id, artifact_version)
);

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
    FOREIGN KEY (job_id) REFERENCES runtime_jobs(job_id) ON DELETE CASCADE
);

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
    FOREIGN KEY (job_id) REFERENCES runtime_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (owner_runtime_instance_id)
        REFERENCES runtime_instances(runtime_instance_id),
    UNIQUE (operation_key, attempt_number)
);

CREATE TABLE artifact_commit_groups (
    commit_group_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    committed_at TEXT,
    FOREIGN KEY (execution_id) REFERENCES executions(execution_id) ON DELETE CASCADE
);

CREATE TABLE artifact_commit_group_members (
    commit_group_id TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    artifact_version INTEGER NOT NULL,
    PRIMARY KEY (commit_group_id, artifact_id, artifact_version),
    FOREIGN KEY (commit_group_id)
        REFERENCES artifact_commit_groups(commit_group_id) ON DELETE CASCADE,
    FOREIGN KEY (artifact_id, artifact_version)
        REFERENCES artifacts(artifact_id, artifact_version)
);

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
    FOREIGN KEY (job_id) REFERENCES runtime_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (owner_runtime_instance_id)
        REFERENCES runtime_instances(runtime_instance_id)
);

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
    FOREIGN KEY (job_id) REFERENCES runtime_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (causation_event_id) REFERENCES events(event_id),
    FOREIGN KEY (owner_runtime_instance_id)
        REFERENCES runtime_instances(runtime_instance_id)
);

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
    FOREIGN KEY (job_id) REFERENCES runtime_jobs(job_id) ON DELETE CASCADE
);

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
        REFERENCES interactions(interaction_id) ON DELETE CASCADE
);

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
    FOREIGN KEY (job_id) REFERENCES runtime_jobs(job_id) ON DELETE CASCADE
);
