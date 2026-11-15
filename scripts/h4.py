"""H4 (context, not validation): what does QHANTAR show where known landslides of La Paz were reported?

Inventory: NASA Global Landslide Catalog export (data.nasa.gov, "Global_Landslide_Catalog_Export_rows.csv";
Kirschbaum et al. 2010, 2015). Events are points with a stated location accuracy, not mapped polygons,
so each event is represented by a disc whose radius is that accuracy. For each disc we report the share of
the four states (footprint pixels) next to the same shares for the whole La Paz crop. No hypothesis test
is run: the inventory is too coarse for one, and this is said in the output.

Second inventory (optional third argument): GAMLP "Mapa de Escarpe de Deslizamiento en el Municipio de La Paz"
(OMPD 2013, GeoBolivia, MultiLineString). Scarps are rasterised onto the 80 m grid (all touched pixels) and their
state mix is compared with every footprint pixel inside the scarps' bounding box, raw and reweighted to the same
slope distribution (5 deg bins). Scarps are 2013 mapping, not 2026 motion: still context, not validation.

Usage: python scripts/h4.py <GLC export csv> results/<scene folder> [<GAMLP scarps geojson>]
Writes docs/h4-glc-lapaz.csv (the events used) and the key "h4" in results.json.
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pyproj
import rasterio

BBOX = (-68.40, -16.75, -67.90, -16.30)  # La Paz crop, same as process_scene.LAPAZ_BBOX
STATES = {1: "interpretable", 2: "visible_incoherent", 3: "coherent_low_sensitivity", 0: "not_observable_or_invalid"}
KEEP = ("event_id", "event_date", "event_title", "location_description", "location_accuracy", "landslide_category",
        "landslide_size", "landslide_trigger", "source_name", "source_link", "longitude", "latitude")


def shares(st, rs):
    fp = st != 255
    st, rs = st[fp], rs[fp]
    out = {"n_pixels": int(st.size), **{n: float((st == s).mean()) if st.size else None for s, n in STATES.items()}}
    out["flat_terrain_reason"] = float((rs == 6).mean()) if st.size else None  # reason 6 = flat
    return out


def slope_matched_shares(sel, ref, state, slope, width=5.0):
    """State shares of `ref` pixels reweighted so their slope bins match those of `sel`."""
    b = np.floor(slope / width)
    w = np.zeros(state.shape)
    for k, n in zip(*np.unique(b[sel], return_counts=True)):
        m = ref & (b == k)
        if m.any():
            w[m] = n / m.sum()
    tot = w[ref].sum()
    return {n: float(w[ref & (state == s)].sum() / tot) for s, n in STATES.items()}


def scarps(path, state, reason, slope, tf):
    from rasterio.features import rasterize
    from rasterio.warp import transform_geom
    raw = Path(path).read_bytes()
    gj = json.loads(raw)
    geoms = [transform_geom("EPSG:4326", "EPSG:32719", f["geometry"]) for f in gj["features"]]
    on = rasterize(((g, 1) for g in geoms), out_shape=state.shape, transform=tf, all_touched=True, dtype="uint8") == 1
    rows, cols = np.nonzero(on)
    box = np.zeros_like(on)
    box[rows.min():rows.max() + 1, cols.min():cols.max() + 1] = True
    fp = state != 255
    on &= fp
    ref = box & fp & ~on
    return {"name": "GAMLP Mapa de Escarpe de Deslizamiento en el Municipio de La Paz (OMPD 2013)",
            "source": "GeoBolivia, via the archive.org mirror https://archive.org/download/geobolivia_GobMunicipal."
                      "escarpe_de_deslizamientowgs84/GobMunicipal:escarpe_de_deslizamientowgs84.geojson",
            "md5": hashlib.md5(raw).hexdigest(), "features": len(gj["features"]),
            "scarp_pixels": shares(state[on], reason[on]),
            "rest_of_bounding_box": shares(state[ref], reason[ref]),
            "rest_of_bounding_box_slope_matched": slope_matched_shares(on, ref, state, slope),
            "median_slope_deg": {"scarp_pixels": float(np.nanmedian(slope[on])), "rest_of_bounding_box": float(np.nanmedian(slope[ref]))}}


def main(csv_path, res_dir, scarps_path=None):
    raw = Path(csv_path).read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    ev = [r for r in rows if r["longitude"] and r["latitude"]
          and BBOX[0] <= float(r["longitude"]) <= BBOX[2] and BBOX[1] <= float(r["latitude"]) <= BBOX[3]]

    out = Path("docs/h4-glc-lapaz.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, KEEP, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(ev)

    with rasterio.open(Path(res_dir) / "full" / "state.tif") as src:
        state, tf, epsg = src.read(1), src.transform, src.crs.to_epsg()
    read = lambda sub, n: rasterio.open(Path(res_dir) / sub / f"{n}.tif").read(1)
    reason, crop, crop_reason = read("full", "reason"), read("geotiff", "state"), read("geotiff", "reason")
    to_utm = pyproj.Transformer.from_crs(4326, epsg, always_xy=True)
    rows_i, cols_i = np.mgrid[0:state.shape[0], 0:state.shape[1]]
    xs, ys = tf.c + (cols_i + 0.5) * tf.a, tf.f + (rows_i + 0.5) * tf.e

    events = []
    for r in ev:
        m = re.fullmatch(r"(\d+)km", r["location_accuracy"].strip())
        radius_km = float(m.group(1)) if m else None
        x, y = to_utm.transform(float(r["longitude"]), float(r["latitude"]))
        e = {k: r[k] for k in ("event_id", "event_date", "event_title", "location_accuracy", "landslide_category", "landslide_size")}
        e["event_date"] = e["event_date"][:10]
        if radius_km:
            disc = (xs - x) ** 2 + (ys - y) ** 2 <= (radius_km * 1000) ** 2
            e["radius_km"] = radius_km
            e["state_shares_in_disc"] = shares(state[disc], reason[disc])
        events.append(e)

    slope = read("full", "slope_deg")
    gamlp = scarps(scarps_path, state, reason, slope, tf) if scarps_path else None
    h4 = {
        "question": "Which QHANTAR states cover the places where landslides in La Paz were reported?",
        "status": "context only, not a validation",
        "inventory": {"name": "NASA Global Landslide Catalog export", "file": "Global_Landslide_Catalog_Export_rows.csv",
                      "url": "https://data.nasa.gov/docs/legacy/Global_Landslide_Catalog_Export/Global_Landslide_Catalog_Export_rows.csv",
                      "md5": hashlib.md5(raw).hexdigest(), "rows": len(rows), "events_in_la_paz_crop": len(ev),
                      "citation": "Kirschbaum et al. 2010, Nat. Hazards 52:561-575; Kirschbaum, Stanley & Zhou 2015, "
                                  "Geomorphology, doi:10.1016/j.geomorph.2015.03.016"},
        "la_paz_crop_state_shares": shares(crop, crop_reason),
        "events": events,
        "gamlp_scarps": gamlp,
        "reading": "the catalogue places events with 1 to 10 km uncertainty, while QHANTAR pixels are 80 m; "
                   "a disc of that size covers whole valleys, so its state mix cannot say whether the slope that "
                   "failed was observable",
        "limitations": ["only events in this one catalogue; no municipal or published inventory was used",
                        "events are points with stated accuracy, not mapped landslide outlines",
                        "events date from before the 2026 acquisitions; the pair cannot show those movements",
                        "a state mix is not a detection: QHANTAR does not detect landslides"],
    }
    rj = Path(res_dir) / "results.json"
    res = json.loads(rj.read_text())
    res["h4"] = h4
    rj.write_text(json.dumps(res, indent=1))
    print(json.dumps(h4, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])
