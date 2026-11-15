# H1 — layover/shadow versus geometrically valid pixels

**Scene:** `NISAR_L2_PR_GUNW_032_118_A_169_033_2000_SH_20261008T102402_20261008T102436_20261020T102402_20261020T102436_P05023_N_F_J_001`
(ascending track 118, frame 169, 2026-10-08 / 2026-10-20, HH, CRID P05023, PROVISIONAL).
Produced by `scripts/h1.py`; the same numbers are stored under `h1` in `results.json`.

## Hypothesis

Pixels that QHANTAR's geometric model flags as layover or shadow show lower median coherence and
a higher fraction of connected component 0 than geometrically valid pixels.

## How the groups were built

Population: radar footprint, not water, both subswaths valid (product mask), DEM and LOS available.
It is split **only** by the model's layover/shadow flags. Coherence and connected components were
not used to build or filter either group. Pixels with missing coherence are reported, not removed
from the component statistic.

## Result

| Group | Pixels | Median coherence | Coherence IQR | Coherence missing | Fraction with component 0 |
| --- | ---: | ---: | --- | ---: | ---: |
| Layover or shadow | 54,612 | 0.557 | 0.319 – 0.747 | 0.03 % | 20.2 % |
| · layover only | 53,832 | 0.563 | 0.328 – 0.750 | 0.03 % | 19.6 % |
| · shadow only | 780 | 0.166 | 0.113 – 0.261 | 0.00 % | 59.5 % |
| Geometrically valid | 8,561,452 | 0.738 | 0.610 – 0.851 | 0.01 % | 2.5 % |
| *Context: valid with slope ≥ 30°* | 643,428 | 0.602 | 0.348 – 0.806 | 0.03 % | 15.7 % |

**In this scene H1 is supported:** the layover/shadow group has a lower median coherence
(0.557 vs 0.738) and a much higher fraction of invalid components (20.2 % vs 2.5 %).

## What this does not show

- **Part of the difference is a steep-slope effect.** Geometrically valid pixels on slopes ≥ 30°
  also have lower coherence (0.602) and more invalid components (15.7 %). Layover/shadow pixels are
  still worse than that steep-slope context group, but the gap is much smaller than in the headline
  comparison. A slope-matched comparison would be the fairer test; it was not run.
- One scene and one 12-day pair, PROVISIONAL processing (P05023).
- The layover/shadow model is first-order and per pixel; passive layover and cast shadow are not modelled.
- The shadow group is tiny (780 pixels); its numbers are fragile.
- Descriptive comparison only; no significance test.
- Connected component 0 is treated as invalid by inference (see `docs/DECISIONS.md`).
