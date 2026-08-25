from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from rrs.domain.artifacts import ArtifactRef, ArtifactVersion
from rrs.domain.enums import ArtifactType, LifecyclePhase
from rrs.domain.ids import ArtifactId, RoutingDecisionId
from rrs.domain.routing import RoutingDecision, RoutingPredicateResult

NOW = datetime(2026, 8, 24, 12, 0, tzinfo=UTC)


def test_routing_predicate_requires_name() -> None:
    with pytest.raises(ValueError, match="name"):
        RoutingPredicateResult(name="", result=True)


def test_routing_decision_preserves_basis() -> None:
    basis = (
        ArtifactRef(
            artifact_type=ArtifactType.JOB_EXPERIENCE_ANALYSIS,
            artifact_id=ArtifactId("jea-1"),
            artifact_version=ArtifactVersion(1),
            uri="file:///data/jea-1/v1",
        ),
    )
    decision = RoutingDecision(
        decision_id=RoutingDecisionId("decision-1"),
        decided_at=NOW,
        from_phase=LifecyclePhase.ANALYSIS,
        to_phase=LifecyclePhase.RESUME_PRODUCTION,
        predicate=RoutingPredicateResult(name="analysis_complete", result=True),
        basis=basis,
        reason="Analysis supports resume production.",
        execution_id=None,
    )

    assert decision.basis == basis


def test_routing_decision_is_immutable() -> None:
    decision = RoutingDecision(
        decision_id=RoutingDecisionId("decision-1"),
        decided_at=NOW,
        from_phase=LifecyclePhase.NEW,
        to_phase=LifecyclePhase.ANALYSIS,
        predicate=RoutingPredicateResult(name="job_created", result=True),
        basis=(),
        reason="New jobs enter analysis.",
        execution_id=None,
    )

    with pytest.raises(FrozenInstanceError):
        decision.reason = "changed"  # type: ignore[misc]

def test_routing_decision_requires_id() -> None:
    with pytest.raises(ValueError, match="decision_id"):
        RoutingDecision(
            decision_id=RoutingDecisionId(""),
            decided_at=NOW,
            from_phase=LifecyclePhase.NEW,
            to_phase=LifecyclePhase.ANALYSIS,
            predicate=RoutingPredicateResult(
                name="job_created",
                result=True,
            ),
            basis=(),
            reason="New jobs enter analysis.",
            execution_id=None,
        )


def test_routing_decision_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        RoutingDecision(
            decision_id=RoutingDecisionId("decision-1"),
            decided_at=datetime(2026, 8, 24, 12, 0),
            from_phase=LifecyclePhase.NEW,
            to_phase=LifecyclePhase.ANALYSIS,
            predicate=RoutingPredicateResult(
                name="job_created",
                result=True,
            ),
            basis=(),
            reason="New jobs enter analysis.",
            execution_id=None,
        )


def test_routing_decision_requires_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        RoutingDecision(
            decision_id=RoutingDecisionId("decision-1"),
            decided_at=NOW,
            from_phase=LifecyclePhase.NEW,
            to_phase=LifecyclePhase.ANALYSIS,
            predicate=RoutingPredicateResult(
                name="job_created",
                result=True,
            ),
            basis=(),
            reason="",
            execution_id=None,
        )