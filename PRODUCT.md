# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: the NASA Space Apps Challenge 2026 jury, watching a team member run a live demo of the web app
(challenge "Dancing with the SARs"). They need to understand in seconds what QHANTAR does and what it does
not do, then follow the five views. Secondary: InSAR researchers and analysts who open the public link later
and check the method and provenance.

## Product Purpose

QHANTAR takes one real NISAR L2 GUNW interferogram over La Paz, Bolivia, crosses it with a DEM and labels every
pixel with one of four states: interpretable, visible but incoherent, coherent but low sensitivity, not
observable or invalid. It answers: where could this specific radar observation see downhill slope motion, and
where not. Success: the jury leaves knowing that a missing InSAR signal in mountains does not always mean no
motion.

## Positioning

The slope/LOS sensitivity idea is prior work (Notti et al. 2010, van Natijne et al. 2022). QHANTAR applies it
a posteriori to one concrete NISAR pair, with the product's own native LOS vectors and its measured coherence
and connected components, as a reproducible four-state classification. It is a differentiation hypothesis, not
a novelty claim.

## Operating Context

Live jury demo on a laptop and projector, then a public link (Vercel). Five views: mission, mountain, radar
evidence, slope-LOS observability, evidence passport. Bilingual ES/EN with hash deep links.

## Capabilities and Constraints

- Every number shown comes from `results/<scene>/results.json`; nothing is hard-coded or invented.
- No synthetic data presented as real. Illustrative material must be labelled as such.
- Phase, coherence, sensitivity and masks stay separate layers; never merged into one score.
- Phase shown in radians, never as displacement.
- Not a landslide detector, not a risk index, not a displacement measurement.
- Provenance (granule, dates, CRID P05023 PROVISIONAL, DOI) visible on every result.
- Static site: React 19 + TypeScript + Vite + MapLibre GL; OSM basemap.

## Brand Commitments

Name QHANTAR. Tagline used in the docs: "knowing where to trust the radar, and where not". Sober, honest,
scientific voice; no hype, no novelty claims.

## Evidence on Hand

Real NISAR GUNW-derived web layers in `results/<scene>/web/` (hillshade, slope, aspect, phase, coherence,
connected components, |S|, four-state map, reason) for La Paz and the full footprint; `results.json` with
fractions, quality, H1 and provenance; screenshots in `docs/screenshots/`. No user testimonials, no
validation with users, H2-H4 pending: never imply otherwise.

## Product Principles

1. Show the evidence, not a verdict.
2. Every figure traceable to `results.json`.
3. Say what it is not as loudly as what it is.
4. Negative and partial results are shown, not hidden.

## Accessibility & Inclusion

Colour-blind-safe state palette (already in results.json colours); bilingual ES/EN; keyboard-reachable controls;
respect reduced motion.
