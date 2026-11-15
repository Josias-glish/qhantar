"""Ascending vs descending: where is a La Paz slope interpretable from one orbit only?

The descending state map is resampled (nearest) onto the ascending La Paz crop grid; only pixels
with a state in both orbits are compared. Writes "two_orbits" into the descending results.json.

Usage: python scripts/two_orbits.py results/<ascending> results/<descending>
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject


def main(asc, desc):
    asc, desc = Path(asc), Path(desc)
    with rasterio.open(asc / "geotiff" / "state.tif") as a:
        sa, prof = a.read(1), a.profile
    sd = np.full(sa.shape, 255, np.uint8)
    with rasterio.open(desc / "full" / "state.tif") as d:
        reproject(rasterio.band(d, 1), sd, dst_transform=prof["transform"], dst_crs=prof["crs"],
                  dst_nodata=255, resampling=Resampling.nearest)
    side = {}
    for k, p in (("ascending", asc), ("descending", desc)):
        with rasterio.open(p / "full" / "los_east.tif") as src:
            side[k] = "este" if np.nanmedian(src.read(1)) > 0 else "oeste"  # LOS points target -> sensor

    both = (sa != 255) & (sd != 255)
    ia, id_ = (sa == 1) & both, (sd == 1) & both
    n = int(both.sum())
    f = lambda m: float(m.sum() / n)
    t = {"method": "descending state resampled (nearest) to the ascending La Paz crop grid; pixels with a state in both orbits",
         "n_common_pixels": n,
         "interpretable_both": f(ia & id_),
         "interpretable_ascending_only": f(ia & ~id_),
         "interpretable_descending_only": f(id_ & ~ia),
         "interpretable_either": f(ia | id_),
         "interpretable_ascending": f(ia), "interpretable_descending": f(id_),
         "ascending_sensor_side_es": side["ascending"], "descending_sensor_side_es": side["descending"],
         "caveat": "different dates (12-day pairs, two weeks apart): coherence differences mix geometry and time"}
    pc = lambda x: f"{x * 100:.1f}".replace(".", ",") + " %"
    t["reading_es"] = (f"Con una sola órbita, la ascendente deja interpretable el {pc(t['interpretable_ascending'])} de estos píxeles "
                       f"y la descendente el {pc(t['interpretable_descending'])}. Sumando las dos se llega al {pc(t['interpretable_either'])}. "
                       f"Las fechas no coinciden, así que parte de la diferencia es coherencia y no solo geometría.")
    rj = desc / "results.json"
    r = json.loads(rj.read_text())
    r["two_orbits"] = t
    rj.write_text(json.dumps(r, indent=1))
    print(json.dumps(t, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
