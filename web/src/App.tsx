import { useEffect, useMemo, useState, type ReactNode } from "react";
import en from "./i18n/en.json";
import es from "./i18n/es.json";
import MapView, { type MapLayer } from "./MapView";
import Cover from "./Cover";
import type { Results } from "./types";

export type Lang = "en" | "es";
export type Dict = typeof en;
// acquisition [start, stop] as "YYYY-MM-DD hh:mm:ss → hh:mm:ss UTC" (the file stores nanoseconds)
const span = ([a, b]: string[]) => `${a.slice(0, 10)} ${a.slice(11, 19)} → ${b.slice(11, 19)} UTC`;
const utc = (s: string) => `${s.slice(0, 10)} ${s.slice(11, 19)}`;
const orb = (t: Dict, k: string) => (t.pv.orbit as Record<string, string>)[k] ?? k;
type View = "cover" | "mission" | "mountain" | "radar" | "observability" | "passport";
type Region = "lapaz" | "scene";

const DICTS: Record<Lang, Dict> = { en, es };
const VIEWS = ["mission", "mountain", "radar", "observability", "passport"] as const;
const ALL_VIEWS: View[] = ["cover", ...VIEWS];
const DATA = "./data/";

// Colour stops sampled from the matplotlib colormaps used to render the PNGs (scripts/process_scene.py).
const RAMPS: Record<string, string[]> = {
  viridis: ["#440154", "#472d7b", "#3b528b", "#2c728e", "#21918c", "#28ae80", "#5ec962", "#addc30", "#fde725"],
  magma: ["#000004", "#1d1147", "#51127c", "#832681", "#b73779", "#e75263", "#fc8961", "#fec488", "#fcfdbf"],
  RdBu_r: ["#053061", "#2a71b2", "#6bacd1", "#c2ddec", "#f7f6f6", "#fbccb4", "#e48066", "#ba2832", "#67001f"],
  cividis: ["#00224e", "#1a386f", "#434e6c", "#61656f", "#7d7c78", "#9b9476", "#bcae6c", "#dec958", "#fee838"],
  twilight: ["#e2d9e2", "#95b5c7", "#6276ba", "#592a8f", "#2f1436", "#741e4f", "#b25652", "#cca389", "#e2d9e2"],
  gray: ["#000000", "#404040", "#808080", "#c0c0c0", "#ffffff"],
};
const STATE_KEYS: Record<string, string> = {
  "1": "interpretable", "2": "visible_incoherent", "3": "coherent_low_sensitivity", "0": "not_observable_or_invalid",
};
const REASON_KEYS = ["interpretable", "visible_incoherent", "coherent_low_sensitivity", "nodata", "layover", "shadow",
  "flat", "invalid_component", "low_sensitivity_and_low_coherence"];

// ponytail: module-level locale, set by App before its children render; a context if views ever render outside App.
let LOC = "en-US";
const fmt = (x: number, d: number) => x.toLocaleString(LOC, { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (x: number | null | undefined) => (x == null ? "—" : `${fmt(x * 100, 1)} %`);
const num = (x: number | null | undefined, d = 3) => (x == null ? "—" : fmt(x, d));
const int = (x: number, lang: Lang) => x.toLocaleString(lang === "es" ? "es-BO" : "en-US");

function initialLang(): Lang {
  try {
    const saved = localStorage.getItem("qhantar-lang");
    if (saved === "en" || saved === "es") return saved;
  } catch { /* storage unavailable: fall through */ }
  return navigator.language.startsWith("es") ? "es" : "en";
}

function Swatch({ color }: { color: string }) {
  return <span className="swatch" style={{ background: color }} aria-hidden="true" />;
}

function ColorBar({ ramp, range, label }: { ramp: string; range: [number, number]; label: string }) {
  return (
    <div className="colorbar">
      <div className="legend-title">{label}</div>
      <div className="bar" style={{ background: `linear-gradient(to right, ${RAMPS[ramp].join(",")})` }} />
      <div className="bar-ticks"><span>{range[0].toLocaleString(LOC)}</span><span>{((range[0] + range[1]) / 2).toLocaleString(LOC)}</span><span>{range[1].toLocaleString(LOC)}</span></div>
    </div>
  );
}

function StateLegend({ r, t, region }: { r: Results; t: Dict; region: Region }) {
  const fr = r.fractions[region === "lapaz" ? "la_paz_crop" : "scene_footprint"].states.fractions;
  return (
    <div className="legend">
      <div className="legend-title">{t.obs.legend}</div>
      {(["1", "2", "3", "0"] as const).map((k) => (
        <div className="legend-row" key={k}>
          <Swatch color={r.colors.state[k]} />
          <div>
            <strong>{k} · {t.states[k]}</strong> <span className="muted">{pct(fr[STATE_KEYS[k]])}</span>
            <div className="small muted">{t.state_desc[k]}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ReasonLegend({ r, t, region }: { r: Results; t: Dict; region: Region }) {
  const fr = r.fractions[region === "lapaz" ? "la_paz_crop" : "scene_footprint"].reasons.fractions;
  return (
    <div className="legend">
      <div className="legend-title">{t.obs.reason}</div>
      {REASON_KEYS.map((key, i) => (
        <div className="legend-row" key={key}>
          <Swatch color={r.colors.reason[String(i)]} />
          <span>{t.reasons[String(i) as keyof Dict["reasons"]]} <span className="muted">{pct(fr[key])}</span></span>
        </div>
      ))}
    </div>
  );
}

function Choice<T extends string>({ value, options, onChange, name }: {
  value: T; options: { v: T; label: string }[]; onChange: (v: T) => void; name: string;
}) {
  return (
    <fieldset className="choice">
      {options.map((o) => (
        <label key={o.v} className={o.v === value ? "on" : ""}>
          <input type="radio" name={name} checked={o.v === value} onChange={() => onChange(o.v)} />
          {o.label}
        </label>
      ))}
    </fieldset>
  );
}

function ProductCard({ r, t }: { r: Results; t: Dict }) {
  const p = r.provenance;
  return (
    <dl className="facts">
      <dt>{t.fields.granule}</dt><dd className="mono">{p.granule}</dd>
      <dt>{t.fields.reference}</dt><dd>{span(p.reference_acquisition)}</dd>
      <dt>{t.fields.secondary}</dt><dd>{span(p.secondary_acquisition)}</dd>
      <dt>{t.fields.maturity}</dt><dd><span className="badge">{p.maturity}</span> {p.crid}</dd>
      <dt>{t.fields.orbit}</dt><dd>{orb(t, p.orbit_pass)} / {orb(t, p.look_direction)}</dd>
      <dt>{t.fields.source}</dt><dd>{t.pv.source}</dd>
    </dl>
  );
}

export default function App() {
  // Every view is addressable: #view=observability&lang=es&region=scene&layer=reason&op=0.5
  const hash = useMemo(() => new URLSearchParams(location.hash.slice(1)), []);
  const pick = <T extends string>(k: string, ok: readonly T[], d: T): T => (ok as readonly string[]).includes(hash.get(k) ?? "") ? (hash.get(k) as T) : d;
  const [lang, setLang] = useState<Lang>(() => pick("lang", ["en", "es"], initialLang()));
  LOC = lang === "es" ? "es-BO" : "en-US";
  const [view, setView] = useState<View>(() => pick("view", ALL_VIEWS, "cover"));
  const [region, setRegion] = useState<Region>(() => pick("region", ["lapaz", "scene"], "lapaz"));
  const [r, setR] = useState<Results | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [terrain, setTerrain] = useState(() => pick("layer", ["hillshade", "slope", "aspect"], "hillshade"));
  const [radar, setRadar] = useState(() => pick("layer", ["phase", "coherence", "connected_components"], "coherence"));
  const [obsLayer, setObsLayer] = useState(() => pick("layer", ["state", "abs_sensitivity", "reason"], "state"));
  const [opacity, setOpacity] = useState(() => Math.min(1, Math.max(0.2, Number(hash.get("op")) || 0.85)));
  const t = DICTS[lang];

  useEffect(() => {
    fetch(`${DATA}results.json`).then((x) => {
      if (!x.ok) throw new Error(`results.json: HTTP ${x.status}`);
      return x.json();
    }).then(setR).catch((e: Error) => setErr(e.message));
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
    try { localStorage.setItem("qhantar-lang", lang); } catch { /* ignore */ }
  }, [lang]);

  const layerName = view === "mountain" ? terrain : view === "radar" ? radar : view === "observability" ? obsLayer : "state";

  useEffect(() => {
    const h = new URLSearchParams({ view, lang, region });
    if (view !== "cover" && view !== "mission" && view !== "passport") h.set("layer", layerName);
    if (opacity !== 0.85) h.set("op", String(opacity));
    history.replaceState(null, "", `#${h}`);
  }, [view, lang, region, layerName, opacity]);
  const layers: MapLayer[] = useMemo(() => {
    if (!r || view === "passport" || view === "cover") return [];
    const key = `${region}_${layerName}`;
    const out: MapLayer[] = [];
    if (view === "mountain" && terrain !== "hillshade") {
      const h = `${region}_hillshade`;
      out.push({ id: h, url: DATA + r.web_layers[h].file, corners: r.web_layers[h].corners, opacity: 0.6 });
    }
    out.push({ id: key, url: DATA + r.web_layers[key].file, corners: r.web_layers[key].corners, opacity });
    return out;
  }, [r, view, region, layerName, terrain, opacity]);

  if (err) return <main className="center">Error: {err}</main>;
  if (!r) return <main className="center">…</main>;

  const wl = r.web_layers[`${region}_${layerName}`];
  const fitCorners = r.web_layers[`${region}_state`].corners;
  const regionKey = region === "lapaz" ? "la_paz_crop" : "scene_footprint";

  let legend: ReactNode = null;
  if (view === "observability" && obsLayer === "reason") legend = <ReasonLegend r={r} t={t} region={region} />;
  else if (layerName === "state") legend = <StateLegend r={r} t={t} region={region} />;
  else if (layerName === "connected_components") legend = (
    <div className="legend">
      <div className="legend-title">{t.radar.cc}</div>
      <div className="legend-row"><Swatch color="#009E73" />{t.radar.cc_valid}</div>
      <div className="legend-row"><Swatch color="#D55E00" />{t.radar.cc_invalid}</div>
    </div>
  );
  else if (wl?.range) {
    const label = { hillshade: t.mountain.hillshade, slope: t.mountain.slope, aspect: t.mountain.aspect, phase: t.radar.phase,
      coherence: t.radar.coherence, abs_sensitivity: t.obs.sens }[layerName as string] ?? layerName;
    legend = <ColorBar ramp={wl.colormap} range={wl.range} label={label} />;
  }

  const regionPicker = (
    <Choice name="region" value={region} onChange={setRegion}
      options={[{ v: "lapaz", label: t.region.lapaz }, { v: "scene", label: t.region.scene }]} />
  );
  const opacityPicker = (
    <label className="slider">{t.opacity}
      <input type="range" min={0.2} max={1} step={0.05} value={opacity} onChange={(e) => setOpacity(+e.target.value)} />
    </label>
  );

  const side: Record<Exclude<View, "passport" | "cover">, ReactNode> = {
    mission: (
      <>
        <h2>{t.mission.title}</h2>
        <p>{t.mission.what}</p>
        <p className="note">{t.mission.prior}</p>
        <h3>{t.mission.not_title}</h3>
        <ul className="not">{t.mission.not.map((x) => <li key={x}>{x}</li>)}</ul>
        <p className="note">{t.mission.slow}</p>
        <h3>{t.mission.product}</h3>
        <ProductCard r={r} t={t} />
      </>
    ),
    mountain: (
      <>
        <h2>{t.mountain.title}</h2>
        <p>{t.mountain.body}</p>
        <Choice name="terrain" value={terrain} onChange={setTerrain} options={[
          { v: "hillshade", label: t.mountain.hillshade }, { v: "slope", label: t.mountain.slope }, { v: "aspect", label: t.mountain.aspect }]} />
        <p className="small">{t.mountain.slope_median}: <strong>{num(r.quality.slope_deg_in_valid.median, 1)}°</strong>. {t.obs.slope_min}: {num(r.parameters.slope_min_deg, 1)}°</p>
      </>
    ),
    radar: (
      <>
        <h2>{t.radar.title}</h2>
        <p>{t.radar.body}</p>
        <Choice name="radar" value={radar} onChange={setRadar} options={[
          { v: "phase", label: t.radar.phase }, { v: "coherence", label: t.radar.coherence }, { v: "connected_components", label: t.radar.cc }]} />
        {radar === "phase" && <p className="note">{t.radar.phase_note}</p>}
        {radar === "connected_components" && <p className="note">{t.radar.cc_note}</p>}
        <p className="small">{t.radar.coh_median}: <strong>{num(r.quality.coherence_in_valid.median)}</strong></p>
      </>
    ),
    observability: (
      <>
        <h2>{t.obs.title}</h2>
        <p>{t.obs.body}</p>
        <Choice name="obs" value={obsLayer} onChange={setObsLayer} options={[
          { v: "state", label: t.obs.state }, { v: "abs_sensitivity", label: t.obs.sens }, { v: "reason", label: t.obs.reason }]} />
        <h3>{t.obs.thresholds}</h3>
        <dl className="facts compact">
          <dt>{t.obs.s_min}</dt><dd>{num(r.parameters.s_min, 1)}</dd>
          <dt>{t.obs.coh_min}</dt><dd>{num(r.parameters.coh_min, 1)}</dd>
          <dt>{t.obs.slope_min}</dt><dd>{num(r.parameters.slope_min_deg, 1)}</dd>
        </dl>
        <h3>{t.obs.fractions} — {region === "lapaz" ? t.region.lapaz : t.region.scene}</h3>
        <table>
          <tbody>
            {(["1", "2", "3", "0"] as const).map((k) => (
              <tr key={k}><td><Swatch color={r.colors.state[k]} /> {t.states[k]}</td>
                <td className="num">{pct(r.fractions[regionKey].states.fractions[STATE_KEYS[k]])}</td>
                <td className="num muted">{int(r.fractions[regionKey].states.counts[STATE_KEYS[k]], lang)}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="small muted">{int(r.fractions[regionKey].states.n_pixels, lang)} {t.obs.pixels} · 80 m</p>
      </>
    ),
  };

  const open = (v: string) => { setView(v as View); scrollTo(0, 0); };

  return (
    <div className={`app v-${view}`}>
      <a className="skip" href="#main">{t.skip}</a>
      <header className="top">
        <button className="brand" onClick={() => open("cover")} aria-label={`QHANTAR · ${t.tagline}`}>
          <span className="mark">QHANTAR</span>
          <span className="tagline">{t.tagline}</span>
        </button>
        {view !== "cover" && <span className="badge real">{t.real_data} · {r.provenance.maturity}</span>}
        <button className="lang" onClick={() => setLang(lang === "en" ? "es" : "en")}>{t.lang}</button>
        {view === "cover" && <button className="btn primary sm" onClick={() => open("mission")}>{t.cover.open}</button>}
        {view !== "cover" && (
          <nav aria-label={t.views_label}>
            {VIEWS.map((v, i) => (
              <button key={v} className={v === view ? "on" : ""} aria-current={v === view} onClick={() => setView(v)}>
                <span className="step">{i + 1}</span>{t.nav[v]}
              </button>
            ))}
          </nav>
        )}
      </header>

      {view === "cover" ? (
        <Cover r={r} t={t} lang={lang} open={open} />
      ) : view === "passport" ? (
        <Passport r={r} t={t} lang={lang} />
      ) : (
        <main id="main" tabIndex={-1} className="split">
          <section className="mapwrap">
            <MapView layers={layers} fit={fitCorners} label={t.nav[view as Exclude<View, "cover">]} />
            <aside className="legend-dock" aria-live="polite">{legend}</aside>
          </section>
          <section className="side" key={view}>
            <div className="controls">{regionPicker}{view !== "mission" && opacityPicker}</div>
            {side[view]}
          </section>
        </main>
      )}
      <footer>
        <p>{t.identity}</p>
        <p className="small">{t.footer} {t.basemap}. {t.cover.note_ai_footer}</p>
      </footer>
    </div>
  );
}

function Passport({ r, t, lang }: { r: Results; t: Dict; lang: Lang }) {
  const p = r.provenance;
  const h = r.h1;
  return (
    <main id="main" tabIndex={-1} className="passport">
      <h2>{t.passport.title}</h2>
      <div className="cols">
        <section>
          <h3>{t.passport.provenance}</h3>
          <dl className="facts">
            <dt>{t.fields.granule}</dt><dd className="mono">{p.granule}</dd>
            <dt>{t.fields.reference}</dt><dd>{span(p.reference_acquisition)}</dd>
            <dt>{t.fields.secondary}</dt><dd>{span(p.secondary_acquisition)}</dd>
            <dt>{t.fields.maturity}</dt><dd><span className="badge">{p.maturity}</span><div className="small">{t.pv.maturity_note}</div></dd>
            <dt>{t.fields.crid}</dt><dd>{p.crid}</dd>
            <dt>{t.fields.orbit}</dt><dd>{orb(t, p.orbit_pass)} / {orb(t, p.look_direction)}</dd>
            <dt>{t.fields.track_frame}</dt><dd>{p.track} / {p.frame}</dd>
            <dt>{t.fields.pol}</dt><dd>{p.frequency.join(", ")} / {p.polarization}</dd>
            <dt>{t.fields.source}</dt><dd>{t.pv.source} — {p.collection}</dd>
            <dt>{t.fields.doi}</dt><dd><a href={`https://doi.org/${p.doi}`}>{p.doi}</a></dd>
            <dt>{t.fields.processed}</dt><dd>{utc(p.product_processing_utc)}</dd>
            <dt>{t.fields.url}</dt><dd className="mono small">{p.download_url}</dd>
            <dt>{t.fields.grid}</dt><dd>EPSG:{p.grid.epsg}, {p.grid.spacing_m} m, {t.pv.grid_size.replace("{w}", String(p.grid.shape[1])).replace("{h}", String(p.grid.shape[0]))}</dd>
            <dt>{t.fields.dem}</dt><dd>{t.pv.dem.replace("{src}", p.dem.source).replace("{n}", String(p.dem.tiles.length))}</dd>
            <dt>{t.fields.dem_vertical}</dt><dd>{t.pv.dem_vertical}</dd>
            <dt>{t.fields.generated}</dt><dd>{utc(r.generated_utc)}</dd>
          </dl>
          <h3>{t.passport.params}</h3>
          <dl className="facts compact">
            <dt>{t.obs.s_min}</dt><dd>{num(r.parameters.s_min, 1)}</dd>
            <dt>{t.obs.coh_min}</dt><dd>{num(r.parameters.coh_min, 1)}</dd>
            <dt>{t.obs.slope_min}</dt><dd>{num(r.parameters.slope_min_deg, 1)}</dd>
            <dt>{t.pv.cc_label}</dt><dd>{t.pv.cc.replace("{v}", String(r.parameters.connected_component_invalid_value))}</dd>
            <dt>{t.pv.valid_label}</dt><dd className="small">{t.pv.valid}</dd>
          </dl>
          <a className="download" href={`${DATA}results.json`} download="results.json">{t.passport.download}</a>
        </section>
        <section>
          <h3>{t.passport.h1}</h3>
          <p>{t.passport.h1_q}</p>
          {h ? (
            <>
              <table>
                <thead><tr><th>{t.passport.group}</th><th className="num">n</th><th className="num">{t.passport.median_coh}</th><th className="num">{t.passport.cc0}</th></tr></thead>
                <tbody>
                  {Object.entries(h.groups).map(([k, g]) => (
                    <tr key={k}><td>{t.passport.groups[k as keyof Dict["passport"]["groups"]] ?? k}</td>
                      <td className="num">{int(g.n_pixels, lang)}</td><td className="num">{num(g.coherence_median)}</td>
                      <td className="num">{pct(g.invalid_component_fraction)}</td></tr>
                  ))}
                  {h.slope_matched_check && <tr><td>{t.passport.matched}</td><td className="num">—</td>
                    <td className="num">{num(h.slope_matched_check.valid_reweighted.coherence_median)}</td>
                    <td className="num">{pct(h.slope_matched_check.valid_reweighted.invalid_component_fraction)}</td></tr>}
                </tbody>
              </table>
              <p><strong>{t.passport.verdict}:</strong> <span className="badge">{h.verdict}</span></p>
              <p className="note">{t.passport.confound}</p>
              <h4>{t.passport.limitations}</h4>
              <ul>{h.limitations.map((x) => <li key={x}>{x}</li>)}</ul>
            </>
          ) : <p className="badge">{t.passport.status}</p>}
          <h3>{t.passport.h234}</h3>
          <dl className="facts compact">
            {r.h2 && <><dt>H2</dt><dd>{t.passport.h2} {num(r.h2.layover_agreement.kappa)} / {num(r.h2.active_shadow_agreement.kappa)} · <span className="badge">{r.h2.verdict}</span></dd></>}
            {r.h3 && <><dt>H3</dt><dd>{t.passport.h3} {pct(r.h3.A_constant_heading_constant_incidence.state_changed_fraction)} / {pct(r.h3.B_constant_heading_per_pixel_incidence.state_changed_fraction)}</dd></>}
            {r.h4 && <><dt>H4</dt><dd>{r.h4.gamlp_scarps && <>{t.passport.h4} {pct(r.h4.gamlp_scarps.scarp_pixels.interpretable)} / {pct(r.h4.gamlp_scarps.scarp_pixels.coherent_low_sensitivity)} / {pct(r.h4.gamlp_scarps.scarp_pixels.not_observable_or_invalid)} · </>}<span className="badge">{r.h4.status}</span></dd></>}
          </dl>
          <p className="note">{t.passport.h234_docs}</p>
        </section>
      </div>
    </main>
  );
}
