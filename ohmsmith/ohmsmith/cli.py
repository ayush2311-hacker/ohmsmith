"""Command-line interface: `ohmsmith combo|divider|rc|series`."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .divider import find_divider
from .rc import find_rc_filter
from .series import SERIES_NAMES, values_in_range
from .solver import find_combos
from .units import fmt_si, parse_si


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ohmsmith",
                                description="Standard-value resistor & filter synthesis.")
    p.add_argument("--version", action="version", version=f"ohmsmith {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("combo", help="best resistor network for a target resistance")
    c.add_argument("target", help="target resistance, e.g. 3.14k")
    c.add_argument("-s", "--series", default="E24", choices=SERIES_NAMES)
    c.add_argument("-n", "--max-parts", type=int, default=2, choices=(1, 2, 3))
    c.add_argument("--top", type=int, default=5)

    d = sub.add_parser("divider", help="voltage divider from standard values")
    d.add_argument("vin")
    d.add_argument("vout")
    d.add_argument("-s", "--series", default="E24", choices=SERIES_NAMES)
    d.add_argument("--top", type=int, default=5)

    r = sub.add_parser("rc", help="first-order RC filter for a cutoff frequency")
    r.add_argument("fc", help="cutoff frequency, e.g. 1kHz")
    r.add_argument("--r-series", default="E24", choices=SERIES_NAMES)
    r.add_argument("--c-series", default="E12", choices=SERIES_NAMES)
    r.add_argument("--top", type=int, default=5)

    s = sub.add_parser("series", help="list the values of a series in a range")
    s.add_argument("name", choices=SERIES_NAMES)
    s.add_argument("--lo", default="1")
    s.add_argument("--hi", default="10")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.cmd == "combo":
            target = parse_si(args.target)
            print(f"Target {fmt_si(target)}ohm using {args.series}, up to {args.max_parts} part(s)\n")
            print(f"{'network':<34}{'value':>12}{'error':>10}")
            for x in find_combos(target, args.series, args.max_parts, top=args.top):
                print(f"{x.describe():<34}{fmt_si(x.value, 'ohm'):>12}{x.error_pct:>+9.3f}%")
        elif args.cmd == "divider":
            vin, vout = parse_si(args.vin), parse_si(args.vout)
            print(f"Vin {fmt_si(vin)}V -> Vout {fmt_si(vout)}V using {args.series}\n")
            print(f"{'R1':>8}{'R2':>8}{'Vout':>10}{'error':>10}{'current':>11}")
            for x in find_divider(vin, vout, args.series, top=args.top):
                print(f"{fmt_si(x.r1):>8}{fmt_si(x.r2):>8}{x.vout:>9.4f}V"
                      f"{x.error_pct:>+9.3f}%{fmt_si(x.current_a, 'A'):>11}")
        elif args.cmd == "rc":
            fc = parse_si(args.fc)
            print(f"Cutoff {fmt_si(fc)}Hz, fc = 1 / (2*pi*R*C)\n")
            print(f"{'R':>8}{'C':>9}{'fc actual':>13}{'error':>10}")
            for x in find_rc_filter(fc, args.r_series, args.c_series, top=args.top):
                print(f"{fmt_si(x.r):>8}{fmt_si(x.c, 'F'):>9}{fmt_si(x.fc_actual, 'Hz'):>13}"
                      f"{x.error_pct:>+9.3f}%")
        else:
            lo, hi = parse_si(args.lo), parse_si(args.hi)
            print("  ".join(fmt_si(v) for v in values_in_range(args.name, lo, hi)))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
