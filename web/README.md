# QHANTAR web

Static bilingual (ES/EN) viewer for the processed scene. Every number it shows is read from
`results.json`; the map layers are the PNGs written by `scripts/process_scene.py`.

```bash
npm ci
npm run build      # copies ../results/<scene folder>/web/* and results.json into public/data, then builds dist/
npm run preview    # serves dist/ on http://localhost:4173
```

Views are addressable by URL hash, e.g. `#view=observability&lang=es&region=lapaz&layer=state&op=0.6`.
Basemap: OpenStreetMap standard tiles (no API key).
