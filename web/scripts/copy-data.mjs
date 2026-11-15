// Copy the processed results (PNGs + results.json) into public/data for the static site.
// public/data is a generated copy (git-ignored); results/ is the source of truth.
import { cpSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { join } from "node:path";

const root = join(import.meta.dirname, "..", "..", "results");
// the site shows the primary (ascending) scene; the descending one is compared in docs/ (scripts/two_orbits.py)
const scene = process.env.QHANTAR_SCENE || "T118_A_F169_20261008_20261020_P05023";
const granules = readdirSync(root, { withFileTypes: true }).filter((d) => d.isDirectory() && d.name === scene);
if (granules.length !== 1) throw new Error(`processed scene ${scene} not found in results/`);
const src = join(root, granules[0].name);
const dst = join(import.meta.dirname, "..", "public", "data");
rmSync(dst, { recursive: true, force: true });
mkdirSync(dst, { recursive: true });
cpSync(join(src, "web"), dst, { recursive: true });
cpSync(join(src, "results.json"), join(dst, "results.json"));
console.log(`copied ${granules[0].name} -> public/data`);
