"""Resistive voltage-divider synthesis from standard values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .series import values_in_range
from .solver import _neighbours


@dataclass(frozen=True)
class Divider:
    """Vin --[r1]--+--[r2]-- GND, with Vout taken at the middle node."""

    r1: float
    r2: float
    vin: float
    vout: float
    error_pct: float

    @property
    def current_a(self) -> float:
        return self.vin / (self.r1 + self.r2)

    @property
    def power_w(self) -> float:
        return self.vin ** 2 / (self.r1 + self.r2)


def find_divider(vin: float, vout: float, series: str = "E24",
                 lo: float = 100.0, hi: float = 1e6, top: int = 5) -> List[Divider]:
    """Best R1/R2 pairs so that vin * r2 / (r1 + r2) ~= vout.

    Derivation: vout = vin * r2 / (r1 + r2)  =>  r2 = r1 * vout / (vin - vout).
    For every standard r1 the ideal r2 is computed and the neighbouring standard
    values are evaluated exactly. Ties in error prefer the higher total resistance
    (lower current draw).
    """
    if not 0 < vout < vin:
        raise ValueError("need 0 < vout < vin")
    vals = values_in_range(series, lo, hi)
    seen = {}
    for r1 in vals:
        ideal_r2 = r1 * vout / (vin - vout)
        for j in _neighbours(vals, ideal_r2):
            r2 = vals[j]
            actual = vin * r2 / (r1 + r2)
            seen[(r1, r2)] = Divider(r1, r2, vin, actual, (actual - vout) / vout * 100.0)
    ranked = sorted(seen.values(),
                    key=lambda d: (round(abs(d.error_pct), 9), -(d.r1 + d.r2)))
    return ranked[:top]
