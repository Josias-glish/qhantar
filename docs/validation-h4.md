# H4: known landslides of La Paz (context, not validation)

**Scene:** same GUNW as H1 to H3. Produced by `scripts/h4.py`; the numbers are stored under `h4` in
`results.json`, and the events used are in `docs/h4-glc-lapaz.csv`.

## Inventory

NASA Global Landslide Catalog export, `Global_Landslide_Catalog_Export_rows.csv`, from data.nasa.gov
(11,033 rows, MD5 `7e12dbd01cd937d7f3a68df0f3fcecce`, downloaded 2026-11-15). Cite: Kirschbaum et al. 2010,
*Natural Hazards* 52: 561–575; Kirschbaum, Stanley & Zhou 2015, *Geomorphology*,
doi:10.1016/j.geomorph.2015.03.016. The catalogue's live map service (`maps.nccs.nasa.gov`) no longer resolves.

Inside the La Paz crop the catalogue has **4 events**. They are points with a stated location accuracy,
not mapped outlines, so each one is drawn here as a disc with that radius.

## Result

Share of each state among the footprint pixels of each disc, next to the whole La Paz crop:

| Event | Date | Accuracy | Pixels | 1 Interpretable | 2 Visible, incoherent | 3 Coherent, low sens. | 0 Not observable |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| *Whole La Paz crop* | | | 420,046 | 35.5 % | 8.6 % | 23.6 % | 32.4 % |
| 3151 Irpavi II, Pampahasi, Callapa | 2011-02-26 | 10 km | 49,101 | 57.0 % | 4.1 % | 33.2 % | 5.6 % |
| 1457 Huanu Huanuni, Bella Vista | 2010-01-29 | 10 km | 49,083 | 49.2 % | 2.9 % | 31.0 % | 16.9 % |
| 987 "La paz city" ⚠ | 2009-02-18 | 10 km | 49,090 | 38.6 % | 6.4 % | 27.7 % | 27.4 % |
| 10773 Auquisamaña | 2017-02-15 | 1 km | 492 | 68.7 % | 0.4 % | 29.7 % | 1.2 % |

⚠ The source linked by event 987 reports evacuations of *barangays*, an administrative unit of the
Philippines. The event is probably La Paz, Philippines, geocoded to Bolivia. It is kept in the table because
it is what the catalogue says, and it is not used in any reading below.

## Reading

**H4 cannot be tested with this inventory.** The catalogue places events with 1 to 10 km uncertainty,
while a QHANTAR pixel is 80 m. A 10 km disc covers several valleys and the El Alto edge, so its state mix
says nothing about whether the slope that failed was observable.

The discs around the two credible 10 km events and the 1 km Auquisamaña event hold more interpretable
pixels than the crop as a whole (49.2 % to 68.7 %, against 35.5 %), and fewer "not observable" ones. The
reason is the terrain: flat ground, which QHANTAR marks as not observable, covers 29.9 % of the crop
(mostly the El Alto altiplano) but only 5.1 % (event 3151), 16.1 % (1457) and 1.2 % (10773) of those discs,
which sit on the steep valley sides of the city. That is a statement about terrain, not about landslides.

A real H4 needs mapped landslide outlines for La Paz, for example from the municipal risk maps or a
published inventory, ideally of slopes active around October 2026.

## What this does not show

- Only this catalogue was used; no municipal or published inventory.
- Events are points with stated accuracy, not landslide outlines.
- The events predate the 2026 acquisitions, so the pair cannot show those movements.
- A state mix is not a detection: QHANTAR does not detect landslides.
