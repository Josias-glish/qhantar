"""Process one NISAR GUNW granule end to end with QHANTAR.

Usage:
  python scripts/process_scene.py data/raw/<granule>.h5 data/raw/dem [--s-min 0.3 --coh-min 0.5 --slope-min-deg 2]

Writes results/T<track>_<A|D>_F<frame>_<ref date>_<sec date>_<CRID>/:
  results.json          provenance, parameters, fractions, quality statistics, checks
  web/*.png             layers reprojected to EPSG:4326 for the web (La Paz crop + full scene preview)
  geotiff/*.tif         La Paz crop, every layer, native UTM 80 m grid (committed)
  full/*.tif            full scene, every layer (regenerable, not committed)
"""
import argparse
import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import h5py
import matplotlib
import matplotlib.image
import numpy as np
import pyproj
import rasterio
from rasterio.transform import from_origin, array_bounds
from rasterio.warp import Resampling, reproject, calculate_default_transform

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qhantar import engine as E  # noqa: E402

GRID = "/science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/"
CUBE = "/science/LSAR/GUNW/metadata/radarGrid/"
IDENT = "/science/LSAR/identification/"
LAPAZ_BBOX = (-68.40, -16.75, -67.90, -16.30)  # lon_min, lat_min, lon_max, lat_max
STATE_COLORS = {0: "#999999", 1: "#0072B2", 2: "#D55E00", 3: "#F0E442"}  # Okabe-Ito based
REASON_COLORS = {0: "#0072B2", 1: "#D55E00", 2: "#F0E442", 3: "#000000", 4: "#CC79A7",
                 5: "#56B4E9", 6: "#E5E5E5", 7: "#009E73", 8: "#7F7F7F"}


def s(v):
    v = v[()]
    if isinstance(v, np.ndarray):
        return [x.decode() if isinstance(x, bytes) else x.item() for x in v.ravel()]
    return v.decode() if isinstance(v, bytes) else v.item() if hasattr(v, "item") else v


def read_gunw(path):
    f = h5py.File(path, "r")
    g = {k: f[GRID + p][()] for k, p in {
        "phase": "HH/unwrappedPhase", "coh": "HH/coherenceMagnitude",
        "cc": "HH/connectedComponents", "mask": "mask", "x": "xCoordinates", "y": "yCoordinates"}.items()}
    g["epsg"] = int(f[GRID + "projection"].attrs["epsg_code"])
    g["cube"] = {k: f[CUBE + k][()] for k in ("losUnitVectorX", "losUnitVectorY", "incidenceAngle",
                                              "alongTrackUnitVectorX", "alongTrackUnitVectorY")}
    g["cube_axes"] = {k: f[CUBE + k][()] for k in ("heightAboveEllipsoid", "yCoordinates", "xCoordinates")}
    g["ident"] = {k: s(f[IDENT + k]) for k in (
        "granuleId", "compositeReleaseId", "orbitPassDirection", "lookDirection", "trackNumber", "frameNumber",
        "referenceZeroDopplerStartTime", "referenceZeroDopplerEndTime", "secondaryZeroDopplerStartTime",
        "secondaryZeroDopplerEndTime", "processingDateTime", "productVersion", "productSpecificationVersion",
        "productDoi", "productType", "productLevel", "radarBand", "listOfFrequencies",
        "referenceAbsoluteOrbitNumber", "secondaryAbsoluteOrbitNumber", "isFullFrame")}
    g["dem_source_in_product"] = s(f["/science/LSAR/GUNW/metadata/processingInformation/inputs/demSource"])
    f.close()
    return g


def dem_to_grid(dem_dir, epsg, transform, shape):
    out = np.full(shape, np.nan, np.float32)
    tiles = sorted(glob.glob(str(Path(dem_dir) / "*.tif")))
    for t in tiles:
        with rasterio.open(t) as src:
            reproject(rasterio.band(src, 1), out, dst_transform=transform, dst_crs=f"EPSG:{epsg}",
                      resampling=Resampling.average, dst_nodata=np.nan, init_dest_nodata=False)
    return out, [Path(t).name for t in tiles]


def geoid_height(lon, lat):
    """EGM2008 geoid undulation N (m), so that h_ellipsoid = H_orthometric + N."""
    pyproj.network.set_network_enabled(True)
    t = pyproj.Transformer.from_crs("EPSG:4326+3855", "EPSG:4979", always_xy=True)
    _, _, h = t.transform(lon, lat, np.zeros_like(lon))
    if not np.all(np.isfinite(h)) or np.all(h == 0):
        raise RuntimeError("EGM2008 grid not available (PROJ network); cannot convert DEM heights")
    return h


def stats(a):
    a = a[np.isfinite(a)]
    if a.size == 0:
        return None
    q = np.percentile(a, [5, 25, 50, 75, 95])
    return {"n": int(a.size), "min": float(a.min()), "p05": float(q[0]), "p25": float(q[1]),
            "median": float(q[2]), "p75": float(q[3]), "p95": float(q[4]), "max": float(a.max())}


def fractions(codes, region, names):
    n = int(region.sum())
    return {"n_pixels": n, "fractions": {names[k]: float(((codes == k) & region).sum() / n) for k in names},
            "counts": {names[k]: int(((codes == k) & region).sum()) for k in names}}


def write_tif(path, arr, transform, epsg, nodata=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(path, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1,
                       dtype=arr.dtype, crs=f"EPSG:{epsg}", transform=transform, nodata=nodata,
                       compress="deflate", predictor=2 if arr.dtype.kind == "f" else 1, tiled=True) as d:
        d.write(arr, 1)


def to_wgs84(arr, transform, epsg, bbox=None, categorical=False, max_px=None):
    """Reproject a UTM layer to EPSG:4326, optionally clipped to bbox. Returns array and bounds."""
    h, w = arr.shape
    src_bounds = array_bounds(h, w, transform)
    dt, dw, dh = calculate_default_transform(f"EPSG:{epsg}", "EPSG:4326", w, h, *src_bounds)
    if bbox:
        res = abs(dt.a)
        dw, dh = int(round((bbox[2] - bbox[0]) / res)), int(round((bbox[3] - bbox[1]) / res))
        dt = from_origin(bbox[0], bbox[3], res, res)
    if max_px and max(dw, dh) > max_px:
        k = max(dw, dh) / max_px
        dt = from_origin(dt.c, dt.f, dt.a * k, -dt.e * k)
        dw, dh = int(dw / k), int(dh / k)
    out = np.full((dh, dw), np.nan, np.float32)
    reproject(arr.astype(np.float32), out, src_transform=transform, src_crs=f"EPSG:{epsg}",
              dst_transform=dt, dst_crs="EPSG:4326", src_nodata=np.nan, dst_nodata=np.nan,
              resampling=Resampling.nearest if categorical else Resampling.bilinear)
    west, south, east, north = array_bounds(dh, dw, dt)
    return out, [[west, north], [east, north], [east, south], [west, south]]


def png_continuous(path, arr, cmap, vmin, vmax):
    rgba = matplotlib.colormaps[cmap]((np.clip(arr, vmin, vmax) - vmin) / (vmax - vmin))
    rgba[~np.isfinite(arr)] = 0
    matplotlib.image.imsave(path, (rgba * 255).astype(np.uint8))


def png_categorical(path, arr, colors, alpha=None):
    rgba = np.zeros(arr.shape + (4,), np.uint8)
    for k, c in colors.items():
        r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
        a = 255 if alpha is None else alpha.get(k, 255)
        rgba[arr == k] = (r, g, b, a)
    matplotlib.image.imsave(path, rgba)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gunw")
    ap.add_argument("dem_dir")
    ap.add_argument("--s-min", type=float, default=E.DEFAULTS["s_min"])
    ap.add_argument("--coh-min", type=float, default=E.DEFAULTS["coh_min"])
    ap.add_argument("--slope-min-deg", type=float, default=E.DEFAULTS["slope_min_deg"])
    ap.add_argument("--out", default="results")
    a = ap.parse_args()

    g = read_gunw(a.gunw)
    gid = g["ident"]["granuleId"]
    f = gid.split("_")  # short folder name: Windows MAX_PATH breaks clones under the 150-char granule id
    out = Path(a.out) / f"T{f[5]}_{f[6]}_F{f[7]}_{f[11][:8]}_{f[13][:8]}_{f[15]}"
    x, y, epsg = g["x"], g["y"], g["epsg"]
    dx, dy = float(x[1] - x[0]), float(y[0] - y[1])
    transform = from_origin(x[0] - dx / 2, y[0] + dy / 2, dx, dy)  # coordinates are pixel centres
    shape = g["phase"].shape
    print(f"{gid}\n grid {shape} EPSG:{epsg} spacing {dx}x{dy} m")

    # --- validity from the product's own layers
    low = (g["mask"] & 0xFF).astype(np.int64)
    # radar footprint: at least one subswath digit set (the water digit alone is set outside the frame too)
    footprint = (g["mask"] != 255) & (low % 100 != 0)
    water = (low // 100) == 1
    subswath_ok = ((low // 10) % 10 > 0) & (low % 10 > 0)
    cc_valid = (g["cc"] != 0) & (g["cc"] != 65535)

    # --- DEM on the GUNW grid, slope/aspect in metres
    dem_ortho, dem_tiles = dem_to_grid(a.dem_dir, epsg, transform, shape)
    slope, aspect = E.slope_aspect(dem_ortho, dx, dy)
    print(f" DEM tiles {len(dem_tiles)}; DEM finite {np.isfinite(dem_ortho).mean():.4f}")

    # --- pixel lon/lat, geoid, ellipsoidal height
    to_ll = pyproj.Transformer.from_crs(epsg, 4326, always_xy=True)
    lon, lat = to_ll.transform(*np.meshgrid(x[::25], y[::25]))  # geoid is smooth: sample every 2 km
    N = geoid_height(lon, lat)
    N_full = np.kron(N, np.ones((25, 25)))[: shape[0], : shape[1]]
    h_ell = (dem_ortho + N_full).astype(np.float32)

    # --- interpolate the geometry cubes at (x, y, h_ell), in row blocks to bound memory
    za, ya, xa = (g["cube_axes"][k] for k in ("heightAboveEllipsoid", "yCoordinates", "xCoordinates"))
    names = ("losUnitVectorX", "losUnitVectorY", "incidenceAngle", "alongTrackUnitVectorX", "alongTrackUnitVectorY")
    cub = {k: np.full(shape, np.nan, np.float32) for k in names}
    lx0 = np.full(shape, np.nan, np.float32)  # LOS x if the geoid correction were ignored
    for r in range(0, shape[0], 400):
        rows = slice(r, r + 400)
        Xb, Yb = np.meshgrid(x, y[rows])
        for k in names:
            cub[k][rows] = E.interp_cube(g["cube"][k], za, ya, xa, h_ell[rows], Yb, Xb)
        lx0[rows] = E.interp_cube(g["cube"]["losUnitVectorX"], za, ya, xa, dem_ortho[rows], Yb, Xb)
    lx, ly, inc_cube = cub["losUnitVectorX"], cub["losUnitVectorY"], cub["incidenceAngle"]
    atx, aty = cub["alongTrackUnitVectorX"], cub["alongTrackUnitVectorY"]
    u_los = E.los_vector(lx, ly)

    # --- engine
    S = E.sensitivity(E.slope_vector(slope, aspect), u_los)
    layover, shadow = E.layover_shadow(slope, aspect, u_los)
    geom_ok = np.isfinite(dem_ortho) & np.isfinite(lx) & np.isfinite(ly)
    valid = footprint & subswath_ok & ~water & geom_ok & np.isfinite(g["phase"]) & np.isfinite(g["coh"])
    layover &= geom_ok
    shadow &= geom_ok
    state, reason = E.classify(S, g["coh"], valid, cc_valid, layover, shadow, slope,
                               s_min=a.s_min, coh_min=a.coh_min, slope_min_deg=a.slope_min_deg)
    state[~footprint], reason[~footprint] = 255, 255  # outside the product footprint: no data at all

    # --- checks with numbers
    v = valid
    norm_dev = np.abs(np.sqrt(lx**2 + ly**2 + u_los[2] ** 2) - 1)[v]
    inc_from_los = np.degrees(E.incidence_from_los(u_los))
    inc_diff = (inc_from_los - inc_cube)[v]
    los_az = np.degrees(np.arctan2(lx, ly))
    heading = np.degrees(np.arctan2(atx, aty))
    expected = heading + (90.0 if g["ident"]["lookDirection"].lower() == "left" else -90.0)
    az_diff = ((los_az - expected + 180) % 360 - 180)[v]
    checks = {
        "los_norm_max_abs_deviation": float(norm_dev.max()),
        "los_horizontal_norm_squared_max": float(np.nanmax((lx**2 + ly**2)[v])),
        "incidence_from_los_minus_cube_deg": stats(inc_diff),
        "los_horizontal_azimuth_deg": stats(los_az[v]),
        "flight_heading_from_alongTrack_deg": stats(heading[v]),
        "los_azimuth_minus_expected_for_look_side_deg": stats(az_diff),
        "geoid_N_m": stats(N),
        "los_x_change_if_geoid_ignored": stats(np.abs(lx - lx0)[v]),
        "dem_finite_fraction_in_footprint": float(np.isfinite(dem_ortho)[footprint].mean()),
    }
    meridian_conv = pyproj.Proj(f"EPSG:{epsg}").get_factors(lon[::8, ::8], lat[::8, ::8]).meridian_convergence
    checks["utm_meridian_convergence_deg"] = {"min": float(np.min(meridian_conv)), "max": float(np.max(meridian_conv))}

    # --- La Paz crop window on the UTM grid
    to_utm = pyproj.Transformer.from_crs(4326, epsg, always_xy=True)
    bx, by = to_utm.transform([LAPAZ_BBOX[0], LAPAZ_BBOX[2], LAPAZ_BBOX[0], LAPAZ_BBOX[2]],
                              [LAPAZ_BBOX[1], LAPAZ_BBOX[1], LAPAZ_BBOX[3], LAPAZ_BBOX[3]])
    c0, c1 = int((min(bx) - x[0]) / dx), int((max(bx) - x[0]) / dx) + 1
    r0, r1 = int((y[0] - max(by)) / dy), int((y[0] - min(by)) / dy) + 1
    win = (slice(r0, r1), slice(c0, c1))
    crop_transform = from_origin(x[c0] - dx / 2, y[r0] + dy / 2, dx, dy)
    lapaz = np.zeros(shape, bool)
    lapaz[win] = True

    state_names = {1: "interpretable", 2: "visible_incoherent", 3: "coherent_low_sensitivity", 0: "not_observable_or_invalid"}
    reason_names = E.REASONS
    results_fr = {
        "scene_footprint": {"states": fractions(state, footprint, state_names),
                            "reasons": fractions(reason, footprint, reason_names)},
        "la_paz_crop": {"states": fractions(state, footprint & lapaz, state_names),
                        "reasons": fractions(reason, footprint & lapaz, reason_names)},
    }
    quality = {
        "coherence_in_valid": stats(g["coh"][v]),
        "unwrapped_phase_rad_in_valid": stats(g["phase"][v]),
        "abs_S_in_valid": stats(np.abs(S)[v]),
        "slope_deg_in_valid": stats(np.degrees(slope)[v]),
        "connected_component_values": {str(k): int(n) for k, n in zip(*np.unique(g["cc"], return_counts=True))},
        "layover_fraction_of_geometry_ok_footprint": float(layover[footprint & geom_ok].mean()),
        "shadow_fraction_of_geometry_ok_footprint": float(shadow[footprint & geom_ok].mean()),
    }

    # --- layers
    layers = {
        "unwrapped_phase_rad": (g["phase"], np.nan),
        "coherence": (g["coh"], np.nan),
        "connected_components": (g["cc"].astype(np.uint16), 65535),
        "validity": (valid.astype(np.uint8), None),
        "dem_orthometric_m": (dem_ortho, np.nan),
        "slope_deg": (np.degrees(slope).astype(np.float32), np.nan),
        "aspect_deg": (np.degrees(aspect).astype(np.float32), np.nan),
        "los_east": (lx.astype(np.float32), np.nan),
        "los_north": (ly.astype(np.float32), np.nan),
        "los_up": (u_los[2].astype(np.float32), np.nan),
        "incidence_deg": (inc_from_los.astype(np.float32), np.nan),
        "sensitivity_S": (np.where(geom_ok, S, np.nan).astype(np.float32), np.nan),
        "layover": (layover.astype(np.uint8), None),
        "shadow": (shadow.astype(np.uint8), None),
        "state": (state, 255),
        "reason": (reason, 255),
    }
    for name, (arr, nd) in layers.items():
        write_tif(out / "full" / f"{name}.tif", arr, transform, epsg, nd)
        write_tif(out / "geotiff" / f"{name}.tif", np.ascontiguousarray(arr[win]), crop_transform, epsg, nd)

    # --- web PNGs (EPSG:4326)
    web = out / "web"
    web.mkdir(parents=True, exist_ok=True)
    corners = {}

    def nanify(arr, mask):
        a2 = arr.astype(np.float32).copy()
        a2[~mask] = np.nan
        return a2

    hill = np.full(shape, np.nan, np.float32)
    az, alt = np.deg2rad(315), np.deg2rad(45)
    hill[:] = np.cos(alt) * np.cos(slope) + np.sin(alt) * np.sin(slope) * np.cos(az - aspect)
    specs = {
        "state": (nanify(state, footprint), "cat", STATE_COLORS),
        "reason": (nanify(reason, footprint), "cat", REASON_COLORS),
        "abs_sensitivity": (nanify(np.abs(S), footprint & geom_ok), "viridis", (0, 1)),
        "phase": (nanify(g["phase"], np.isfinite(g["phase"])), "RdBu_r", (-24.0, 24.0)),
        "coherence": (nanify(g["coh"], np.isfinite(g["coh"])), "magma", (0, 1)),
        "connected_components": (nanify(cc_valid.astype(np.float32), footprint), "cat", {0: "#D55E00", 1: "#009E73"}),
        "slope": (nanify(np.degrees(slope), geom_ok), "cividis", (0, 45)),
        "aspect": (nanify(np.degrees(aspect), geom_ok & (slope >= np.deg2rad(a.slope_min_deg))), "twilight", (0, 360)),
        "hillshade": (nanify(hill, geom_ok), "gray", (0, 1)),
        # used only as a mask by the web cover (contour handover); no figure is read from it
        "elevation": (nanify(dem_ortho, np.isfinite(dem_ortho)), "gray", (2400.0, 5500.0)),
    }
    for region, bbox, max_px in (("lapaz", LAPAZ_BBOX, None), ("scene", None, 1400)):
        for name, (arr, kind, par) in specs.items():
            img, cor = to_wgs84(arr, transform, epsg, bbox, categorical=(kind == "cat"), max_px=max_px)
            p = web / f"{region}_{name}.png"
            if kind == "cat":
                lab = np.where(np.isfinite(img), img, -1).astype(np.int16)
                alpha = {0: 140} if name == "state" else None
                png_categorical(p, lab, par, alpha)
            else:
                png_continuous(p, img, kind, *par)
            corners[f"{region}_{name}"] = {"corners": cor, "colormap": kind, "range": None if kind == "cat" else list(par)}

    ident = g["ident"]
    crid = ident["compositeReleaseId"]
    maturity = {"P": "PROVISIONAL", "X": "BETA", "V": "VALIDATED"}.get(crid[0], "UNKNOWN")
    search = json.loads(Path("docs/search-record.json").read_text())
    res = {
        "qhantar_version": "0.1.0",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "provenance": {
            "granule": gid,
            "source": "NASA/JPL NISAR L2 GUNW via ASF DAAC",
            "collection": search.get("collectionName"),
            "download_url": search.get("url"),
            "doi": ident["productDoi"],
            "crid": crid,
            "maturity": maturity,
            "maturity_note": "PROVISIONAL (CRID P05023). ASF documents a P05023 timestamp issue that can cause InSAR decorrelation, fixed in P05036; no P05036 GUNW existed over La Paz on 2026-11-14.",
            "reference_acquisition": [ident["referenceZeroDopplerStartTime"], ident["referenceZeroDopplerEndTime"]],
            "secondary_acquisition": [ident["secondaryZeroDopplerStartTime"], ident["secondaryZeroDopplerEndTime"]],
            "orbit_pass": ident["orbitPassDirection"], "look_direction": ident["lookDirection"],
            "track": ident["trackNumber"], "frame": ident["frameNumber"],
            "frequency": ident["listOfFrequencies"], "polarization": "HH",
            "product_processing_utc": ident["processingDateTime"], "product_version": ident["productVersion"],
            "product_spec_version": ident["productSpecificationVersion"],
            "grid": {"epsg": epsg, "spacing_m": dx, "shape": list(shape)},
            "layers_used": {k: GRID + p for k, p in {"phase": "HH/unwrappedPhase", "coherence": "HH/coherenceMagnitude",
                            "connected_components": "HH/connectedComponents", "mask": "mask"}.items()}
                           | {k: CUBE + k for k in ("losUnitVectorX", "losUnitVectorY", "incidenceAngle")},
            "dem": {"name": "Copernicus GLO-30 DEM (EGM2008 heights)", "source": "https://copernicus-dem-30m.s3.amazonaws.com/",
                    "tiles": dem_tiles, "resampling": "average to the 80 m GUNW grid",
                    "vertical": "converted to WGS84 ellipsoidal height with EGM2008 (PROJ) before interpolating the geometry cubes",
                    "product_dem_for_reference": g["dem_source_in_product"][:200]},
        },
        "parameters": {"s_min": a.s_min, "coh_min": a.coh_min, "slope_min_deg": a.slope_min_deg,
                       "connected_component_invalid_value": 0,
                       "validity": "mask low byte: both subswath digits > 0 and water digit 0; finite phase, coherence, DEM and LOS"},
        "conventions": {"enu": True, "aspect": "downhill azimuth, clockwise from north",
                        "los": "target to sensor", "S_positive": "downhill motion projects towards the sensor"},
        "states": {"1": "interpretable", "2": "visible_incoherent", "3": "coherent_low_sensitivity", "0": "not_observable_or_invalid"},
        "reasons": {str(k): n for k, n in E.REASONS.items()},
        "colors": {"state": STATE_COLORS, "reason": REASON_COLORS},
        "fractions": results_fr,
        "quality": quality,
        "checks": checks,
        "regions": {"la_paz_crop_bbox_lonlat": LAPAZ_BBOX},
        "web_layers": {k: {"file": f"{k}.png", **c} for k, c in corners.items()},
        "h1": None,
    }
    old = out / "results.json"
    if old.exists():
        res["h1"] = json.loads(old.read_text()).get("h1")
    (out / "results.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({"checks": checks, "fractions_scene": results_fr["scene_footprint"]["states"]["fractions"],
                      "fractions_lapaz": results_fr["la_paz_crop"]["states"]["fractions"],
                      "reasons_scene": results_fr["scene_footprint"]["reasons"]["fractions"],
                      "reasons_lapaz": results_fr["la_paz_crop"]["reasons"]["fractions"]}, indent=1))


if __name__ == "__main__":
    main()
