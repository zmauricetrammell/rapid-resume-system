"""Immutable routing history values for the RRS runtime."""

from dataclasses import dataclass
from datetime import datetime

from rrs.domain.artifacts import ArtifactRef
from rrs.domain.enums import LifecyclePhase
from rrs.domain.ids import ExecutionId, RoutingDecisionId


@dataclass(frozen=True)
class RoutingPredicateResult:
    """Result of one deterministic routing predicate evaluation."""

    name: str
    result: bool

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("routing predicate name must be nonempty")


@dataclass(frozen=True)
class RoutingDecision:
    """Append-only record of one authoritative routing decision."""

    decision_id: RoutingDecisionId
    decided_at: datetime
    from_phase: LifecyclePhase
    to_phase: LifecyclePhase
    predicate: RoutingPredicateResult
    basis: tuple[ArtifactRef, ...]
    reason: str
    execution_id: ExecutionId | None

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("routing decision_id must be nonempty")
        if self.decided_at.tzinfo is None:
            raise ValueError("routing decided_at must be timezone-aware")
        if not self.reason:
            raise ValueError("routing reason must be nonempty")


__all__ = ["RoutingDecision", "RoutingPredicateResult"]
