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

A real test of H4 would need outlines of slopes known to be moving around October 2026. The municipal
scarp map below is the best inventory found, and it gives a more useful picture than the catalogue.

## Second inventory: GAMLP landslide scarps (added 2026-11-15)

The municipality's *Mapa de Escarpe de Deslizamiento en el Municipio de La Paz* (Oficialía Mayor de
Planificación para el Desarrollo, GAMLP, 2013; published on GeoBolivia, downloaded from its archive.org
mirror because geo.gob.bo did not resolve; MD5 `6071f5fcfef6994146d8c4a25f482751`) maps 1,026 scarps as lines.
That is metre-scale mapping, so it can be compared with 80 m pixels. The file is not committed; the
script takes it as an optional third argument.

The scarps were burned onto the 80 m grid (every pixel a line touches: 2,599 pixels). They are compared
with all other footprint pixels inside the scarps' bounding box (35,377 pixels), raw and reweighted to the
same slope distribution (5° bins). Median slope: 15.7° on scarps, 14.9° elsewhere in the box.

| | 1 Interpretable | 2 Visible, incoherent | 3 Coherent, low sens. | 0 Not observable |
| --- | ---: | ---: | ---: | ---: |
| Scarp pixels | 61.8 % | 2.4 % | 35.5 % | 0.3 % |
| Rest of the box | 52.3 % | 6.6 % | 35.0 % | 6.1 % |
| Rest of the box, same slopes | 54.5 % | 5.7 % | 37.8 % | 2.0 % |

**Reading.** In this ascending pair, the slopes where the municipality mapped landslide scarps are mostly
observable: 61.8 % interpretable and almost none (0.3 %) not observable. About a third (35.5 %) are coherent
but have |S| < 0.3, so a downhill motion there would barely show on this line of sight. For those slopes a
quiet interferogram does **not** mean stability. This answers the question H4 asked (do known active zones
fall in interpretable or in non-observable areas?) for one geometry. It is still not a validation: the scarps
date from 2013 and say nothing about motion between 8 and 20 October 2026.

## What this does not show

- The GAMLP scarps are lines from 2013 mapping, not outlines of landslides active in 2026.
- Events are points with stated accuracy, not landslide outlines.
- The events predate the 2026 acquisitions, so the pair cannot show those movements.
- A state mix is not a detection: QHANTAR does not detect landslides.
