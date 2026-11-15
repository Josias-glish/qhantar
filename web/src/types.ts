// Shape of results.json written by scripts/process_scene.py and scripts/h1.py (only the fields the web reads).
export type Corners = [[number, number], [number, number], [number, number], [number, number]];

export interface Stats { n: number; median: number; p25: number; p75: number }
export interface Fractions { n_pixels: number; fractions: Record<string, number>; counts: Record<string, number> }
export interface H1Group {
  n_pixels: number; coherence_median: number | null; coherence_iqr: [number, number] | null;
  coherence_missing_fraction: number | null; invalid_component_fraction: number | null;
}

export interface Results {
  generated_utc: string;
  provenance: {
    granule: string; source: string; collection: string; download_url: string; doi: string; crid: string;
    maturity: string; maturity_note: string; reference_acquisition: [string, string];
    secondary_acquisition: [string, string]; orbit_pass: string; look_direction: string; track: number;
    frame: number; frequency: string[]; polarization: string; product_processing_utc: string;
    grid: { epsg: number; spacing_m: number; shape: [number, number] };
    dem: { name: string; source: string; tiles: string[]; resampling: string; vertical: string };
  };
  parameters: { s_min: number; coh_min: number; slope_min_deg: number; connected_component_invalid_value: number; validity: string };
  fractions: Record<"scene_footprint" | "la_paz_crop", { states: Fractions; reasons: Fractions }>;
  quality: { coherence_in_valid: Stats; abs_S_in_valid: Stats; slope_deg_in_valid: Stats };
  colors: { state: Record<string, string>; reason: Record<string, string> };
  web_layers: Record<string, { file: string; corners: Corners; colormap: string; range: [number, number] | null }>;
  h1: null | {
    groups: Record<string, H1Group>; verdict: string; lower_median_coherence: boolean;
    higher_invalid_component_fraction: boolean; limitations: string[];
    slope_matched_check?: { valid_reweighted: { coherence_median: number; invalid_component_fraction: number } };
  };
  h2?: { layover_agreement: { kappa: number }; active_shadow_agreement: { kappa: number }; verdict: string };
  h3?: Record<"A_constant_heading_constant_incidence" | "B_constant_heading_per_pixel_incidence", { state_changed_fraction: number }>;
  h4?: { status: string; inventory: { name: string; events_in_la_paz_crop: number } };
}
