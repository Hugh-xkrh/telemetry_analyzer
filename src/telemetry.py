from pathlib import Path
from typing import List
import csv
from dataclasses import dataclass


@dataclass(frozen=True)  # make evevrything immutable
class TelemetryRow:
    time_s: float
    speed_kmh: float
    rpm: int
    coolant_c: float
    throttle_pct: float


def _to_float(value: str, field: str, row: int) -> float:
    try:
        return float(value)
    except ValueError as e:
        raise ValueError(
            f"Row {row}: invalid float for {field}: {value!r}") from e


def _to_int(value: str, field: str, row: int) -> int:
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(
            f"Row {row}: invalid int for {field}: {value!r}") from e


def load_telemetry(path: Path) -> List[TelemetryRow]:
    rows: List[TelemetryRow] = []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, r in enumerate(reader, start=1):
            rows.append(
                TelemetryRow(
                    time_s=_to_float(r["time_s"], "time_s", i),
                    speed_kmh=_to_float(r["speed_kmh"], "speed_kmh", i),
                    rpm=_to_int(r["rpm"], "rpm", i),
                    coolant_c=_to_float(r["coolant_c"], "coolant_c", i),
                    throttle_pct=_to_float(
                        r["throttle_pct"], "throttle_pct", i),
                )
            )

    return rows
