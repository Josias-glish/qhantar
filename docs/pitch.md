# Pitch, demo script and hard questions

Every figure here comes from `results/T118_A_F169_20261008_20261020_P05023/results.json`.

## Three versions of the pitch

**Short.** QHANTAR evaluates where a NISAR observation is interpretable in mountain terrain. It
crosses the geometry of each slope with the radar line of sight and with the measured quality of
the interferometric pair. That shows where there is enough sensitivity, and where the
interpretation should not be trusted.

**Differentiation.** The relation between slope and radar geometry already exists in the
scientific literature: Notti et al. 2010, van Natijne et al. 2022. Our contribution is not to
invent it. We apply it to one concrete NISAR GUNW pair, using its native LOS vectors and its
measured coherence and connected components, and produce a reproducible four-state classification.
That moves from a general estimate of observation potential to an interpretability analysis
conditioned on the evidence of one specific acquisition.

**Impact.** In mountain areas, a missing signal does not always mean there is no motion. It can
mean the radar was not sensitive to it. QHANTAR aims to help researchers and analysts recognise
that limitation before drawing conclusions.

## Demo script (about 2½ minutes)

Open the web app in English, La Paz region.

**1 · Mission summary (20 s).** "This is one real NISAR interferogram over La Paz. It is an ascending
pass, 8 to 20 October 2026, provisional processing, CRID P05023, and the badge says so. QHANTAR
asks one question: where could this specific observation see downhill motion, and where not? It
does not detect landslides and it does not measure displacement."

**2 · Mountain observatory (25 s).** Switch the layer to *slope*. "This is the terrain from the
Copernicus 30 m DEM, resampled to the 80 m NISAR grid. Here is the flat El Alto altiplano, and
here the La Paz canyon. On flat ground there is no downhill direction, so QHANTAR cannot say
anything there."

**3 · Radar evidence (30 s).** Show *coherence*, then *unwrapped phase*. "These are the radar's own
layers, shown separately and never merged. Median coherence of valid pixels is 0.737. Phase is
shown in radians, not converted to displacement. Coherence says the pair is good. It does not say
the radar is looking along the slope."

**4 · Slope–LOS observability (45 s).** Show the *four-state map*, then lower the opacity.

> "Here we cross both. S is the projection of a downhill motion on the native line of sight
> of this product. In the La Paz crop:
>
> - 35.5 % is **interpretable**: blue.
> - 8.6 % is **visible but incoherent**: orange.
> - 23.6 % is **coherent but barely sensitive**: yellow. Here a still slope and a moving slope
>   would look the same.
> - 32.4 % is **not observable**: grey. Mostly that is flat terrain, 29.9 %."
>
> "The thresholds, |S| 0.3 and coherence 0.5, are on screen and are parameters."

Switch to *reason* for a second to show why each grey pixel is grey.

**5 · Evidence passport (30 s).** "Every result carries its passport: granule, dates, CRID,
maturity, DOI, DEM and parameters. We also tested a hypothesis. Pixels our model flags as layover
or shadow have a median coherence of 0.557, against 0.738 for geometrically valid pixels. They
also have 20.2 % invalid components, against 2.5 %. So the hypothesis is supported in this scene.
But steep valid slopes are also worse, at 0.602, and we say so. H2 to H4 are still pending."

**Close (10 s).** "QHANTAR: knowing where to trust the radar, and where not."

## Hard questions

**Does this already exist?**
Yes, the underlying ideas do. Notti et al. (2010) used the R-index and visibility analysis.
van Natijne et al. (2022) built a world-wide InSAR sensitivity index for downhill motion. Both
assess potential *before* a given pair. Our proposal is to apply the idea *after*, on one NISAR GUNW,
with its native LOS vectors and its measured coherence and connected components, as a
reproducible four-state map. We do not claim to be first in the world.

**Does it detect landslides?**
No. It evaluates whether one radar observation could see a *hypothetical* downhill motion. State 1
means "interpretable", not "moving".

**Why isn't coherence enough?**
Because coherence measures the quality of the pair, not the geometry. In the La Paz crop, 23.6 % of
pixels are coherent but have |S| < 0.3. There, real downhill motion would barely project on the
line of sight.

**Why aren't slope and aspect enough?**
Because a geometric estimate ignores what actually happened in this pair. 8.6 % of the La Paz crop
has good sensitivity but coherence below 0.5.

**Why the native LOS vectors?**
They are the geometry the product itself provides, per pixel and per height. On this scene they
agree with the product's incidence cube to within 1.5·10⁻⁵°. Their azimuth spans 80.1° to 80.6°,
which is consistent with a left-looking ascending pass. Comparing them with the simpler
heading/incidence approximation is H3, which is still pending. We have not measured how much
difference it makes.

**Why four states?**
Because geometry and quality are different dimensions. Merging them into one score would hide
which one failed. The map, the |S| layer, the coherence layer and the reason layer are all shown
separately.

**How do we know it works?**
- 20 analytical tests: parallel and perpendicular LOS, flat terrain, five bearings, layover, shadow,
  state precedence, thresholds as parameters, and native LOS against the angle formulation.
- Consistency checks on the real scene: LOS norm, incidence against the product cube, LOS azimuth
  against the look side, and S by aspect against the analytical values.
- H1: supported, with a steep-slope confound.

What is missing: validation with users and against known active zones (H4).

**Can it give 3-D motion?**
No. One line of sight measures one projection.

**What if the data contradict the hypothesis?**
We publish it. H1 came out supported, but we report the confound that weakens it, and the
thresholds were not tuned to make it pass.

**Why provisional data?**
It was the only NISAR GUNW over La Paz available when we searched. The newer CRID P05036, which fixes
a documented timestamp issue, did not cover La Paz on 2026-11-14. The provisional status is shown on
every screen.
