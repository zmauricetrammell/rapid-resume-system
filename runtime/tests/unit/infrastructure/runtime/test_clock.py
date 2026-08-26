from datetime import UTC, datetime, timedelta

import pytest

from rrs.infrastructure.runtime.clock import FakeClock, SystemClock
from rrs.ports.clock import Clock


def accepts_clock(clock: Clock) -> Clock:
    return clock


def test_system_clock_returns_aware_utc_time() -> None:
    clock = accepts_clock(SystemClock())

    current = clock.now()

    assert current.tzinfo is UTC
    assert current.utcoffset() is not None


def test_fake_clock_returns_fixed_time_and_advances_explicitly() -> None:
    initial = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)
    clock = FakeClock(initial)

    assert clock.now() == initial

    clock.advance(timedelta(minutes=15))

    assert clock.now() == initial + timedelta(minutes=15)


def test_fake_clock_rejects_naive_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        FakeClock(datetime(2026, 8, 25, 12, 0))


def test_fake_clock_rejects_negative_advance() -> None:
    clock = FakeClock(datetime(2026, 8, 25, 12, 0, tzinfo=UTC))

    with pytest.raises(ValueError, match="cannot move backwards"):
        clock.advance(timedelta(seconds=-1))
