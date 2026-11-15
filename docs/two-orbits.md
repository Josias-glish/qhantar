# Two orbits: ascending and descending over La Paz

One line of sight measures one projection. To see how much the answer depends on the orbit, the same
engine, thresholds and DEM were run on a second real NISAR GUNW: the **descending** pass.

| | Ascending (primary) | Descending |
| --- | --- | --- |
| Granule | `NISAR_L2_PR_GUNW_032_118_A_169_…_P05023_N_F_J_001` | `NISAR_L2_PR_GUNW_031_097_D_097_032_2000_SH_20260924T224522_20260924T224556_20261006T224522_20261006T224556_P05023_N_F_J_001` |
| Track / frame | 118 / 169 | 97 / 97 |
| Dates | 2026-10-08 / 2026-10-20 | 2026-09-24 / 2026-10-06 |
| CRID, maturity | P05023, PROVISIONAL | P05023, PROVISIONAL |
| Sensor side (from the native LOS) | east | west |
| La Paz crop: interpretable | 35.5 % | 39.1 % |
| visible, incoherent | 8.6 % | 6.3 % |
| coherent, low sensitivity | 23.6 % | 22.6 % |
| not observable or invalid | 32.4 % | 32.0 % |

Descending scene, valid pixels: median coherence 0.738, median |S| 0.430.

## Combined (`scripts/two_orbits.py`)

The descending state map is resampled (nearest neighbour) onto the ascending La Paz crop grid; the
420,046 pixels with a state in both orbits are compared.

| Interpretable in | Share |
| --- | --- |
| both orbits | 20.1 % |
| ascending only | 15.4 % |
| descending only | 19.0 % |
| at least one | **54.5 %** |

Reading: a slope that one pass cannot interpret is often interpretable from the other, because the
sensor sits on the opposite side. Together the two passes leave 54.5 % of the crop
interpretable, against 35.5 % and 39.1 % alone.

## Limits

- The pairs are not simultaneous (September to October vs October), so part of the difference is
  coherence over different dates, not geometry alone.
- Two passes still give two projections, not 3-D motion.
- Both products are PROVISIONAL P05023.
- The descending frame needed 16 DEM tiles (the 12 of the ascending scene plus W067 S16 to S19).

Every number here is read from `results/T097_D_F097_20260924_20261006_P05023/results.json` (`two_orbits`, `fractions`, `quality`) and the
ascending `results.json`.
