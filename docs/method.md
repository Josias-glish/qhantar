# Method

Implementation: `qhantar/engine.py` (pure functions on numpy arrays) and `scripts/process_scene.py`
(I/O, regridding, checks). Sign conventions and the layover/shadow derivation are spelled out in
[`conventions.md`](conventions.md); the analytical tests are in `tests/test_engine.py`.

## Inputs

| Input | Where it comes from |
| --- | --- |
| Unwrapped phase (rad), coherence, connected components | `/science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/HH/` |
| Validity mask | `.../unwrappedInterferogram/mask`: low byte = water digit, reference subswath digit, secondary subswath digit |
| LOS unit vector (East, North), incidence angle | 3-D cubes in `/science/LSAR/GUNW/metadata/radarGrid/` (height above the WGS84 ellipsoid, −500 to 9000 m) |
| Terrain | Copernicus GLO-30, averaged onto the 80 m GUNW grid, converted from EGM2008 to ellipsoidal heights |

The cubes are interpolated trilinearly at each pixel's (x, y, ellipsoidal height). That is why the
geoid correction is applied, even though its effect on the LOS here is about 2·10⁻⁵.

## Formulas

From the DEM on a metric grid:

- slope `β = atan(|∇z|)`
- aspect `α = atan2(−∂z/∂E, −∂z/∂N)`: the downhill azimuth, clockwise from north
- `u_slope = (sin α cos β, cos α cos β, −sin β)`, the downhill unit vector in ENU

From the product: `u_LOS = (x, y, √(1 − x² − y²))`, the target-to-sensor unit vector.

**Sensitivity:** `S = u_slope · u_LOS`.

- S > 0 means a hypothetical downhill motion would move towards the sensor.
- |S| close to 1 means the motion lies along the line of sight; close to 0, the motion is almost invisible.
- S describes geometry. It is not a measurement of motion.

**Layover and shadow** (first-order, per pixel):

- range-plane slope: `β_r = atan(tan β · (d · h))`, where `d` is the horizontal downhill direction and `h` the horizontal direction to the sensor
- **layover** when `β_r > θ`
- **shadow** when `−β_r > 90° − θ`

**Classification.** Rules are applied in order; the first that matches sets the state and the reason:

1. no data
2. layover
3. shadow
4. flat
5. invalid connected component
6. low |S| and low coherence

If none of these apply, the pixel gets state 1, 2 or 3 depending on whether |S| ≥ `s_min` and coherence ≥ `coh_min`.

**Validity** is checked pixel by pixel. A pixel is valid only if:

- both subswath digits of the mask are non-zero;
- the water digit is 0;
- phase, coherence, DEM and LOS are all finite.

## Thresholds and why

| Parameter | Default | Reason |
| --- | --- | --- |
| `s_min` | 0.3 | Initial value from the team's master document. It is an adjustable starting point, not a universal constant or a demonstrated result. |
| `coh_min` | 0.5 | Same source and the same caveat. |
| `slope_min_deg` | 2° | Below about 2° the downhill direction is not well defined at 80 m. Such pixels are labelled "flat" rather than given an arbitrary aspect. |
| invalid component | 0 | Inferred, not documented: the file holds only 0 and 1, every no-data pixel carries 0, the master document says so, and it is the usual unwrapper convention. Neither the file attributes, the ASF page nor the product specification define it. |

All four are function arguments. They are written to `results.json` and shown in the web app.
They were not tuned to make H1 pass.

## Outputs

Each layer is written separately, as a GeoTIFF (UTM 19S, 80 m) and as a web PNG:

- state and reason
- |S|
- phase in radians
- coherence
- connected components
- slope and aspect
- hillshade

`results.json` holds provenance, parameters, conventions, fractions per region, quality statistics,
the consistency checks and H1.

## Consistency checks on the real scene

These are recorded in `results.json` → `checks`:

- **LOS norm:** largest deviation from 1 is 6·10⁻⁸.
- **Incidence:** the angle derived from the LOS differs from the product's incidence cube by at most 1.5·10⁻⁵°.
- **LOS azimuth:** 80.1° to 80.6°, so the sensor is to the east. This matches a left-looking ascending pass with a flight heading of about −11°.
- **Sensitivity by aspect:** the sign and size of S per aspect match the analytical values.
- **Fractions:** they sum to 1.

## Limitations

- One scene and one 12-day pair, with PROVISIONAL processing (CRID P05023). ASF documents a timestamp issue for that CRID.
- First-order layover/shadow model. Passive layover and shadow cast by distant terrain are not modelled.
- Aspect is computed on grid north, not true north. The UTM meridian convergence is −0.61° to +0.35° and is not corrected; its effect on S is below about 0.01.
- Treating connected component 0 as invalid is an inference.
- Coherence measures the quality of the pair. It does not guarantee that motion is detectable.
- State 1 does not mean that motion exists or would be detected.
- A single line of sight cannot separate the East, North and vertical components of motion.
- The 80 m grid smooths narrow ravines.
