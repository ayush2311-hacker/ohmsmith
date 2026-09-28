"""Parsing and formatting of engineering-notation values (4.7k, 4k7, 100n ...)."""

from __future__ import annotations

import re

_MULT = {
    "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3,
    "R": 1.0, "r": 1.0, "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9,
}
_UNIT_TAIL = re.compile(r"(hz|ohms?|Ω|f|v|a)$", re.IGNORECASE)
_RKM = re.compile(r"(\d+)([RrkKMmunpµG])(\d+)")
_PLAIN = re.compile(r"([0-9]*\.?[0-9]+(?:[eE][-+]?\d+)?)\s*([pnuµmkKMGRr])?")


def parse_si(text: str) -> float:
    """Parse '4.7k', '4k7', '100nF', '1e3', '220R', '1kHz' into a float."""
    s = str(text).strip().replace(" ", "")
    s = _UNIT_TAIL.sub("", s)
    m = _RKM.fullmatch(s)
    if m:
        whole, suffix, frac = m.groups()
        return float(f"{whole}.{frac}") * _MULT[suffix]
    m = _PLAIN.fullmatch(s)
    if not m:
        raise ValueError(f"cannot parse value: {text!r}")
    number, suffix = m.groups()
    return float(number) * (_MULT[suffix] if suffix else 1.0)


def fmt_si(x: float, unit: str = "") -> str:
    """Format a float in engineering notation, e.g. 4700 -> '4.7k'."""
    for scale, suffix in ((1e9, "G"), (1e6, "M"), (1e3, "k"), (1.0, ""),
                          (1e-3, "m"), (1e-6, "u"), (1e-9, "n"), (1e-12, "p")):
        if abs(x) >= scale * 0.99995:
            return f"{x / scale:.4g}{suffix}{unit}"
    return f"{x:.4g}{unit}"
