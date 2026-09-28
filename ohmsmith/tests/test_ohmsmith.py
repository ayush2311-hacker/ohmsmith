import math

import pytest

from ohmsmith import (base_values, find_combos, find_divider, find_rc_filter,
                      fmt_si, parse_si, values_in_range)
from ohmsmith.cli import main


def test_series_sizes_and_known_values():
    assert len(base_values("E12")) == 12
    assert len(base_values("E24")) == 24
    assert len(base_values("E48")) == 48
    e96 = base_values("E96")
    assert len(e96) == 96
    for v in (1.00, 1.02, 2.74, 4.02, 6.81, 9.76):
        assert v in e96


def test_values_in_range_sorted_and_bounded():
    v = values_in_range("E12", 100, 1000)
    assert v[0] == 100 and v[-1] == 1000 and 820 in v
    assert v == sorted(v)


def test_single_exact():
    best = find_combos(4700, "E24", max_parts=1, top=1)[0]
    assert best.value == 4700 and best.error_pct == 0


def test_parallel_exact():
    best = find_combos(5000, "E12", max_parts=2, top=1)[0]
    assert abs(best.error_pct) < 1e-9


def test_three_parts_never_worse_than_two():
    t = 3141.59
    two = find_combos(t, "E24", 2, top=1)[0]
    three = find_combos(t, "E24", 3, top=1)[0]
    assert abs(three.error_pct) <= abs(two.error_pct) + 1e-12


def test_combo_value_matches_topology():
    for c in find_combos(1234.5, "E12", 3, top=20):
        p = c.parts
        expected = {
            "single": p[0],
            "series": sum(p),
            "parallel": 1 / sum(1 / x for x in p),
            "series_parallel": p[0] + p[1] * p[2] / (p[1] + p[2]),
            "parallel_series": 1 / (1 / p[0] + 1 / (p[1] + p[2])),
        }[c.topology]
        assert math.isclose(c.value, expected, rel_tol=1e-9)


def test_divider():
    best = find_divider(5, 3.3, "E24", top=1)[0]
    assert abs(best.error_pct) < 1.0
    assert math.isclose(best.vout, 5 * best.r2 / (best.r1 + best.r2))


def test_rc_filter():
    best = find_rc_filter(1000, top=1)[0]
    assert abs(best.error_pct) < 1.0
    assert math.isclose(best.fc_actual, 1 / (2 * math.pi * best.r * best.c))


@pytest.mark.parametrize("text,val", [
    ("4.7k", 4700), ("4k7", 4700), ("220R", 220), ("100nF", 1e-7),
    ("1kHz", 1000), ("2M2", 2.2e6), ("1e3", 1000), ("10", 10),
])
def test_parse_si(text, val):
    assert math.isclose(parse_si(text), val, rel_tol=1e-12)


def test_parse_si_rejects_garbage():
    with pytest.raises(ValueError):
        parse_si("abc")


def test_fmt_si():
    assert fmt_si(4700) == "4.7k"
    assert fmt_si(1e-7, "F") == "100nF"


def test_cli_smoke(capsys):
    assert main(["combo", "3.14k", "-n", "3"]) == 0
    assert main(["divider", "5", "3.3"]) == 0
    assert main(["rc", "1kHz"]) == 0
    assert main(["series", "E12"]) == 0
    assert main(["divider", "3", "5"]) == 2
    assert "ohm" in capsys.readouterr().out


def test_small_values_keep_precision():
    caps = values_in_range("E12", 1e-9, 9.9e-9)
    assert len(caps) == 12
    assert 8.2e-9 in caps and 8e-9 not in caps
