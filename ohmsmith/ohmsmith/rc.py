"""First-order RC filter design from standard resistor and capacitor values."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from .series import values_in_range
from .solver import _neighbours


@dataclass(frozen=True)
class RCFilter:
    r: float
    c: float
    fc_target: float
    fc_actual: float
    error_pct: float


def find_rc_filter(fc: float, r_series: str = "E24", c_series: str = "E12",
                   r_lo: float = 100.0, r_hi: float = 1e6,
                   c_lo: float = 10e-12, c_hi: float = 10e-6,
                   top: int = 5) -> List[RCFilter]:
    """Best (R, C) pairs for a first-order cutoff fc.

    Cutoff: fc = 1 / (2*pi*R*C)  =>  R = 1 / (2*pi*fc*C). Valid for both the
    low-pass and the high-pass form since they share the same -3 dB corner.
    """
    if fc <= 0:
        raise ValueError("fc must be positive")
    r_vals = values_in_range(r_series, r_lo, r_hi)
    c_vals = values_in_range(c_series, c_lo, c_hi)
    out = {}
    for c in c_vals:
        ideal_r = 1.0 / (2 * math.pi * fc * c)
        if not r_lo / 2 <= ideal_r <= r_hi * 2:
            continue
        for j in _neighbours(r_vals, ideal_r):
            r = r_vals[j]
            actual = 1.0 / (2 * math.pi * r * c)
            out[(r, c)] = RCFilter(r, c, fc, actual, (actual - fc) / fc * 100.0)
    ranked = sorted(out.values(), key=lambda f: (round(abs(f.error_pct), 9), f.c))
    return ranked[:top]
