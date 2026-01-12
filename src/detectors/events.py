from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    kind: str
    start_s: float
    end_s: float
    details: str
