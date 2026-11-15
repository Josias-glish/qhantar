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

    d, v = groups["layover_or_shadow"], groups["geometrically_valid"]
    lower_coh = d["coherence_median"] < v["coherence_median"]
    more_cc0 = d["invalid_component_fraction"] > v["invalid_component_fraction"]
    verdict = ("supported" if lower_coh and more_cc0 else "not supported" if not lower_coh and not more_cc0
               else "partially supported")
    h1 = {"hypothesis": "Pixels flagged as layover or shadow have lower median coherence and a higher fraction of "
                        "connected component 0 than geometrically valid pixels.",
          "groups": groups, "lower_median_coherence": bool(lower_coh), "higher_invalid_component_fraction": bool(more_cc0),
          "verdict": verdict,
          "group_definition": "radar footprint, not water, both subswaths valid, DEM and LOS available; split by the "
                              "model's layover/shadow flags only. Coherence and components not used for grouping.",
          "limitations": ["one scene, one interferometric pair (12 days, PROVISIONAL P05023)",
                          "first-order single-pixel layover/shadow model, no passive layover or cast shadow",
                          "layover and shadow groups are small relative to the valid group",
                          "no significance test: descriptive comparison only"]}
    rj = Path(res_dir) / "results.json"
    r = json.loads(rj.read_text())
    r["h1"] = h1
    rj.write_text(json.dumps(r, indent=1))
    print(json.dumps(h1, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
