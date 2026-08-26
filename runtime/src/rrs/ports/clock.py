"""Clock boundary for deterministic runtime time access."""

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


__all__ = ["Clock"]
