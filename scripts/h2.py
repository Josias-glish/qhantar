"""H2: contrast QHANTAR's geometry with an independent implementation of the R-index.

R-index (Notti et al. 2010, 2014), as written in Remote Sens. 2021, 13, 1938, eq. (1):
    R = sin{ theta + arctan[ tan(alpha) * cos(phi - beta) ] }
alpha slope, beta aspect, theta LOS incidence, phi azimuth of the LOS (here: the look direction,
sensor -> target). Regions (same paper, sec. 2.2): R < 0 layover; 0 < R < sin(theta) foreshortening;
R >= sin(theta) good visibility. Active shadow is not separable by the value of R; we flag it from the
argument of the sine (theta + arctan[...] > 90 deg) and say so.

Independence: slope and aspect are recomputed here from the DEM with Horn's 3x3 method, not with
qhantar.engine (central differences); nothing from qhantar.engine is imported. The LOS azimuth and
incidence are the product's native ones (los_east/los_north, incidence_deg).

Criterion, fixed before running: the two models are "consistent" if Cohen's kappa >= 0.8 for both the
layover flag (R < 0 vs QHANTAR layover) and the active-shadow flag; otherwise "differ", and the
disagreements are reported. Pixels: QHANTAR valid pixels (reason not nodata) inside the footprint.

Usage: python scripts/h2.py results/<scene folder>
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

STATES = {1: "interpretable", 2: "visible_incoherent", 3: "coherent_low_sensitivity", 0: "not_observable_or_invalid"}
R_CLASSES = ("layover", "active_shadow", "foreshortening", "good_visibility")


def read(d, name):
    with rasterio.open(Path(d) / "full" / f"{name}.tif") as src:
        return src.read(1), src.transform


def horn(dem, dx, dy):
    """Slope and downhill aspect (radians) with Horn (1981) weights; rows run north -> south."""
    z = np.pad(dem.astype("float64"), 1, mode="edge")
    a, b, c = z[:-2, :-2], z[:-2, 1:-1], z[:-2, 2:]
    d, f = z[1:-1, :-2], z[1:-1, 2:]
    g, h, i = z[2:, :-2], z[2:, 1:-1], z[2:, 2:]
    dz_de = ((c + 2 * f + i) - (a + 2 * d + g)) / (8 * dx)
    dz_dn = ((a + 2 * b + c) - (g + 2 * h + i)) / (8 * dy)  # top row is north
    slope = np.arctan(np.hypot(dz_de, dz_dn))
    aspect = np.mod(np.arctan2(-dz_de, -dz_dn), 2 * np.pi)
    return slope, aspect


def kappa(a, b):
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return {"kappa": float((po - pe) / (1 - pe)) if pe < 1 else 1.0, "r_index_pixels": int(a.sum()),
            "qhantar_pixels": int(b.sum()), "both": int((a & b).sum()), "n_pixels": int(a.size)}


def main(res_dir):
    dem, tr = read(res_dir, "dem_orthometric_m")
    lx, ly = read(res_dir, "los_east")[0], read(res_dir, "los_north")[0]
    theta = np.deg2rad(read(res_dir, "incidence_deg")[0])
    lay, sha = read(res_dir, "layover")[0].astype(bool), read(res_dir, "shadow")[0].astype(bool)
    state, reason = read(res_dir, "state")[0], read(res_dir, "reason")[0]
    S = read(res_dir, "sensitivity_S")[0]

    alpha, beta = horn(dem, tr.a, -tr.e)
    phi = np.mod(np.arctan2(lx, ly) + np.pi, 2 * np.pi)  # LOS points target -> sensor; look direction is opposite
    arg = theta + np.arctan(np.tan(alpha) * np.cos(phi - beta))
    R = np.sin(arg)

    use = (state != 255) & (reason != 3) & np.isfinite(R) & np.isfinite(dem)
    r_lay = R < 0
    r_sha = arg > np.pi / 2
    r_cls = np.select([r_lay, r_sha, R < np.sin(theta)], [0, 1, 2], default=3)

    k_lay, k_sha = kappa(r_lay[use], lay[use]), kappa(r_sha[use], sha[use])
    cross = {}
    for s, sn in STATES.items():
        m = use & (state == s)
        cross[sn] = {R_CLASSES[c]: float((r_cls[m] == c).mean()) if m.any() else None for c in range(4)}
    m_ok = use & ~lay & ~sha & np.isfinite(S)
    rank = lambda v: np.argsort(np.argsort(v))
    rho = float(np.corrcoef(rank(R[m_ok]), rank(np.abs(S[m_ok])))[0, 1])
    good = (r_cls == 3) & m_ok
    good_low_s = float((np.abs(S[good]) < 0.3).mean())
    # control: same R-index on QHANTAR's own slope/aspect isolates the DEM-derivative effect
    a_q, b_q = np.deg2rad(read(res_dir, "slope_deg")[0]), np.deg2rad(read(res_dir, "aspect_deg")[0])
    arg_q = theta + np.arctan(np.tan(a_q) * np.cos(phi - b_q))
    ctrl = {"layover_kappa": kappa((np.sin(arg_q) < 0)[use], lay[use])["kappa"],
            "active_shadow_kappa": kappa((arg_q > np.pi / 2)[use], sha[use])["kappa"]}

    h2 = {
        "hypothesis": "QHANTAR's layover/shadow flags agree with an independent R-index implementation "
                      "(Cohen's kappa >= 0.8 for both flags, criterion fixed before running).",
        "r_index_formula": "R = sin{theta + arctan[tan(slope) * cos(phi - aspect)]}, phi = look azimuth "
                           "(Notti et al. 2010, 2014; as in Remote Sens. 2021, 13, 1938, eq. 1)",
        "independence": "slope/aspect recomputed with Horn's 3x3 method; no code shared with qhantar.engine",
        "layover_agreement": k_lay,
        "active_shadow_agreement": k_sha,
        "control_same_slope_aspect_as_qhantar": ctrl,
        "r_class_fraction_by_state": cross,
        "spearman_R_vs_absS_valid_geometry": rho,
        "fraction_of_R_good_visibility_with_absS_below_0_3": good_low_s,
        "verdict": "consistent" if k_lay["kappa"] >= 0.8 and k_sha["kappa"] >= 0.8 else "differ",
        "reading": "R scores how the slope is imaged (pixel compression); |S| scores how much downhill motion "
                   "projects on the LOS. They answer different questions, so pixels with good R-index visibility "
                   "can still be blind to downhill motion.",
        "limitations": ["the R-index layover condition and QHANTAR's range-plane condition are the same first-order "
                        "geometry, so agreement mostly tests implementation and the DEM-derivative choice",
                        "no passive layover or cast shadow in either model",
                        "R classes follow the 2021 paper's description; Notti et al. 2014 use their own class cut-offs",
                        "one scene, one pair"],
    }
    rj = Path(res_dir) / "results.json"
    r = json.loads(rj.read_text())
    r["h2"] = h2
    rj.write_text(json.dumps(r, indent=1))
    print(json.dumps(h2, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
