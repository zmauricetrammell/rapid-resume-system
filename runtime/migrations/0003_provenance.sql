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
    FOREIGN KEY (execution_id) REFERENCES executions(execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_invocation_provider_request
ON invocation_provenance(provider, provider_request_id);
