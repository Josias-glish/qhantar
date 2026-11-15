---
name: QHANTAR
description: A survey sheet of one NISAR observation over La Paz; knowing where to trust the radar, and where not.
colors:
  paper: "#ECEDE6"
  paper-hi: "#F5F6F1"
  paper-lo: "#E1E3DA"
  ink: "#1F2421"
  ink-2: "#4A524E"
  rule: "#8E928A"
  siena: "#9A4B2C"
  siena-hi: "#B35A36"
  ocre: "#C8A15A"
  pizarra: "#3F4D5C"
  contour: "#B9AE96"
  on-dark: "#F1F1EA"
typography:
  display:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(3rem, 7.5vw, 6rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "0.08em"
    fontVariation: "'wdth' 125"
  figure:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(3.4rem, 7vw, 6rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.01em"
    fontFeature: "'tnum'"
    fontVariation: "'wdth' 125"
  headline:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(2rem, 4.2vw, 3.4rem)"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "0.02em"
    fontVariation: "'wdth' 125"
  lede:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(1.35rem, 2.4vw, 2.05rem)"
    fontWeight: 520
    lineHeight: 1.22
    letterSpacing: "-0.005em"
  title:
    fontFamily: "Archivo, Arial Narrow, system-ui, sans-serif"
    fontSize: "clamp(1.5rem, 2.4vw, 2.1rem)"
    fontWeight: 750
    lineHeight: 1.15
    fontVariation: "'wdth' 118"
  body:
    fontFamily: "Archivo, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 700
    lineHeight: 1.5
    letterSpacing: "0.14em"
    fontVariation: "'wdth' 120"
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "0.72rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0.04em"
rounded:
  none: "0px"
  hair: "2px"
spacing:
  gutter: "clamp(16px, 2.5vw, 32px)"
  plate-inset: "10px"
  cell: "0.6rem 0.9rem"
  section: "clamp(4rem, 12vh, 8rem)"
components:
  button-primary:
    backgroundColor: "{colors.siena}"
    textColor: "{colors.paper-hi}"
    rounded: "{rounded.hair}"
    padding: "0.7rem 1.15rem"
  button-primary-hover:
    backgroundColor: "{colors.siena-hi}"
    textColor: "{colors.paper-hi}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.hair}"
    padding: "0.7rem 1.15rem"
  button-secondary-hover:
    backgroundColor: "{colors.paper-lo}"
  choice-segment:
    backgroundColor: "{colors.paper-hi}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.35rem 0.65rem"
  choice-segment-on:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper-hi}"
  nav-tab:
    backgroundColor: "transparent"
    textColor: "{colors.ink-2}"
    padding: "0.55rem 0.9rem 0.45rem"
  nav-tab-on:
    textColor: "{colors.ink}"
  legend-cell:
    backgroundColor: "{colors.paper-hi}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.65rem 0.8rem"
  badge:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.12rem 0.5rem"
  note:
    backgroundColor: "{colors.paper-lo}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0.55rem 0.8rem"
  provenance-chip:
    backgroundColor: "rgba(14, 16, 15, 0.62)"
    textColor: "{colors.on-dark}"
    rounded: "{rounded.none}"
    padding: "0.35rem 0.7rem"
---

# Design System: QHANTAR

## Overview

**Creative North Star: "Hoja de puna"**

The site is a survey sheet of one radar observation. Every surface reads as part of a printed topographic sheet: a cool grey-green map paper, a thin black neatline doubled by an offset outline, legend cells ruled like a map margin, and provenance printed as marginalia beside the plate it describes. It deliberately refuses the dark mission-control look that satellite projects ship; the only dark field on the site is the AI hero, and it is dark because it is a photograph-like illustration, not because the brand is.

Density is low on the cover (one monumental figure per scroll beat) and moderate in the five map views, where a fixed 400px side margin carries text, controls and tables beside a full-height map. The voice is sober: wide, spaced Archivo capitals name the sheet; ordinary Archivo carries the reading; JetBrains Mono appears only where a surveyor would print machine strings (granule ids, EPSG, CRID).

Honesty is a visual rule, not only a copy rule. What is illustration is labelled as illustration on the image itself, what is data names its source on the image itself, and the switch between the two is drawn from the real terrain.

**Key Characteristics:**
- Cool map paper ground with a faint, slowly breathing contour field behind everything.
- Neatlines: 1px pizarra or ink border plus a 1px outline offset 3 to 5px; 3px double rules for sheet margins.
- One action colour (siena), one marker colour (ocre), one structure colour (pizarra).
- Data colours come from `results.json` and live only inside data: plates, swatches, bars, colour ramps.
- Square corners everywhere except a 2px softening on buttons.
- Scroll-scrubbed cover with a DEM-driven contour handover; static, fully legible fallback behind five media gates.

## Colors

A muted highland sheet: grey-green paper, near-black green ink, one earth red for action, one dry-grass ochre for marking, one slate blue for structure.

### Primary
- **Siena** (siena): the action colour. Primary buttons ("Open the map" in the header and the cover's caption bands and close), the download link, the active nav underline and the nav step numbers, focus rings, slider accent, and the moving contour edge of the handover wipe. Hover deepens to **Siena Light** (siena-hi).

### Secondary
- **Pizarra** (pizarra): structure and reference. Links, the outline of secondary buttons, neatlines around plates and the map, 3px double rules on the header, footer and section tables, table header underlines.

### Tertiary
- **Ocre** (ocre): the marker. Text selection and the dot in the provenance chip while it names an illustration. The dot turns to on-dark once the chip names real data.

### Neutral
- **Map Paper** (paper): page ground; badge fill.
- **Paper Light** (paper-hi): header, footer, side margin, legend cells, marginalia tables, choice segments; text on siena.
- **Paper Shade** (paper-lo): internal hairlines between rows and cells, note fill, plate ground under the grid, secondary button hover.
- **Ink** (ink): text; selected choice segment fill; legend cell neatline.
- **Ink Muted** (ink-2): secondary text, labels, captions, marginalia.
- **Rule Grey** (rule): hairline borders of badges, notes, choice segments and the language toggle.
- **Contour** (contour): the fixed contour field drawn behind the sheet (at 26 to 32% alpha, layer opacity 0.55 breathing to 0.25).
- **On Dark** (on-dark): text, neatline and chip text on the AI hero and on dark chips.

### Data colours (not UI colours)
State colours are read from `results.json` at runtime: 1 interpretable #0072B2, 2 visible but incoherent #D55E00, 3 coherent but low sensitivity #F0E442, 0 not observable or invalid #999999. Reason colours, connected-component colours and the matplotlib ramps (viridis, magma, RdBu_r, cividis, twilight, gray) likewise belong to the data.

### Named Rules
**The Data Ink Rule.** Data colours appear only inside data: map layers, plates, swatches, proportion bars and colour bars. They are never reused as UI colour, and UI colours never enter a data legend.

**The One Action Rule.** Siena is reserved for what can be acted on or is currently active (buttons, the download, the active tab, focus). It is never a fill for surfaces or a decoration for headings.

**The Cool Paper Rule.** The ground is grey-green map paper (#ECEDE6 family), never cream, never dark. Darkness exists only inside the AI hero.

## Typography

**Display Font:** Archivo, variable width axis (with Arial Narrow, system-ui)
**Body Font:** Archivo (with system-ui, -apple-system, Segoe UI)
**Label/Mono Font:** JetBrains Mono (with ui-monospace, Cascadia Mono, Consolas)

**Character:** One family stretched across its width axis does the whole job: at wdth 125 and 800 weight with open tracking it is the sheet title of a map; at normal width it is a plain, legible reading face. The monospace is a printer's marginalia, never a voice.

### Hierarchy
- **Display** (800, clamp 3 to 6rem, 0.95, wdth 125, +0.08em): the sheet title QHANTAR on the cover. The header mark repeats it small (1.25rem, +0.16em).
- **Figure** (800, clamp 3.4 to 6rem, 0.95, wdth 125, tabular): the one monumental number per handover beat, formatted in the UI locale.
- **Headline** (800, clamp 2 to 3.4rem, wdth 125, +0.02em, max 20ch): cover section titles; the passport title uses the same face at clamp 1.6 to 2.4rem, +0.06em.
- **Lede** (520, clamp 1.35 to 2.05rem, 1.22, max 26ch): the hero question and caption bands.
- **Title** (750, clamp 1.5 to 2.1rem, wdth 118): beat titles; side-margin view titles at 1.45rem.
- **Body** (400, 1rem, 1.5): reading text, 44 to 70ch in the cover, the 400px margin in views.
- **Label** (650 to 700, 0.72 to 0.78rem, uppercase, +0.12 to 0.14em): legend titles, table headers, marginalia keys, side-margin h3, badges, figure captions.
- **Mono** (400, 0.72 to 0.78rem, +0.04em): granule ids, CRID, EPSG and grid spacing, nav step numerals, colour-bar ticks.

### Named Rules
**The Marginalia Mono Rule.** JetBrains Mono is used only for machine strings a survey sheet prints in its margin: granule ids, CRID, EPSG, grid spacing, tick values. Never for headings, buttons or prose.

**The Locale Number Rule.** Every number is formatted with the UI locale (es-BO decimal comma in Spanish, en-US in English) and set with tabular figures in tables and figures. Phase is labelled and shown in radians, never converted to displacement.

## Layout

The sheet has a top margin (header, paper-hi, closed by a 3px double pizarra rule) and a bottom margin (footer, same treatment). Horizontal gutter is clamp(16px, 2.5vw, 32px).

The five views share one split: map on the left, a fixed 400px side margin on the right, collapsing to one column under 960px with the map at 58vh and the legend dock moved under it. The map sits inset 10px inside its region with an offset outline, so it reads as a plate with a neatline. The passport is a two-column sheet capped at 1240px.

The cover is a vertical story: a 420vh scroll-scrubbed hero with a sticky 100vh stage, a 560vh handover with a sticky stage that pairs the plate (1.35fr) with the beat text (1fr), then three sections capped at 1120px with section padding clamp(4rem, 12vh, 8rem).

**The Five Gates Rule.** The scroll-scrubbed hero turns into a static, fully set hero under any of five media gates: max-width 720px; portrait up to 1024px; portrait coarse pointer; landscape coarse pointer under 560px tall; prefers-reduced-motion. The gate strings are identical in CSS and in Cover.tsx and must stay so. Under 960px the handover shows the final real layer with the NISAR label and stacks its beats.

## Elevation & Depth

Flat. Depth on the sheet comes from rules, not shadows: a 1px border doubled by a 1px outline offset 3 to 5px (legend cells, plates, the map, marginalia), and 3px double rules for margins. The only shadow is a layered text shadow on hero captions for legibility over the illustration, and the only blur is the provenance chip's backdrop on the hero.

### Shadow Vocabulary
- **Hero caption legibility** (`text-shadow: 0 1px 2px rgba(10,12,11,0.9), 0 3px 12px rgba(10,12,11,0.7), 0 10px 40px rgba(10,12,11,0.6)`): hero caption bands only; removed from buttons inside them.

### Named Rules
**The Neatline Rule.** A framed thing gets a neatline (border plus offset outline), never a drop shadow or a card lift.

## Shapes

Square. Legend cells, plates, notes, badges, chips, tables and segmented choices have no radius; buttons and the language toggle soften to 2px. Segmented choices share borders (−1px overlap) like ruled cells. Round shapes appear only for the chip's 7px dot and the video-loading ring. List markers in the "is not" list are short 0.85rem rules, not glyphs.

## Components

### Buttons
- **Shape:** near-square (2px).
- **Primary:** siena fill, paper-hi text, 600 weight, +0.02em, padding 0.7rem 1.15rem; small variant 0.45rem 0.8rem at 0.88rem in the header.
- **Hover / Focus:** hover to siena-hi over 0.35s ease-out; active nudges 1px down; focus is a 2px siena outline offset 3px.
- **Secondary:** transparent with a 1px pizarra border and ink text; hover fills paper-lo.
- **Touch:** 44px minimum height on coarse pointers.

### Chips
- **Provenance chip:** translucent dark (rgba(14,16,15,0.62)) with a hairline on-dark border, 8px backdrop blur, 0.78rem, ocre dot. It sits on the image it describes: bottom-left of the hero, bottom-left of the handover plate.
- **State:** names "AI-generated illustration · not data" while any illustration pixel remains; once the wipe completes it names the Copernicus GLO-30 DEM on the relief beats and "Real NISAR data" only on the coherence, |S| and state beats. The dot turns from ocre to on-dark when it names data.
- **Badge:** square label-type tag with a rule border on paper; the "Real NISAR data · PROVISIONAL" variant takes a pizarra border.

### Cards / Containers
- **Legend cell:** paper-hi, 1px ink border plus 1px ink outline offset 3px, square, padding 0.65rem 0.8rem, settles in over 0.6s. Title in label type over a paper-lo hairline.
- **Note:** paper-lo fill, rule border, square. For caveats (prior work, phase in radians, slow motion).
- **Marginalia table:** two-column definition grid with pizarra neatline and offset outline, label-type keys, paper-lo row hairlines.
- **Facts list:** the same grid without the frame, inside the side margin.

### Inputs / Fields
- **Segmented choice:** radio inputs rendered as ruled cells (rule border, paper-hi), selected cell inverts to ink with paper-hi text; focus-within draws the siena ring.
- **Slider:** native range with siena accent, labelled in ink-2.

### Navigation
- **Header:** brand mark (wide caps) with tagline, the real-data badge outside the cover, the language toggle, and on the cover a small primary "Open the map".
- **View tabs:** five numbered tabs (mono siena numerals), ink-2 at rest, ink and 650 weight when active, with a 3px siena underline that scales in from the left over 0.45s. Separated by paper-lo hairlines; scroll horizontally on narrow screens.
- **On the cover:** the header floats over the hero on a top-down dark gradient with on-dark text and no rule.

### The handover plate (signature)
A plate with a pizarra neatline over a 40px pizarra grid on paper-lo. The AI ending frame is painted on a canvas and drains away along the real La Paz DEM (`lapaz_elevation.png`, same grid as the hillshade), lowest ground first, levelled by area so the wipe advances evenly; the moving edge is the true contour line drawn in siena. Under it the real hillshade, then coherence, |S| and the state map fade in one per beat at 0.9 opacity. Mono marginalia below the plate print "NISAR L2 GUNW · CRID · maturity" and "EPSG · spacing".

### Motion
Two easings: ease-out cubic-bezier(0.16, 1, 0.3, 1) for state changes and entrances, ease-in-out cubic-bezier(0.65, 0, 0.35, 1) for loops. Entrances rise 6 to 18px and settle with 60 to 120ms staggers, once. Hero words reveal by per-word thresholds tied to scroll. Under prefers-reduced-motion every animation and transition is removed and all content is set at rest; loops pause on hidden tabs.

## Do's and Don'ts

### Do:
- **Do** label any illustrative image on the image itself, in the footer and in its file metadata; the AI hero carries "AI-generated illustration · not data" on screen.
- **Do** name the actual source on each layer's chip: the DEM on relief, NISAR only on NISAR layers, and switch away from "illustration" only when no illustration pixel remains.
- **Do** frame plates, maps, legends and marginalia with a neatline (1px border plus 1px outline offset 3 to 5px) and close sheet margins with a 3px double pizarra rule.
- **Do** format numbers in the UI locale (es-BO decimal comma) with tabular figures, and show phase in radians.
- **Do** keep the five static-hero gate strings identical in CSS and script.

### Don't:
- **Don't** reuse the state colours (#0072B2, #D55E00, #F0E442, #999999) or any data ramp as UI colour.
- **Don't** use siena for surfaces, headings or decoration; it marks actions and the active state.
- **Don't** print coordinates, grid or EPSG on the AI hero; located marginalia start at the real plate.
- **Don't** set headings, buttons or prose in JetBrains Mono.
- **Don't** use drop shadows, card lifts or rounded containers; depth is ruled, corners are square.
- **Don't** move to a dark or cream ground outside the hero.
