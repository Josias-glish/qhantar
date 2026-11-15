---
version: 1
slug: "web-src-app-tsx"
primary_target: "web/src/App.tsx"
related_targets: []
---

Scope: web/ (cover page + the five views). Visitor mode: Persuade on the cover (jury, live demo), Operate in the five views.
Audience: Space Apps jury watching a live demo; later researchers via the public Vercel link.
Action: understand what QHANTAR does and does not do in seconds, then open the interactive map.
Proof: only real NISAR-derived layers and results.json figures. The hero video is an AI-generated illustration and is labelled as such on screen.
Constraints: PRODUCT.md (no synthetic data as real, phase in radians, layers separate, provenance visible).

## Direction contract

THESIS: The site is a survey sheet of one observation. It refuses the dark-space mission-control look every satellite project ships; the jury reads a map sheet with a neatline, a legend and a margin that states where each layer came from.

OWN-WORLD: Cool grey-green map-paper ground (never cream), contour brown linework, survey red for the active route and selection, lake blue for links, hypsometric tints for depth. Thin black neatline with graticule ticks frames every surface. Archivo Expanded spaced caps for sheet titles, Archivo for body, JetBrains Mono only for coordinates and granule ids. Legend boxes are ruled map-margin cells, not cards.

STORY: Descend (illustration) onto a mountain slope; at the boundary the illustration hands over to the real hillshade of La Paz; real layers stack one per scroll beat (relief, coherence, |S|, four states) with their figures; what it is not; open the map.

FIRST VIEWPORT: Full-bleed scroll-scrubbed descent inside a neatline frame. Sheet title QHANTAR top-left at display scale, one-line question beneath, coordinates on the frame edges, map note "AI-generated illustration, not data" bottom-left, primary action "Open the map" bottom-right in survey red.

FORM: topographic survey sheet, candidate 1 of my ordered list (user chose the pick over assigned candidate 7); seed a0a15d56. Raises: one ink per evidence layer (risograph discipline); provenance printed inline as sheet marginalia (terminal discipline); one monumental figure per beat (command-wall discipline).

Signature interaction: the illustration-to-data handover, a contour wipe where the AI frame is replaced by the real hillshade with the label switching from "illustration" to "NISAR data".

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Amendments (build, 2026-11-15)

- FIRST VIEWPORT, coordinates: none on the hero frame. The hero is an AI illustration of no real place; printing coordinates on it would present it as a located observation. Real coordinates and grid (EPSG, spacing, CRID) appear as marginalia from the handover plate on, where the imagery is real.
- FIRST VIEWPORT, primary action: "Open the map" sits in the sheet's top margin (header, siena) from the first frame and again in the last caption band, so it is reachable at any scroll depth; the bottom margin carries the AI note and the scroll cue.
- Signature: the contour wipe is a true contour wipe. The illustration drains along the real La Paz DEM (`lapaz_elevation.png`, same grid as the hillshade), valley floor first, with the moving edge drawn as the actual contour line in siena.

