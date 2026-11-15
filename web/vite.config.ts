import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Relative base: the static build works under any GitHub Pages path.
// MapLibre GL alone is ~1 MB minified; one chunk is fine for a single-page static site.
export default defineConfig({ plugins: [react()], base: "./", build: { chunkSizeWarningLimit: 1400 } });
