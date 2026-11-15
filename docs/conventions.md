# Conventions

All of these are implemented in `qhantar/engine.py` and exercised by `tests/test_engine.py`.

## Frames and angles

- **ENU**: vectors are (East, North, Up) unit vectors at the target.
- **Slope β**: terrain inclination from horizontal, radians. 0 = flat.
- **Aspect α**: azimuth of the **downhill** direction, clockwise from north (0 = north, 90° = east).
  From a north-up DEM with row 0 at the northern edge: `dz/dE = dz/dcol / dx`, `dz/dN = −dz/drow / dy`,
  `β = atan(|∇z|)`, `α = atan2(−dz/dE, −dz/dN)`. Derivatives use metric pixel sizes (UTM metres), never degrees.
- **Downhill unit vector**: `u_slope = (sin α cos β, cos α cos β, −sin β)`.

## Line of sight

- `u_LOS = (losUnitVectorX, losUnitVectorY, sqrt(1 − x² − y²))`, **from the target to the sensor**.
  This is how the GUNW file itself describes the cube (`description` attribute of
  `/science/LSAR/GUNW/metadata/radarGrid/losUnitVectorX`) and how the ASF glossary defines it.
- Incidence angle from the vector: `θ = arccos(u_LOS,z)`; checked against the product's `incidenceAngle` cube.
- Angle formulation (used only for test 8 and H3): with platform heading ψ (flight azimuth,
  clockwise from north), the sensor-to-target look azimuth is ψ − 90° for a left-looking radar and
  ψ + 90° for a right-looking one; the target-to-sensor horizontal azimuth is that plus 180°.
  NISAR is left-looking in this product (`identification/lookDirection = Left`).

## Sensitivity

`S = u_slope · u_LOS`. **S > 0: hypothetical downhill motion projects towards the sensor**
(the range to the sensor would shorten). `|S|` is the magnitude used for the threshold. S is a
geometric property of a hypothetical motion and an observation; it is not a measurement of motion.

## Layover and shadow (range-plane model)

Let `h = (u_LOS,x, u_LOS,y)/|…|` be the horizontal unit vector pointing towards the sensor and
`d = (sin α, cos α)` the horizontal downhill direction. The slope seen in the range plane is

`β_r = atan( tan β · (d · h) )`, positive when the slope **faces the radar** (downhill towards the sensor).

The local incidence angle in the range plane is `θ − β_r`:

- **Layover** when the local incidence becomes negative: `β_r > θ` (fore-slope steeper than the incidence).
- **Shadow** when the local incidence exceeds 90°: `−β_r > 90° − θ` (back-slope steeper than the complement of the incidence).

This is the classical first-order, single-pixel criterion. It does not model passive layover or
shadow cast by distant terrain along the range line; those need a ray-tracing pass and are a known limitation.

## Four states and reasons

| State | Meaning |
| --- | --- |
| 1 | Interpretable |
| 2 | Visible, incoherent |
| 3 | Coherent, low sensitivity |
| 0 | Not observable or invalid |

The `reason` layer records why a pixel got its state. Rules are applied in this order and the
first that matches wins:

| Reason | Code | State |
| --- | --- | --- |
| nodata (phase/coherence missing, outside valid subswaths, water) | 3 | 0 |
| layover | 4 | 0 |
| shadow | 5 | 0 |
| flat (slope < `slope_min_deg`) | 6 | 0 |
| invalid connected component (value 0) | 7 | 0 |
| low sensitivity **and** low coherence | 8 | 0 |
| interpretable | 0 | 1 |
| visible incoherent | 1 | 2 |
| coherent low sensitivity | 2 | 3 |

Parameters (defaults): `s_min = 0.3`, `coh_min = 0.5`, `slope_min_deg = 2.0`. They are function
arguments, written to `results.json` and shown in the web app. Coherence and sensitivity are never
multiplied or combined into a single score.
