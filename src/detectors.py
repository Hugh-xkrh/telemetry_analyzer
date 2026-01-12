from __future__ import annotations

from typing import List
from .events import Event
from .telemetry import TelemetryRow


def detect_coolant_overheat(
    samples: List[TelemetryRow],
    threshold_c: float = 130.0,
) -> List[Event]:
    events: List[Event] = []

    in_overheat = False
    start_s = 0.0
    max_temp = float("-inf")

    for t in samples:
        if t.coolant_c >= threshold_c:
            if not in_overheat:
                in_overheat = True
                start_s = t.time_s
                max_temp = t.coolant_c
            else:
                if t.coolant_c > max_temp:
                    max_temp = t.coolant_c
        else:
            if in_overheat:
                # window ended
                events.append(
                    Event(
                        kind="COOLANT_OVERHEAT",
                        start_s=start_s,
                        end_s=t.time_s,
                        details=f"max_coolant_c={max_temp:.1f}, threshold_c={threshold_c:.1f}",
                    )
                )
                in_overheat = False

    # If overheating continues until the last sample
    if in_overheat and samples:
        events.append(
            Event(
                kind="COOLANT_OVERHEAT",
                start_s=start_s,
                end_s=samples[-1].time_s,
                details=f"max_coolant_c={max_temp:.1f}, threshold_c={threshold_c:.1f}",
            )
        )

    return events
