"""Canonical persisted enum vocabulary for the RRS runtime."""

from enum import StrEnum


class LifecyclePhase(StrEnum):
    NEW = "new"
    ANALYSIS = "analysis"
    EVIDENCE_REQUEST = "evidence_request"
    INVESTIGATION = "investigation"
    EVIDENCE_INTEGRATION = "evidence_integration"
    RESUME_PRODUCTION = "resume_production"
    EVALUATION = "evaluation"
    COMPLETE = "complete"
    MANUAL_REVIEW = "manual_review"
    CANCELLED = "cancelled"


class OperationType(StrEnum):
    GENERATE_ANALYSIS = "generate_analysis"
    REQUEST_EVIDENCE = "request_evidence"
    INVESTIGATE_EVIDENCE_REQUEST = "investigate_evidence_request"
    INTEGRATE_EVIDENCE = "integrate_evidence"
    GENERATE_RESUME = "generate_resume"
    EVALUATE_RESUME = "evaluate_resume"


class RuntimeOperationStatus(StrEnum):
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    VALIDATING = "validating"
    COMMITTING = "committing"


class ExecutionStatus(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    OUTPUT_RECEIVED = "output_received"
    VALIDATING = "validating"
    VALIDATED = "validated"
    STALE = "stale"
    COMMITTING = "committing"
    COMMITTED = "committed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InteractionProjectionStatus(StrEnum):
    NONE = "none"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class InteractionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InteractionType(StrEnum):
    EVIDENCE_INVESTIGATION = "evidence_investigation"
    MANUAL_REVIEW = "manual_review"


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RECOVERABLE_FAILURE = "recoverable_failure"
    BLOCKED = "blocked"


class MutationType(StrEnum):
    SET = "set"
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
    UPSERT_VERSION = "upsert_version"


class RetrievalRequirement(StrEnum):
    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"


class ArtifactRuntimeStatus(StrEnum):
    COMMITTED = "committed"
    STALE_OUTPUT = "stale_output"
    ORPHANED_OUTPUT = "orphaned_output"
    DIAGNOSTIC = "diagnostic"


class EventStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    IGNORED = "ignored"
    RETRY_PENDING = "retry_pending"
    DEAD_LETTER = "dead_letter"


class EventCriticality(StrEnum):
    WORKFLOW_CRITICAL = "workflow_critical"
    INTEGRATION_ONLY = "integration_only"


class CommandStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    RETRY_PENDING = "retry_pending"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FailureClass(StrEnum):
    EVIDENCE_SOURCE_UNAVAILABLE = "evidence_source_unavailable"
    INVOCATION_FAILURE = "invocation_failure"
    SCHEMA_VALIDATION_FAILURE = "schema_validation_failure"
    STALE_OUTPUT = "stale_output"
    PERSISTENCE_FAILURE = "persistence_failure"
    STORAGE_CONFLICT = "storage_conflict"
    CONCURRENCY_CONFLICT = "concurrency_conflict"
    INTERACTION_FAILURE = "interaction_failure"
    PROVIDER_RECONCILIATION_FAILURE = "provider_reconciliation_failure"
    RUNTIME_INTEGRITY_FAILURE = "runtime_integrity_failure"


class ArtifactType(StrEnum):
    TARGET_JOB = "target_job"
    JOB_EXPERIENCE_RECORD = "job_experience_record"
    JOB_EXPERIENCE_ANALYSIS = "job_experience_analysis"
    EVIDENCE_REQUEST = "evidence_request"
    EVIDENCE_RESPONSE = "evidence_response"
    TARGETED_RESUME = "targeted_resume"
    WRITER_CONTENT_MANIFEST = "writer_content_manifest"
    RESUME_EVALUATION = "resume_evaluation"
    PROCESS_FEEDBACK = "process_feedback"


__all__ = [
    "ArtifactRuntimeStatus", "ArtifactType", "CommandStatus", "EventCriticality",
    "EventStatus", "ExecutionStatus", "FailureClass", "HealthStatus",
    "InteractionProjectionStatus", "InteractionStatus", "InteractionType",
    "LifecyclePhase", "MutationType", "OperationType", "RetrievalRequirement",
    "RuntimeOperationStatus",
]
