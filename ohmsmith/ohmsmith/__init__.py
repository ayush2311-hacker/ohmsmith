"""Ohmsmith: standard-value (E-series) resistor network and filter synthesis."""

from .series import SERIES_NAMES, base_values, values_in_range
from .solver import Combo, find_combos
from .divider import Divider, find_divider
from .rc import RCFilter, find_rc_filter
from .units import parse_si, fmt_si

__version__ = "0.1.0"

__all__ = [
    "SERIES_NAMES", "base_values", "values_in_range",
    "Combo", "find_combos",
    "Divider", "find_divider",
    "RCFilter", "find_rc_filter",
    "parse_si", "fmt_si",
]
