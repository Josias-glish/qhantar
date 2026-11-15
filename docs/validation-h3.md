# H3: native LOS versus a heading/incidence approximation

**Scene:** same GUNW as H1 and H2. Produced by `scripts/h3.py`; the numbers are stored under `h3` in `results.json`.

## Question

How much does the four-state result change if the per-pixel line of sight stored in the GUNW is
replaced by the usual approximation from the platform heading and the incidence angle?

## How it was done

- **Heading.** Taken from the reference orbit state vectors at mid acquisition: the ECEF velocity
  expressed in local East/North at the sub-satellite point (lon −63.27°, lat −16.02°). That gives
  347.5°. It does not use the product's LOS cubes.
- **Look direction.** For a left-looking radar, the target-to-sensor azimuth is heading + 90° = 77.5°.
- **Variant A.** Constant heading and constant incidence (40.9°, the median native incidence).
- **Variant B.** Constant heading and the native incidence per pixel. B isolates the azimuth error.
- **Everything else fixed.** Slope, aspect, coherence, components, validity and thresholds are the
  same, and so are the engine functions. Only the LOS changes.
- **Control.** Re-classifying with the native LOS reproduces `state.tif` exactly (0 pixels changed).

## Result

The native target-to-sensor azimuth spans 80.1° to 80.6°. Heading + 90° is therefore off by
**2.6° to 3.1°**. Native incidence spans 33.7° to 47.3° across the swath.

| | A: constant heading + constant incidence | B: constant heading + native incidence |
| --- | ---: | ---: |
| abs(abs(S) approx − abs(S) native), median | 0.032 | 0.020 |
| same, 95th percentile | 0.080 | 0.034 |
| same, maximum | 0.128 | 0.039 |
| Pixels crossing the abs(S) = 0.3 threshold | 4.1 % | 2.7 % |
| **Pixels that change state, whole footprint** | **3.1 %** | **1.7 %** |
| Pixels that change state, La Paz crop | 2.9 % | 1.7 % |
| · of native state 1 Interpretable | 3.9 % | 2.1 % |
| · of native state 3 Coherent, low sensitivity | 6.1 % | 4.4 % |

**Reading.** In this frame the native geometry changes the state of 3.1 % of the pixels
compared with the full approximation. About half of that (1.7 %) comes from the look azimuth alone, because
heading ± 90° is not the zero-Doppler look direction at the target. The other half comes from
treating the incidence as constant across the swath (33.7° to 47.3°). States 3 and 1 change most
(6.1 % and 3.9 % in A), as expected for pixels whose |S| sits close to the 0.3 threshold.

## What this does not show

- One scene, one pair.
- The heading comes from the product's own orbit at the sub-satellite point. A nominal published
  heading, or one taken at the target latitude, would give a different offset.
- No threshold was set for "material". The numbers are reported as they are.
- The same first-order layover/shadow model is used for all variants.
