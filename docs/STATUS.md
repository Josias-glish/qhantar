# QHANTAR status

Only items backed by a command output or a file in this repository are marked done.

| Item | Status | Evidence |
| --- | --- | --- |
| Python environment (numpy, h5py, rasterio, pyproj) | Done | `python -c "import h5py, rasterio, pyproj, numpy"` OK |
| NISAR GUNW over La Paz selected and downloaded | Done | file in `data/raw/` (not in git); granuleId, CRID P05023 and dates read from the file match `docs/search-record.json`; La Paz (590716 E, 8175565 N, UTM 19S) inside the 80 m grid |
| Product inspection report | Done | `docs/product-inspection.md` (219 datasets) from `scripts/inspect_gunw.py` |
| Engine + analytical tests | Done | `pytest`: 20 passed (covers the 8 cases of the master document plus extras) |
| Real scene processed, four-state map | Done (reviewed at stop 2) | `results/T118_A_F169_20261008_20261020_P05023/results.json`, `geotiff/`, `web/`; checks: LOS norm dev 6e-8, incidence vs cube ≤2e-5°, LOS azimuth 80.1–80.6° (sensor east, left-looking ascending), S by aspect matches analytic values, landmarks (Plaza Murillo 3635 m, Titicaca 3808 m, Illimani 6399 m) in place, fractions sum to 1 |
| H1 | Done: supported in this scene, with a steep-slope confound | `docs/validation-h1.md`, `results.json` → `h1` |
| H2 (R-index contrast) | Done: consistent (criterion κ ≥ 0.8 fixed before running) | `docs/validation-h2.md`, `results.json` → `h2`; layover κ 0.880, shadow κ 0.838; control with QHANTAR's own slope/aspect gives κ 1.000, so the residual is the DEM-derivative method |
| H3 (native LOS vs heading/incidence) | Done: quantified | `docs/validation-h3.md`, `results.json` → `h3`; control with native LOS reproduces `state.tif` exactly; 3.1 % of pixels change state with constant heading and incidence, 1.7 % with constant heading only |
| H4 (known active zones of La Paz) | Not testable with the available inventory; context reported | `docs/validation-h4.md`, `docs/h4-glc-lapaz.csv`, `results.json` → `h4`; NASA Global Landslide Catalog has 4 events in the crop with 1 to 10 km accuracy (one probably mis-geocoded); a real test needs mapped outlines |
| Web app (5 views, ES/EN) | Done | `npm run build` clean (no TS errors or warnings); built site walked in headless Chromium, 5 views × 2 languages, no console errors; layers land on La Paz (flat El Alto altiplano grey, canyon slopes coloured); every visible number checked by script against `results.json`; captures in `docs/screenshots/` |
| Web cover + visual redesign | Done | cover in `web/src/Cover.tsx`: AI illustration labelled as such, handed over along the real DEM to real La Paz layers (chip names DEM vs NISAR per layer), figures from `results.json`; `npm run build` clean; headless Chromium: no console errors in cover + 5 views × ES/EN, numbers in UI locale, no horizontal overflow at 390 and 1440 px, caption flick test, video-blocked fallback and reduced-motion static cover; design detector: no findings; independent finish review: "ship" |
| Documentation and jury material (EN) | Done | `README.md`, `LICENSE` (MIT), `docs/method.md`, `docs/ai-usage.md` (ChatGPT, Antigravity and human-verification sections left for the team), `docs/pitch.md`, `docs/submission.md`; every figure checked by script against `results.json`; literature references checked against NHESS and Crossref |
| Reproduction from a clean clone (README commands) | Done | fresh `git clone` on Windows 11 / Git Bash: new venv + `pip install -r requirements.txt`, `pytest` 20 passed, the 12 DEM tiles re-downloaded with the README loop are byte-identical (md5) to the ones used, `process_scene.py` + `h1.py` re-run on the same GUNW: `fractions`, `quality`, `h1` and `parameters` in the new `results.json` identical to the committed one |
| Validation with real users | Not done | |
