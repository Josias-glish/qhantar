# Space Apps 2026 submission text

Ready to paste. Figures come from `results/T118_A_F169_20261008_20261020_P05023/results.json`.

## Project name

QHANTAR — knowing where to trust the radar, and where not

## Challenge

Dancing with the SARs

## Short description (one paragraph)

QHANTAR takes a real NISAR L2 GUNW interferogram and a DEM, and maps where that specific
observation could interpret downhill slope motion. For every pixel it projects a hypothetical
downhill motion on the product's native line-of-sight vectors (sensitivity S). It then crosses |S|
with the coherence and connected components measured in the same pair. The result is four states:

1. interpretable
2. visible but incoherent
3. coherent but barely sensitive
4. not observable or invalid

Phase, coherence, sensitivity and masks stay separate layers. Nothing is merged into a risk score.

On an ascending pass over La Paz, Bolivia (8–20 October 2026, provisional CRID P05023), the La Paz
crop splits as follows:

| State | Share of the La Paz crop |
| --- | ---: |
| Interpretable | 35.5 % |
| Visible but incoherent | 8.6 % |
| Coherent but barely sensitive | 23.6 % |
| Not observable or invalid | 32.4 % (mostly flat altiplano) |

## Longer description

**Problem.** In mountains, a missing InSAR signal does not always mean no motion. The radar may
simply not be sensitive to a slope's downhill direction, or the pair may have lost coherence there.
Reading a single interferogram without checking both leads to wrong conclusions.

**What we built.**

- A tested Python engine: slope and aspect, the downhill vector, S = u_slope · u_LOS, first-order
  layover and shadow, and the four-state classification with a "reason" layer. 20 analytical tests.
- A processing script that reads the NISAR GUNW and does the following:
  - reads phase, coherence, connected components, mask and the 3-D LOS and incidence cubes;
  - regrids Copernicus GLO-30 and converts it to ellipsoidal heights;
  - interpolates the cubes per pixel;
  - writes GeoTIFFs, web layers and a `results.json` with full provenance and consistency checks.
- A bilingual (ES/EN) static web app with five views: mission, mountain, radar evidence,
  slope–LOS observability and evidence passport.

**Results.**

| Region | Pixels | Interpretable | Visible, incoherent | Coherent, low sensitivity | Not observable |
| --- | ---: | ---: | ---: | ---: | ---: |
| Radar footprint | 8,972,101 | 37.9 % | 3.9 % | 19.7 % | 38.5 % |
| La Paz crop | 420,046 | 35.5 % | 8.6 % | 23.6 % | 32.4 % |

Median coherence of valid pixels is 0.737.

Hypothesis H1 passes its pre-registered comparison. Pixels flagged as layover or shadow have:

- a median coherence of 0.557, against 0.738 for geometrically valid pixels;
- 20.2 % invalid connected components, against 2.5 %.

But once valid pixels are reweighted to the same slopes, they score 0.510 and 20.6 %, no better than
layover/shadow. The difference comes from slope steepness, not from layover or shadow.
H2: the layover and shadow flags are consistent with an independent R-index (κ 0.880 and 0.838).
H3: the native LOS changes the state of 3.1 % of the pixels compared with a heading/incidence approximation.
H4 (context, not validation): on the 1,026 landslide scarps mapped by the La Paz municipality in 2013, 61.8 % of pixels are
interpretable and 0.3 % not observable; the NASA Global Landslide Catalog was too coarse to use.

**What it is not.** It is not a landslide detector, a risk index or a displacement measurement. A
single 12-day pair cannot reveal slow landslides (5 cm/year ≈ 1.6 mm in 12 days).

**Prior work.** It builds on Notti et al. (2010, NHESS 10:1865) and van Natijne et al. (2022, JAG 111:102829).
Our differentiation is applying the idea a posteriori to one NISAR pair with native geometry and
measured quality. We do not claim to be the first.

## NASA data used

- **NISAR L2 Geocoded Unwrapped Interferogram (GUNW), provisional** (NASA/JPL, ASF DAAC), DOI 10.5067/NIL2GUNW-P1.
  - Granule `NISAR_L2_PR_GUNW_032_118_A_169_033_2000_SH_20261008T102402_20261008T102436_20261020T102402_20261020T102436_P05023_N_F_J_001`.
  - Ascending, track 118, frame 169, HH, CRID P05023.
  - Second granule `NISAR_L2_PR_GUNW_031_097_D_097_032_2000_SH_20260924T224522_20260924T224556_20261006T224522_20261006T224556_P05023_N_F_J_001`: descending, track 97, frame 97, CRID P05023 (two-orbit comparison, `docs/two-orbits.md`).

## Other data

- Copernicus DEM GLO-30 (ESA / European Union, open AWS bucket)
- OpenStreetMap basemap

## Links

- Repository: https://github.com/Josias-glish/qhantar
- Web app: https://qhantar.vercel.app (static build of `web/`, hosted on Vercel)
- Method: `docs/method.md` · H1: `docs/validation-h1.md` · AI usage: `docs/ai-usage.md`
- Explainer for the jury (Spanish PDF): `docs/QHANTAR-funcionamiento.pdf` · Jury pitch (Spanish): `docs/pitch-jurado.es.md`

## Tools and AI

Python (numpy, h5py, rasterio, pyproj, matplotlib, pytest); React, TypeScript, Vite, MapLibre GL.
AI tools: Claude (Anthropic), ChatGPT (OpenAI), Antigravity (Google). Details in `docs/ai-usage.md`.
