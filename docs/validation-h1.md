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

**The pre-registered comparison supports H1:** the layover/shadow group has a lower median coherence
(0.557 vs 0.738) and a much higher fraction of invalid components (20.2 % vs 2.5 %).

## Slope-matched check (added 2026-11-15)

The headline groups have very different slopes, and steep ground decorrelates for reasons that have
nothing to do with layover. So the valid pixels were reweighted, in 5° slope bins, to the slope
distribution of the layover/shadow group (every layover/shadow pixel has valid pixels in its bin).
This check was added after the first result; the verdict above stays the pre-registered one, and this
is reported next to it.

| Group | Median coherence | Fraction with component 0 |
| --- | ---: | ---: |
| Layover or shadow | 0.557 | 20.2 % |
| Geometrically valid, reweighted to the same slopes | 0.510 | 20.6 % |

**Once slope is matched, H1 is not supported.** Bin by bin (7 bins with at least 100 pixels in both
groups, 30° to 65°), layover/shadow has the lower median coherence in only 3 bins and the higher
component-0 fraction in 4.

| Slope | Layover/shadow pixels | Valid pixels | Median coherence (L/S vs valid) | Component 0 (L/S vs valid) |
| --- | ---: | ---: | --- | --- |
| 30–35° | 303 | 320,124 | 0.557 vs 0.656 | 13.5 % vs 12.7 % |
| 35–40° | 18,093 | 205,561 | 0.586 vs 0.582 | 17.3 % vs 16.6 % |
| 40–45° | 20,227 | 82,335 | 0.559 vs 0.504 | 20.6 % vs 20.9 % |
| 45–50° | 9,541 | 25,910 | 0.545 vs 0.443 | 21.5 % vs 25.1 % |
| 50–55° | 4,126 | 7,520 | 0.521 vs 0.420 | 21.1 % vs 25.6 % |
| 55–60° | 1,737 | 1,648 | 0.441 vs 0.460 | 29.4 % vs 22.0 % |
| 60–65° | 472 | 281 | 0.354 vs 0.458 | 40.7 % vs 26.3 % |

Reading: on slopes up to 55°, layover/shadow pixels are about as coherent as valid ones, or more.
Only above 55° do they look worse, and those bins hold few pixels. In this scene the layover flag adds
little information about coherence beyond the slope itself. This does not make the flag wrong (H2
confirms the geometry); it means low coherence there is better explained by steepness.

## What this does not show

- **The difference is a steep-slope effect.** See the slope-matched check below: at equal slope,
  layover/shadow pixels are not worse than valid ones.
- One scene and one 12-day pair, PROVISIONAL processing (P05023).
- The layover/shadow model is first-order and per pixel; passive layover and cast shadow are not modelled.
- The shadow group is tiny (780 pixels); its numbers are fragile.
- Descriptive comparison only; no significance test.
- Connected component 0 is treated as invalid. The file does not define it; SNAPHU and NISAR's ISCE3 configuration do (see `docs/method.md`).
