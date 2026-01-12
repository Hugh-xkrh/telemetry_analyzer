# src/detectors/rpm_idle_instability.py

from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from typing import Deque, Optional, List, Tuple
import math

from ..events import Event  # adjust if your Event path differs


@dataclass(frozen=True)
class rpm_unstable_event(Event):
    timestamp: float
    mean_rpm: float
    std_rpm: float
    peak_to_peak: float
    window_s: float
    message: str = "Idle RPM instability detected"


@dataclass
class rpm_instaility_config:
    # Gating: define "idling"
    max_speed_kph: float = 2.0
    max_throttle_pct: float = 5.0
    min_rpm_running: float = 500.0
    min_coolant_temp_c: Optional[float] = 60.0  # set None to disable warm gate

    # Rolling window + thresholds
    window_s: float = 8.0
    min_samples: int = 10

    std_threshold_rpm: float = 60.0          # tune
    peak_to_peak_threshold_rpm: float = 180.0  # tune

    # Debounce / anti-spam
    min_unstable_duration_s: float = 3.0
    stable_reset_std_rpm: float = 40.0        # hysteresis
    stable_reset_p2p_rpm: float = 120.0       # hysteresis


class detect_rpm_instability:
    """
    Detects unstable idle RPM (hunting / shaking) while vehicle is idling.
    Keeps a time-based rolling window of RPM samples, checks variance / p2p,
    and emits an event once the condition persists long enough.
    """

    def __init__(self, cfg: rpm_instaility_config | None = None):
        self.cfg = cfg or rpm_instaility_config()
        self._rpm_window: Deque[Tuple[float, float]
                                ] = deque()  # (timestamp, rpm)
        self._unstable_since: Optional[float] = None
        self._active: bool = False  # prevents spamming events while unstable

    def reset(self) -> None:
        self._rpm_window.clear()
        self._unstable_since = None
        self._active = False

    def update(self, telemetry) -> List[Event]:
        """
        telemetry must provide:
          - telemetry.timestamp (float seconds)
          - telemetry.rpm (float)
          - telemetry.vehicle_speed_kph (float)
          - telemetry.throttle_pct (float)
          - telemetry.coolant_temp_c (float) optional if cfg.min_coolant_temp_c is not None
        """
        t = float(telemetry.timestamp)
        rpm = float(telemetry.rpm)
        v = float(telemetry.vehicle_speed_kph)
        thr = float(telemetry.throttle_pct)

        # Gate: only evaluate when idling
        if not self._is_idling(rpm=rpm, speed_kph=v, throttle_pct=thr, telemetry=telemetry):
            # Leaving idle: clear window & state
            self.reset()
            return []

        # Add sample and trim window
        self._rpm_window.append((t, rpm))
        self._trim_window(now=t)

        if len(self._rpm_window) < self.cfg.min_samples:
            return []

        mean_rpm, std_rpm, p2p = self._stats()

        unstable_now = (std_rpm >= self.cfg.std_threshold_rpm) or (
            p2p >= self.cfg.peak_to_peak_threshold_rpm)
        stable_now = (std_rpm <= self.cfg.stable_reset_std_rpm) and (
            p2p <= self.cfg.stable_reset_p2p_rpm)

        # Debounce logic
        if unstable_now:
            if self._unstable_since is None:
                self._unstable_since = t

            duration = t - self._unstable_since
            if (duration >= self.cfg.min_unstable_duration_s) and (not self._active):
                self._active = True
                return [
                    rpm_unstable_event(
                        timestamp=t,
                        mean_rpm=mean_rpm,
                        std_rpm=std_rpm,
                        peak_to_peak=p2p,
                        window_s=self.cfg.window_s,
                    )
                ]

        # Reset active only after it becomes stable (hysteresis)
        if self._active and stable_now:
            self._active = False
            self._unstable_since = None

        # If condition is not unstable, clear timer
        if not unstable_now:
            self._unstable_since = None

        return []

    def _is_idling(self, rpm: float, speed_kph: float, throttle_pct: float, telemetry) -> bool:
        if rpm < self.cfg.min_rpm_running:
            return False
        if speed_kph > self.cfg.max_speed_kph:
            return False
        if throttle_pct > self.cfg.max_throttle_pct:
            return False

        if self.cfg.min_coolant_temp_c is not None:
            # If your telemetry doesn’t have coolant temp, set min_coolant_temp_c=None in config
            temp = float(getattr(telemetry, "coolant_temp_c"))
            if temp < self.cfg.min_coolant_temp_c:
                return False

        return True

    def _trim_window(self, now: float) -> None:
        cutoff = now - self.cfg.window_s
        while self._rpm_window and self._rpm_window[0][0] < cutoff:
            self._rpm_window.popleft()

    def _stats(self) -> Tuple[float, float, float]:
        rpms = [r for _, r in self._rpm_window]
        n = len(rpms)
        mean = sum(rpms) / n
        var = sum((r - mean) ** 2 for r in rpms) / n
        std = math.sqrt(var)
        p2p = max(rpms) - min(rpms)
        return mean, std, p2p
