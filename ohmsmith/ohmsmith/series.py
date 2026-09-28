"""IEC 60063 preferred-number (E-series) generation."""

from __future__ import annotations

import math
from functools import lru_cache
from typing import List

# Low-precision series use hand-picked standard values (not a pure formula).
_TABLE = {
    "E3": [1.0, 2.2, 4.7],
    "E6": [1.0, 1.5, 2.2, 3.3, 4.7, 6.8],
    "E12": [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2],
    "E24": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
            3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1],
}
# High-precision series are 10**(k/n) rounded to three significant figures.
_FORMULA = {"E48": 48, "E96": 96}

SERIES_NAMES = tuple(list(_TABLE) + list(_FORMULA))


@lru_cache(maxsize=None)
def base_values(name: str) -> List[float]:
    """Return one decade (1.00 .. 9.xx) of the named E-series."""
    key = name.upper()
    if key in _TABLE:
        return list(_TABLE[key])
    if key in _FORMULA:
        n = _FORMULA[key]
        return [round(10 ** (k / n), 2) for k in range(n)]
    raise ValueError(f"unknown series {name!r}; choose from {', '.join(SERIES_NAMES)}")


@lru_cache(maxsize=None)
def _values_in_range(name: str, lo: float, hi: float) -> tuple:
    base = base_values(name)
    first = math.floor(math.log10(lo)) - 1
    last = math.ceil(math.log10(hi)) + 1
    out = []
    for d in range(first, last + 1):
        for b in base:
            v = float(f"{b * 10.0 ** d:.6g}")
            if lo <= v <= hi:
                out.append(v)
    return tuple(sorted(set(out)))


def values_in_range(name: str, lo: float, hi: float) -> List[float]:
    """All values of a series across decades that fall within [lo, hi]."""
    if lo <= 0 or hi < lo:
        raise ValueError("need 0 < lo <= hi")
    return list(_values_in_range(name.upper(), float(lo), float(hi)))
