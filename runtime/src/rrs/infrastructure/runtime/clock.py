"""Production and deterministic clock implementations."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("FakeClock current time must be timezone-aware")


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass
class FakeClock:
    current: datetime

    def __post_init__(self) -> None:
        _require_aware(self.current)

    def now(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        if delta < timedelta(0):
            raise ValueError("FakeClock cannot move backwards")
        self.current += delta


__all__ = ["FakeClock", "SystemClock"]
