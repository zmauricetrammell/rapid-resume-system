CREATE INDEX idx_runtime_instances_started_at ON runtime_instances(started_at);
CREATE INDEX idx_runtime_jobs_lifecycle_phase ON runtime_jobs(lifecycle_phase);
CREATE INDEX idx_runtime_jobs_health_status ON runtime_jobs(health_status);
CREATE INDEX idx_runtime_jobs_operation_status ON runtime_jobs(operation_status);
CREATE INDEX idx_runtime_jobs_interaction_status ON runtime_jobs(interaction_status);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX idx_artifacts_operation_key ON artifacts(operation_key);
CREATE INDEX idx_artifacts_execution ON artifacts(committed_by_execution_id);
CREATE INDEX idx_artifacts_runtime_status ON artifacts(runtime_status);
CREATE INDEX idx_routing_decisions_job_time ON routing_decisions(job_id, decided_at);
CREATE INDEX idx_executions_job ON executions(job_id);
CREATE INDEX idx_executions_operation_key ON executions(operation_key);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_owner_status ON executions(owner_runtime_instance_id, status);

CREATE UNIQUE INDEX uq_executions_one_active_per_operation_key
ON executions(operation_key)
WHERE status IN (
    'created','queued','running','output_received','validating','validated','committing'
);

CREATE UNIQUE INDEX uq_events_provider_identity
ON events(source_provider, provider_event_id)
WHERE provider_event_id IS NOT NULL;
CREATE INDEX idx_events_status_created ON events(status, created_at);
CREATE INDEX idx_events_job ON events(job_id);
CREATE INDEX idx_events_owner_lease ON events(owner_runtime_instance_id, lease_expires_at);

CREATE UNIQUE INDEX uq_commands_dedupe_key
ON commands(dedupe_key) WHERE dedupe_key IS NOT NULL;
CREATE INDEX idx_commands_status_created ON commands(status, created_at);
CREATE INDEX idx_commands_job ON commands(job_id);
CREATE INDEX idx_commands_owner_lease ON commands(owner_runtime_instance_id, lease_expires_at);

CREATE INDEX idx_interactions_job_status ON interactions(job_id, status);
CREATE INDEX idx_interactions_provider ON interactions(provider);
CREATE UNIQUE INDEX uq_interactions_one_active_per_job
ON interactions(job_id) WHERE status IN ('pending','active','paused');

CREATE UNIQUE INDEX uq_interaction_messages_provider_id
ON interaction_messages(provider, provider_message_id)
WHERE provider_message_id IS NOT NULL;
CREATE INDEX idx_interaction_messages_unprocessed
ON interaction_messages(interaction_id, processed_at, provider_created_at, provider_message_id);

CREATE INDEX idx_failures_job_resolved ON failures(job_id, resolved_at);
CREATE INDEX idx_failures_execution ON failures(execution_id);
CREATE INDEX idx_failures_event ON failures(event_id);
CREATE INDEX idx_failures_command ON failures(command_id);
CREATE INDEX idx_failures_interaction ON failures(interaction_id);
