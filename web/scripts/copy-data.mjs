// Copy the processed results (PNGs + results.json) into public/data for the static site.
// public/data is a generated copy (git-ignored); results/ is the source of truth.
import { cpSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { join } from "node:path";

const root = join(import.meta.dirname, "..", "..", "results");
const granules = readdirSync(root, { withFileTypes: true }).filter((d) => d.isDirectory());
if (granules.length !== 1) throw new Error(`expected exactly one processed granule in results/, found ${granules.length}`);
const src = join(root, granules[0].name);
const dst = join(import.meta.dirname, "..", "public", "data");
rmSync(dst, { recursive: true, force: true });
mkdirSync(dst, { recursive: true });
cpSync(join(src, "web"), dst, { recursive: true });
cpSync(join(src, "results.json"), join(dst, "results.json"));
console.log(`copied ${granules[0].name} -> public/data`);
