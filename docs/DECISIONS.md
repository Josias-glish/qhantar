# Decisions log

Minor decisions taken without stopping, with the reason.

- Python 3.12 virtual environment (3.14 is installed but binary wheels for rasterio are more reliable on 3.12).
- Repo-local git identity "QHANTAR team" (no personal email in a public history); to be confirmed at stop 3.
- Download done through the user's logged-in Chrome session (no `.netrc` on this PC). Integrity check: file size equals the ASF search record (2,281,701,376 bytes); ASF publishes no MD5 for this granule. Search record saved in `docs/search-record.json`.
- No P05036 (VALIDATED) GUNW exists over La Paz as of 2026-11-14; P05023 (PROVISIONAL) is the latest available. Chosen by the user at stop 1: ascending track 118, frame 169, 2026-10-08 / 2026-10-20.
- Connected components: the file only contains values 0 and 1 (no 65535 fill). Neither the file attributes, the ASF GUNW page nor product spec D-102272 Rev E define the meaning of 0. Treated as "not assigned / invalid" because (a) value 0 covers every nodata pixel, (b) the master document says so, (c) it is the usual unwrapper convention. Flagged as inferred, not documented.
- Validity mask (`unwrappedInterferogram/mask`, low byte = three decimal digits water/ref-subswath/sec-subswath, per the dataset's own description): a pixel is valid when both subswath digits are non-zero and the water digit is 0. Bit 24 (ionospheric filtering mask, "masked out and filled with interpolated data" for the ionosphere estimate) is NOT used as an invalidity flag for the phase.
- Minimum slope for a defined downhill direction: `slope_min_deg = 2.0` (configurable). Below it the pixel is state 0, reason "flat".
- Low sensitivity AND low coherence at the same time: state 0, reason code 8 (not covered by the master document's table).
- GUNW contains no layover/shadow layer; the spec lists `layover_percentage`/`shadow_percentage` only as possible mask attributes, and they are absent in this file. Layover/shadow come from QHANTAR's own range-plane model.
