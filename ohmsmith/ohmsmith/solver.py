"""Find the best series/parallel combination of standard resistors for a target."""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from .series import values_in_range
from .units import fmt_si


@dataclass(frozen=True)
class Combo:
    """One candidate network and how close it lands to the target."""

    topology: str            # single | series | parallel | series_parallel | parallel_series
    parts: Tuple[float, ...]
    value: float
    error_pct: float

    @property
    def n_parts(self) -> int:
        return len(self.parts)

    def describe(self) -> str:
        p = [fmt_si(x) for x in self.parts]
        if self.topology == "single":
            return p[0]
        if self.topology == "series":
            return " + ".join(p)
        if self.topology == "parallel":
            return " || ".join(p)
        if self.topology == "series_parallel":      # c + (a || b)
            return f"{p[0]} + ({p[1]} || {p[2]})"
        return f"{p[0]} || ({p[1]} + {p[2]})"       # c || (a + b)


def _neighbours(sorted_vals: Sequence[float], x: float) -> range:
    """Indices of the values just below and just above x."""
    i = bisect_left(sorted_vals, x)
    return range(max(0, i - 1), min(len(sorted_vals), i + 1))


def _pair_table(vals: Sequence[float], kind: str):
    rows = []
    for i, a in enumerate(vals):
        for b in vals[i:]:
            v = a + b if kind == "series" else a * b / (a + b)
            rows.append((v, a, b))
    rows.sort()
    return rows, [r[0] for r in rows]


def find_combos(target: float, series: str = "E24", max_parts: int = 2,
                lo: float = 1.0, hi: float = 10e6, top: int = 5) -> List[Combo]:
    """Return the `top` best networks (up to `max_parts` resistors) for `target` ohms."""
    if target <= 0:
        raise ValueError("target must be positive")
    if not 1 <= max_parts <= 3:
        raise ValueError("max_parts must be 1, 2 or 3")
    vals = values_in_range(series, lo, hi)
    found: Dict[tuple, Combo] = {}

    def add(topology: str, parts: Tuple[float, ...], value: float) -> None:
        err = (value - target) / target * 100.0
        key = (topology,) + (tuple(sorted(parts)) if topology in ("series", "parallel") else parts)
        if key not in found:
            found[key] = Combo(topology, parts, value, err)

    for i in _neighbours(vals, target):
        add("single", (vals[i],), vals[i])

    if max_parts >= 2:
        for a in vals:
            need = target - a                          # series partner
            if need > 0:
                for j in _neighbours(vals, need):
                    b = vals[j]
                    add("series", (a, b), a + b)
            if a > target:                             # parallel partner
                need = a * target / (a - target)
                for j in _neighbours(vals, need):
                    b = vals[j]
                    add("parallel", (a, b), a * b / (a + b))

    if max_parts == 3:
        par_rows, par_keys = _pair_table(vals, "parallel")
        ser_rows, ser_keys = _pair_table(vals, "series")
        for c in vals:
            need = target - c                          # c + (a || b)
            if need > 0:
                for j in _neighbours(par_keys, need):
                    _, a, b = par_rows[j]
                    add("series_parallel", (c, a, b), c + a * b / (a + b))
            if c > target:                             # c || (a + b)
                need = c * target / (c - target)
                for j in _neighbours(ser_keys, need):
                    _, a, b = ser_rows[j]
                    s = a + b
                    add("parallel_series", (c, a, b), c * s / (c + s))

    ranked = sorted(found.values(),
                    key=lambda c: (round(abs(c.error_pct), 9), c.n_parts, c.parts))
    return ranked[:top]
