# AI usage statement

QHANTAR's foundational document (`docs/master-document.es.md`) commits the team to declare which
AI tools were used, for which tasks, and what the human team verified. This file does that.

## Claude (Anthropic, Claude Code, model Claude Opus 5.5)

A team member gave Claude a written brief: build QHANTAR from scratch following the master
document. Claude worked in a local terminal on this repository, with three mandatory human
checkpoints. Everything below was done by Claude:

- **Scene search.** Searched the ASF catalogue for NISAR GUNW products over La Paz and recorded the
  search result (`docs/search-record.json`). The team member chose the ascending scene.
  The 2.28 GB download ran in the team member's own logged-in browser session. Claude never saw
  or stored Earthdata credentials, and checked the file size against the ASF record.
- **Product inspection.** Wrote `scripts/inspect_gunw.py` and generated `docs/product-inspection.md`.
- **Engine and tests.** Wrote `qhantar/engine.py` and the 20 analytical tests in
  `tests/test_engine.py`. Wrote `docs/conventions.md`.
- **Processing.** Wrote `scripts/process_scene.py` and `scripts/h1.py`, and ran them on the real scene.
  Added the consistency checks stored in `results.json`. Found and fixed one bug on the first run:
  the radar footprint was wrongly built from the water digit of the mask.
- **H1.** Defined the groups from geometry and the product mask only, ran the comparison, and wrote
  `docs/validation-h1.md`. That includes the steep-slope confound, which weakens the headline result.
- **Web app.** Wrote the React + TypeScript + Vite + MapLibre site in `web/`. Checked it in headless
  Chromium: 5 views in 2 languages, no console errors, and every visible number compared by script
  with `results.json`. Took the screenshots in `docs/screenshots/`.
- **Documentation.** Wrote:
  - `README.md`
  - `docs/method.md`
  - `docs/DECISIONS.md`
  - `docs/STATUS.md`
  - `docs/pitch.md`
  - `docs/submission.md`
  - this file

  The two literature references were checked against the publisher page and Crossref.
- **Reproducibility.** Ran the README commands from a clean clone, which exposed a Windows path-length
  bug that was then fixed. Packaged the ZIP.

- **Cover page and visual redesign.** On the team member's request, used two Claude Code skills (impeccable, 10k-websites) to restyle the site and add a scroll-driven cover. Generated the cover illustration with the **Higgsfield** connector: one start image (GPT Image 2.6) and one 6-second video (Kling 4.0, chosen by the team member), 22.25 credits in total, each price shown before spending. The team member approved the image, the video and the palette. The illustration is labelled as AI-generated on screen and is never used as data.

Claude did **not**:

- validate the results with real users or domain experts;
- compare against the R-index (H2), the heading/incidence approximation (H3) or known active zones of La Paz (H4);
- review competitors beyond table 4.3 of the master document.

**Human checkpoints.** The team member made these decisions in the conversation with Claude:

- approved the download of the ascending scene;
- reviewed the first real map and told Claude to continue with the default thresholds;
- will approve the name and content of the public repository before it is published.

## ChatGPT (OpenAI)

> **TO BE COMPLETED BY THE TEAM.** Which tasks (for example: the foundational document, the
> competitor review, the pitch), which dates or versions, and what was kept or discarded.

## Antigravity (Google)

> **TO BE COMPLETED BY THE TEAM.** Which tasks, which parts of earlier prototypes, and whether any
> of that code is in this repository (none of the code in this repository came from it in the
> session described above).

## What the human team verified

> **TO BE COMPLETED BY THE TEAM.** List only checks a person actually performed, for example:
> read the method and conventions, re-ran the tests, opened the map and compared it with local
> knowledge of La Paz, checked the citations. Do not list a check that was not done.
