# QHANTAR status

Only items backed by a command output or a file in this repository are marked done.

| Item | Status | Evidence |
| --- | --- | --- |
| Python environment (numpy, h5py, rasterio, pyproj) | Done | `python -c "import h5py, rasterio, pyproj, numpy"` OK |
| NISAR GUNW over La Paz selected and downloaded | Done | file in `data/raw/` (not in git); granuleId, CRID P05023 and dates read from the file match `docs/search-record.json`; La Paz (590716 E, 8175565 N, UTM 19S) inside the 80 m grid |
| Product inspection report | Done | `docs/product-inspection.md` (219 datasets) from `scripts/inspect_gunw.py` |
| Engine + analytical tests | Done | `pytest`: 19 passed (covers the 8 cases of the master document plus extras) |
| Real scene processed, four-state map | Done (pending review at stop 2) | `results/<granule>/results.json`, `geotiff/`, `web/`; checks: LOS norm dev 6e-8, incidence vs cube ≤2e-5°, LOS azimuth 80.1–80.6° (sensor east, left-looking ascending), S by aspect matches analytic values, landmarks (Plaza Murillo 3635 m, Titicaca 3808 m, Illimani 6399 m) in place, fractions sum to 1 |
| H1 | Pending | |
| H2 (R-index contrast) | Pending | |
| H3 (native LOS vs heading/incidence) | Pending | |
| H4 (known active zones of La Paz) | Pending | |
| Web app | Pending | |
| Validation with real users | Not done | |
