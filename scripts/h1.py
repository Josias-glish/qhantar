"""H1: do pixels the model flags as layover/shadow show lower coherence and more invalid
connected components than geometrically valid pixels?

Groups are built from geometry and the product's own footprint/water/subswath mask only.
Coherence and connected components are NOT used to build or filter the groups.

Usage: python scripts/h1.py data/raw/<granule>.h5 results/<scene folder>
"""
import json
import sys
from pathlib import Path

import h5py
import numpy as np
import rasterio

MASK = "/science/LSAR/GUNW/grids/frequencyA/unwrappedInterferogram/mask"


def read(d, name):
    with rasterio.open(Path(d) / "full" / f"{name}.tif") as src:
        return src.read(1)


def summary(sel, coh, cc):
    c = coh[sel]
    fin = np.isfinite(c)
    return {"n_pixels": int(sel.sum()),
            "coherence_median": float(np.median(c[fin])) if fin.any() else None,
            "coherence_iqr": [float(np.percentile(c[fin], 25)), float(np.percentile(c[fin], 75))] if fin.any() else None,
            "coherence_missing_fraction": float(1 - fin.mean()) if sel.any() else None,
            "invalid_component_fraction": float((cc[sel] == 0).mean()) if sel.any() else None}


def wmedian(x, w):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return float(x[o][np.searchsorted(c, c[-1] / 2)])


def matched(distorted, valid, slope, coh, cc, width=5.0):
    """Valid pixels reweighted so their slope distribution (bins of `width` deg) matches the distorted group."""
    bins = np.floor(slope / width)
    db, dn = np.unique(bins[distorted], return_counts=True)
    vb = bins[valid]
    vc, vh, wv = coh[valid], cc[valid], np.zeros(vb.size)
    for b_, n in zip(db, dn):
        sel = vb == b_
        if sel.any():
            wv[sel] = n / sel.sum()
    fin = np.isfinite(vc) & (wv > 0)
    per_bin = []
    for b_, n in zip(db, dn):
        sd, sv = distorted & (bins == b_), valid & (bins == b_)
        if n >= 100 and sv.sum() >= 100:
            per_bin.append({"slope_deg": [float(b_ * width), float((b_ + 1) * width)], "n_distorted": int(n), "n_valid": int(sv.sum()),
                            "coherence_median": [float(np.nanmedian(coh[sd])), float(np.nanmedian(coh[sv]))],
                            "invalid_component_fraction": [float((cc[sd] == 0).mean()), float((cc[sv] == 0).mean())]})
    return {"method": f"valid pixels reweighted to the slope distribution of the layover/shadow group, {width:g} deg bins",
            "distorted_pixels_without_valid_counterpart": int(dn[~np.isin(db, vb)].sum()),
            "valid_reweighted": {"coherence_median": wmedian(vc[fin], wv[fin]),
                                 "invalid_component_fraction": float((wv * (vh == 0)).sum() / wv.sum())},
            "per_bin_pairs_layover_shadow_vs_valid": per_bin,
            "bins_with_lower_coherence": sum(b["coherence_median"][0] < b["coherence_median"][1] for b in per_bin),
            "bins_with_more_component_0": sum(b["invalid_component_fraction"][0] > b["invalid_component_fraction"][1] for b in per_bin),
            "bins_compared": len(per_bin)}


def main(gunw, res_dir):
    with h5py.File(gunw, "r") as f:
        m = f[MASK][()]
    low = (m & 0xFF).astype(np.int64)
    base = (m != 255) & ((low // 10) % 10 > 0) & (low % 10 > 0) & ((low // 100) != 1)  # radar data, not water
    lay, sha = read(res_dir, "layover").astype(bool), read(res_dir, "shadow").astype(bool)
    slope = read(res_dir, "slope_deg")
    geom_ok = base & np.isfinite(slope) & np.isfinite(read(res_dir, "los_east"))
    coh, cc = read(res_dir, "coherence"), read(res_dir, "connected_components")

    distorted = geom_ok & (lay | sha)
    valid = geom_ok & ~lay & ~sha
    groups = {"layover_or_shadow": summary(distorted, coh, cc),
              "layover_only": summary(geom_ok & lay, coh, cc),
              "shadow_only": summary(geom_ok & sha, coh, cc),
              "geometrically_valid": summary(valid, coh, cc)}
    # context, not the hypothesis test: steep slopes decorrelate for other reasons too
    groups["context_geometrically_valid_slope_ge_30deg"] = summary(valid & (slope >= 30), coh, cc)

    slope_matched = matched(distorted, valid, slope, coh, cc)

    d, v = groups["layover_or_shadow"], groups["geometrically_valid"]
    lower_coh = d["coherence_median"] < v["coherence_median"]
    more_cc0 = d["invalid_component_fraction"] > v["invalid_component_fraction"]
    verdict = ("supported" if lower_coh and more_cc0 else "not supported" if not lower_coh and not more_cc0
               else "partially supported")
    h1 = {"hypothesis": "Pixels flagged as layover or shadow have lower median coherence and a higher fraction of "
                        "connected component 0 than geometrically valid pixels.",
          "groups": groups, "lower_median_coherence": bool(lower_coh), "higher_invalid_component_fraction": bool(more_cc0),
          "verdict": verdict,
          "slope_matched_check": slope_matched,
          "group_definition": "radar footprint, not water, both subswaths valid, DEM and LOS available; split by the "
                              "model's layover/shadow flags only. Coherence and components not used for grouping.",
          "limitations": ["one scene, one interferometric pair (12 days, PROVISIONAL P05023)",
                          "first-order single-pixel layover/shadow model, no passive layover or cast shadow",
                          "layover and shadow groups are small relative to the valid group",
                          "no significance test: descriptive comparison only",
                          "the verdict uses the pre-registered unmatched comparison; the slope-matched check is reported "
                          "next to it, not instead of it"]}
    rj = Path(res_dir) / "results.json"
    r = json.loads(rj.read_text())
    r["h1"] = h1
    rj.write_text(json.dumps(r, indent=1))
    print(json.dumps(h1, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
