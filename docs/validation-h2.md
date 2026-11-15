# H2: contrast with an independent R-index

**Scene:** same GUNW as H1 (ascending track 118, frame 169, 2026-10-08 / 2026-10-20, HH, CRID P05023, PROVISIONAL).
Produced by `scripts/h2.py`; the same numbers are stored under `h2` in `results.json`.

## What was compared

The R-index of Notti et al. (2010, 2014), as written in *Remote Sensing* 2021, 13, 1938, eq. (1):

`R = sin{ θ + arctan[ tan α · cos(φ − β) ] }`

α slope, β aspect, θ incidence, φ look azimuth (sensor → target). Regions, as described in that paper:
R < 0 layover; 0 < R < sin θ foreshortening; R ≥ sin θ good visibility. Active shadow cannot be told
apart by the value of R, so it is flagged separately when the argument of the sine exceeds 90°.

The implementation is independent of `qhantar/engine.py`: slope and aspect are recomputed from the
same DEM with Horn's 3×3 method (the engine uses central differences), and no engine code is imported.
Incidence and look azimuth are the product's native ones.

**Criterion, fixed in the script before it was run:** the two models are *consistent* if Cohen's κ ≥ 0.8
for both the layover flag and the active-shadow flag. Population: QHANTAR's valid pixels inside the
footprint (8,614,957).

## Result

| Flag | R-index pixels | QHANTAR pixels | Both | Cohen's κ |
| --- | ---: | ---: | ---: | ---: |
| Layover (R < 0) | 46,160 | 53,818 | 44,027 | 0.880 |
| Active shadow | 600 | 780 | 578 | 0.838 |

**Verdict: consistent.** Both κ values pass the 0.8 criterion.

**Control.** The same R-index computed on QHANTAR's own slope and aspect gives κ = 1.000 for both
flags. The disagreement in the table therefore comes only from the DEM-derivative method: Horn's
3×3 kernel smooths the terrain slightly more and flags fewer steep fore-slopes. It does not come
from a sign, azimuth or convention error.

### Where the two indices say different things

Share of R-index classes inside each QHANTAR state (valid pixels):

| QHANTAR state | Layover | Active shadow | Foreshortening | Good visibility |
| --- | ---: | ---: | ---: | ---: |
| 1 Interpretable | 0.0 % | 0.0 % | 39.3 % | 60.7 % |
| 2 Visible, incoherent | 0.0 % | 0.0 % | 10.6 % | 89.4 % |
| 3 Coherent, low sensitivity | 0.1 % | 0.0 % | 78.5 % | 21.5 % |
| 0 Not observable or invalid | 1.5 % | 0.0 % | 53.3 % | 45.3 % |

- Spearman correlation between R and |S| on pixels with valid geometry: 0.554.
- 17.9 % of the pixels the R-index rates as *good visibility* have |S| < 0.3. The radar images those
  slopes well, but a downhill motion would barely project on the line of sight.

This is the useful part of H2. The R-index answers *how well is this slope imaged*; |S| answers
*how much of a downhill motion would the interferogram see*. They agree on where the image is
geometrically broken, and they disagree on purpose elsewhere.

## What this does not show

- The R-index layover condition and QHANTAR's range-plane condition are the same first-order geometry.
  Agreement tests the implementation and the DEM-derivative choice, not the physics.
- Neither model includes passive layover or cast shadow.
- The R classes follow the 2021 paper's description; Notti et al. (2014) use their own class cut-offs,
  which were not available to check here.
- One scene, one pair. Descriptive comparison, no significance test.
