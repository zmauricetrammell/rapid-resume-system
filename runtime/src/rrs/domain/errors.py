"""Normalized runtime exceptions."""

class RRSRuntimeError(Exception):
    """Base exception for normalized runtime failures."""


class PersistenceFailure(RRSRuntimeError):
    """Raised when the persistence layer cannot complete an operation."""


class ConcurrencyConflict(PersistenceFailure):
    """Raised when optimistic compare-and-swap detects stale state."""


__all__ = [
    "ConcurrencyConflict",
    "PersistenceFailure",
    "RRSRuntimeError",
]
