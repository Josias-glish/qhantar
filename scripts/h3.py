"""H3: how much does the four-state result change when the native per-pixel LOS of the GUNW is replaced
by the usual approximation from platform heading and incidence?

Heading: from the reference orbit state vectors at mid acquisition (ECEF velocity in local ENU at the
sub-satellite point), so it does not use the product's LOS cubes. Two approximations, both left-looking:
  A  constant heading + constant incidence (median native incidence over valid pixels)
  B  constant heading + per-pixel native incidence
Everything else (slope, aspect, coherence, components, validity, thresholds) is held fixed and the same
qhantar.engine functions are used, so differences come only from the LOS. A control re-classifies with the
native LOS and must reproduce state.tif exactly.

This is a quantification, not a pass/fail test: no threshold is set for "material".

Usage: python scripts/h3.py data/raw/<granule>.h5 results/<scene folder>
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import h5py
import numpy as np
import pyproj
import rasterio

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qhantar import engine as E  # noqa: E402

ID = "/science/LSAR/identification/"
ORB = "/science/LSAR/GUNW/metadata/orbit/reference/"
STATES = {1: "interpretable", 2: "visible_incoherent", 3: "coherent_low_sensitivity", 0: "not_observable_or_invalid"}


def read(d, sub, name):
    with rasterio.open(Path(d) / sub / f"{name}.tif") as src:
        return src.read(1), src.transform


def orbit_heading(gunw):
    """Flight azimuth (rad, clockwise from north) of the reference orbit at mid acquisition."""
    with h5py.File(gunw, "r") as f:
        t, pos, vel = f[ORB + "time"][()], f[ORB + "position"][()], f[ORB + "velocity"][()]
        epoch = f[ORB + "time"].attrs["units"].decode().split("since ")[1]
        t0, t1 = (f[ID + k][()].decode()[:26] for k in ("referenceZeroDopplerStartTime", "referenceZeroDopplerEndTime"))
    sec = lambda s: (datetime.fromisoformat(s) - datetime.fromisoformat(epoch)).total_seconds()
    tm = (sec(t0) + sec(t1)) / 2
    p = np.array([np.interp(tm, t, pos[:, k]) for k in range(3)])
    v = np.array([np.interp(tm, t, vel[:, k]) for k in range(3)])
    lon, lat, _ = pyproj.Transformer.from_crs(4978, 4979, always_xy=True).transform(*p)
    lo, la = np.radians(lon), np.radians(lat)
    east = np.array([-np.sin(lo), np.cos(lo), 0.0])
    north = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
    return float(np.arctan2(v @ east, v @ north)), {"lon": float(lon), "lat": float(lat)}


def compare(u, inputs, native_S, native_state):
    slope, aspect, coh, valid, cc_valid, footprint = inputs
    S = E.sensitivity(E.slope_vector(slope, aspect), u)
    lay, sha = E.layover_shadow(slope, aspect, u)
    geo = np.isfinite(S)
    lay &= geo
    sha &= geo
    state, _ = E.classify(S, coh, valid, cc_valid, lay, sha, slope)
    state[~footprint] = 255
    m = footprint & valid & np.isfinite(native_S)
    d = np.abs(np.abs(S) - np.abs(native_S))[m]
    changed = (state != native_state) & footprint
    by_state = {STATES[s]: float(changed[footprint & (native_state == s)].mean()) for s in STATES}
    return {"abs_S_difference": {"median": float(np.median(d)), "p95": float(np.percentile(d, 95)), "max": float(d.max())},
            "abs_S_threshold_crossings_fraction": float(((np.abs(S) >= 0.3) != (np.abs(native_S) >= 0.3))[m].mean()),
            "state_changed_fraction": float(changed[footprint].mean()),
            "state_changed_fraction_by_native_state": by_state,
            "n_pixels": int(footprint.sum())}, state


def main(gunw, res_dir):
    g = lambda n: read(res_dir, "full", n)[0]
    slope, aspect = np.deg2rad(g("slope_deg")), np.deg2rad(g("aspect_deg"))
    lx, ly, inc = g("los_east"), g("los_north"), np.deg2rad(g("incidence_deg"))
    coh, cc, native_state, reason, native_S = g("coherence"), g("connected_components"), g("state"), g("reason"), g("sensitivity_S")
    footprint = native_state != 255
    valid = footprint & (reason != 3)
    cc_valid = (cc != 0) & (cc != 65535)
    inputs = (slope, aspect, coh, valid, cc_valid, footprint)

    heading, subsat = orbit_heading(gunw)
    inc_const = float(np.median(inc[valid & np.isfinite(inc)]))
    u_native = E.los_vector(lx, ly)
    u_a = E.los_from_angles(np.full(inc.shape, inc_const), heading, "left")
    u_b = E.los_from_angles(inc, heading, "left")

    ctrl, _ = compare(u_native, inputs, native_S, native_state)
    res_a, st_a = compare(u_a, inputs, native_S, native_state)
    res_b, st_b = compare(u_b, inputs, native_S, native_state)

    # La Paz crop: same window as geotiff/
    tf_full, tf_crop = read(res_dir, "full", "state")[1], read(res_dir, "geotiff", "state")[1]
    c0, r0 = round((tf_crop.c - tf_full.c) / tf_full.a), round((tf_crop.f - tf_full.f) / tf_full.e)
    h, w = read(res_dir, "geotiff", "state")[0].shape
    win = (slice(r0, r0 + h), slice(c0, c0 + w))
    fp = footprint[win]
    lapaz = {k: float((st[win] != native_state[win])[fp].mean()) for k, st in (("A", st_a), ("B", st_b))}

    az_native = np.degrees(np.mod(np.arctan2(lx, ly), 2 * np.pi))[valid]
    az_approx = float(np.degrees(np.mod(heading + np.pi / 2, 2 * np.pi)))  # left-looking: sensor lies at heading + 90
    h3 = {
        "question": "How much does the four-state result change when the native per-pixel LOS is replaced by a "
                    "heading/incidence approximation?",
        "orbit_heading_deg": float(np.degrees(heading) % 360), "sub_satellite_point": subsat,
        "native_los_azimuth_target_to_sensor_deg": {"min": float(az_native.min()), "max": float(az_native.max()),
                                                   "approximation": az_approx},
        "native_incidence_deg": {"min": float(np.degrees(inc[valid].min())), "max": float(np.degrees(inc[valid].max())),
                                 "constant_used_in_A": float(np.degrees(inc_const))},
        "control_native_reproduces_state": ctrl["state_changed_fraction"] == 0.0,
        "A_constant_heading_constant_incidence": res_a,
        "B_constant_heading_per_pixel_incidence": res_b,
        "la_paz_crop_state_changed_fraction": lapaz,
        "reading": f"heading + 90 deg puts the look azimuth {az_native.min() - az_approx:.1f} to "
                   f"{az_native.max() - az_approx:.1f} deg away from the native LOS (B isolates this), and a constant "
                   f"incidence adds the across-swath spread of {np.degrees(inc[valid].min()):.1f} to "
                   f"{np.degrees(inc[valid].max()):.1f} deg (A)",
        "limitations": ["one scene, one pair",
                        "the approximation uses the product's own orbit at the sub-satellite point; a nominal published "
                        "heading could differ more or less",
                        "same first-order layover/shadow model for all variants"],
    }
    rj = Path(res_dir) / "results.json"
    r = json.loads(rj.read_text())
    r["h3"] = h3
    rj.write_text(json.dumps(r, indent=1))
    print(json.dumps(h3, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
