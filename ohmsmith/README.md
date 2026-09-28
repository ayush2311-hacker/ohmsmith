# Ohmsmith

![tests](https://github.com/ayush2311-hacker/ohmsmith/actions/workflows/tests.yml/badge.svg)

**Find the best standard-value resistor networks, voltage dividers and RC filters, from the command line or as a Python library.**

You almost never have the exact resistor you calculated. Ohmsmith searches the real
IEC 60063 preferred-value series (E3 to E96) and returns the combinations that land closest
to your target, including two- and three-resistor series/parallel networks. Zero dependencies.

## Install

```bash
git clone https://github.com/YOUR-USERNAME/ohmsmith.git
cd ohmsmith
pip install -e .
```

## Usage

### Hit an odd resistance with standard parts
```
$ ohmsmith combo 3.14k -n 3
network                                  value     error
390 + (3k || 33k)                     3.14kohm   +0.000%
62k || (7.5 + 3.3k)                   3.14kohm   -0.000%
4.3 + (3.9k || 16k)                   3.14kohm   -0.001%
```
`-n` sets the maximum resistors (1-3), `-s E96` picks the series. Notation like `4.7k`, `4k7`, `220R`, `2M2` works.

### Voltage divider (5 V to 3.3 V)
```
$ ohmsmith divider 5 3.3
      R1      R2      Vout     error    current
    470k    910k   3.2971V   -0.088%    3.623uA
     47k     91k   3.2971V   -0.088%    36.23uA
    4.7k    9.1k   3.2971V   -0.088%    362.3uA
```
Equal-error ties are listed high-resistance first, so you can pick the current draw you can afford.

### RC filter for a cutoff frequency
```
$ ohmsmith rc 440Hz --r-series E96 --top 3
       R        C    fc actual     error
    301k    1.2nF      440.6Hz   +0.143%
   30.1k     12nF      440.6Hz   +0.143%
   3.01k    120nF      440.6Hz   +0.143%
```

### As a library
```python
from ohmsmith import find_combos, find_divider, parse_si

best = find_combos(parse_si("3.14k"), series="E24", max_parts=3, top=1)[0]
print(best.describe(), best.value, best.error_pct)
```

## The math

| Problem | Relation | How it is searched |
|---|---|---|
| Series / parallel | `R = Ra + Rb`, `R = RaRb / (Ra + Rb)` | For each `Ra`, solve for the ideal `Rb` and check its two neighbouring standard values (binary search) |
| 3-part networks | `Rc + (Ra ‖ Rb)`, `Rc ‖ (Ra + Rb)` | Pre-sorted tables of all pair values; solve for the ideal pair value for each `Rc` |
| Divider | `Vout = Vin·R2 / (R1 + R2)` so `R2 = R1·Vout / (Vin − Vout)` | Same neighbour search per `R1` |
| RC filter | `fc = 1 / (2πRC)` so `R = 1 / (2πfcC)` | Same neighbour search per standard `C` |

Because the ideal partner is computed directly instead of brute-forcing every pair,
even E96 three-part searches finish in a fraction of a second.

E3-E24 use the hand-picked standard values; E48/E96 are `10^(k/n)` rounded to three
significant figures.

## Tests
```bash
pip install -e ".[dev]"
pytest
```

## License
MIT
