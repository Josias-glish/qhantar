import { useEffect, useRef } from "react";
import type { Results } from "./types";
import type { Dict, Lang } from "./App";

const DATA = "./data/";
// Absolute URLs: a url() inside a CSS custom property resolves against the stylesheet, not the page.
const abs = (u: string) => new URL(u, location.href).href;
const VIDEO_URL = abs("./media/hero-scrub.mp4");
const POSTER_URL = abs("./media/hero-poster.jpg");
const ENDING_URL = abs("./media/hero-ending.jpg");

// The five static-hero gates (phones, portrait tablets, coarse portrait, landscape phones, reduced motion).
// Must match the media queries in index.css character for character.
const GATES = [
  "(max-width: 720px)",
  "(orientation: portrait) and (max-width: 1024px)",
  "(orientation: portrait) and (pointer: coarse)",
  "(orientation: landscape) and (pointer: coarse) and (max-height: 560px)",
  "(prefers-reduced-motion: reduce)",
];
// Caption bands in hero progress [start, end]; first starts settled, last ends settled.
const BANDS: [number, number][] = [[0, 0.3], [0.36, 0.64], [0.7, 1]];

const smooth = (p: number, a: number, b: number) => {
  const t = Math.min(1, Math.max(0, (p - a) / (b - a)));
  return t * t * (3 - 2 * t);
};
const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

function rng(seed: number) {
  let s = seed >>> 0;
  return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296;
}

/** Visually split words (aria-hidden) with a screen-reader copy; each word gets a stagger threshold. */
function Words({ text, seed, spread = 0.5 }: { text: string; seed: number; spread?: number }) {
  const r = rng(seed);
  const words = text.split(" ");
  return (
    <>
      <span className="sr">{text}</span>
      <span aria-hidden="true">
        {words.map((w, i) => (
          <span key={i}><span className="w" style={{ ["--th" as string]: ((i / words.length) * spread + r() * 0.05).toFixed(3) }}>
            {w}
          </span>{" "}</span>
        ))}
      </span>
    </>
  );
}

const fmtDate = (iso: string, lang: Lang) =>
  new Date(iso.slice(0, 10) + "T12:00:00Z").toLocaleDateString(lang === "es" ? "es-BO" : "en-GB", { day: "numeric", month: "long", year: "numeric" });

export default function Cover({ r, t, lang, open }: { r: Results; t: Dict; lang: Lang; open: (view: string) => void }) {
  const hero = useRef<HTMLElement>(null);
  const hand = useRef<HTMLElement>(null);
  const c = t.cover;
  const p = r.provenance;
  const lp = r.fractions.la_paz_crop.states;
  const sc = r.fractions.scene_footprint.states;
  const dec = (x: number, d: number) => x.toLocaleString(lang === "es" ? "es-BO" : "en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  const pct = (x: number) => dec(x * 100, 1);

  // ---------- hero scrub ----------
  useEffect(() => {
    const root = hero.current!;
    const stage = root.querySelector<HTMLElement>(".stage")!;
    const video = root.querySelector<HTMLVideoElement>("video")!;
    const ring = root.querySelector<SVGElement>(".ring")!;
    const bands = [...root.querySelectorAll<HTMLElement>(".band")].map((el) => ({ el, op: -1, k: -1 }));
    let target = 0, shown = 0, raf: number | null = null, last = 0, onScreen = true;
    let seekBusy = false, pending: number | null = null, scrubOn = false, started = false;
    const loadStart = performance.now();

    const progress = () => {
      const rect = root.getBoundingClientRect();
      const range = rect.height - innerHeight;
      return range > 0 ? clamp(-rect.top / range, 0, 1) : 0;
    };
    const requestSeek = (time: number) => {
      if (!video.duration) return;
      if (seekBusy) { pending = time; return; }
      seekBusy = true;
      video.currentTime = time;
    };
    const onSeeked = () => {
      seekBusy = false;
      if (pending !== null) { const tm = pending; pending = null; requestSeek(tm); }
    };
    const onErr = () => { seekBusy = false; pending = null; stage.classList.add("video-failed"); };
    video.addEventListener("seeked", onSeeked);
    video.addEventListener("error", onErr);

    let past = false;
    const captions = (pr: number) => {
      if ((pr > 0.06) !== past) { past = !past; stage.classList.toggle("past", past); }
      const loadK = clamp((performance.now() - loadStart) / 1400, 0, 1);
      bands.forEach((b, i) => {
        const [a, e] = BANDS[i];
        const f = Math.min(0.03, (e - a) / 3);
        const op = (i === 0 ? 1 : smooth(pr, a, a + f)) * (i === BANDS.length - 1 ? 1 : 1 - smooth(pr, e - f, e));
        let k = clamp((pr - a) / Math.min(0.06, (e - a) * 0.35), 0, 1);
        if (i === 0) k = Math.max(k, loadK);
        if (Math.abs(op - b.op) > 0.004) { b.op = op; b.el.style.opacity = op.toFixed(3); b.el.classList.toggle("live", op > 0.05); }
        if (Math.abs(k - b.k) > 0.008) { b.k = k; b.el.style.setProperty("--k", k.toFixed(3)); }
      });
    };
    const tick = (now: number) => {
      const dt = Math.min(100, now - (last || now));
      last = now;
      shown += (target - shown) * (1 - Math.pow(1 - 0.16, dt / 16.667));
      const loading = performance.now() - loadStart < 1500;
      if (Math.abs(target - shown) < 0.0005 && !loading) { shown = target; raf = null; last = 0; }
      else raf = requestAnimationFrame(tick);
      requestSeek(shown * video.duration);
      captions(shown);
    };
    const onScroll = () => {
      target = progress();
      if (raf === null && onScreen) raf = requestAnimationFrame(tick);
    };

    const loadBlob = async () => {
      const ctrl = new AbortController();
      let watchdog = setTimeout(() => ctrl.abort(), 20000);
      const res = await fetch(VIDEO_URL, { signal: ctrl.signal });
      if (!res.ok || !res.body) throw new Error(`video HTTP ${res.status}`);
      const total = Number(res.headers.get("Content-Length")) || 6_000_000;
      const reader = res.body.getReader();
      const chunks: BlobPart[] = [];
      let got = 0, lastRing = 0;
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        clearTimeout(watchdog);
        watchdog = setTimeout(() => ctrl.abort(), 20000);
        chunks.push(value);
        got += value.length;
        const frac = Math.min(1, got / total), now = performance.now();
        if (now - lastRing > 100 || frac === 1) { lastRing = now; ring.style.setProperty("--ld", String(Math.round(126 * (1 - frac)))); }
      }
      clearTimeout(watchdog);
      ring.style.setProperty("--ld", "0");
      video.src = URL.createObjectURL(new Blob(chunks, { type: "video/mp4" }));
      video.load();
      video.addEventListener("canplay", () => { requestSeek(progress() * video.duration); stage.classList.add("video-ready"); }, { once: true });
    };
    const initOnce = () => {
      if (started) return;
      started = true;
      stage.style.setProperty("--poster", `url('${POSTER_URL}')`);
      const img = new Image();
      const go = () => loadBlob().catch(() => stage.classList.add("video-failed"));
      img.onload = img.onerror = go;
      img.src = POSTER_URL;
    };
    const enable = () => {
      if (scrubOn) return;
      scrubOn = true;
      initOnce();
      addEventListener("scroll", onScroll, { passive: true });
      bands.forEach((b) => { b.op = -1; b.k = -1; b.el.style.opacity = ""; });
      onScroll();
    };
    const disable = () => {
      if (!scrubOn) return;
      scrubOn = false;
      removeEventListener("scroll", onScroll);
      if (raf !== null) { cancelAnimationFrame(raf); raf = null; }
      bands.forEach((b) => { b.el.style.opacity = ""; b.el.style.setProperty("--k", "1"); });
    };
    const mqls = GATES.map((q) => matchMedia(q));
    const apply = () => (mqls.some((m) => m.matches) ? disable() : enable());
    mqls.forEach((m) => m.addEventListener("change", apply));
    apply();
    const io = new IntersectionObserver(([e]) => { onScreen = e.isIntersecting; if (onScreen) onScroll(); });
    io.observe(root);

    return () => {
      disable();
      io.disconnect();
      mqls.forEach((m) => m.removeEventListener("change", apply));
      video.removeEventListener("seeked", onSeeked);
      video.removeEventListener("error", onErr);
      if (video.src.startsWith("blob:")) URL.revokeObjectURL(video.src);
    };
  }, []);

  // ---------- illustration-to-data handover and the real-layer beats ----------
  useEffect(() => {
    const root = hand.current!;
    let lastP = -1, raf: number | null = null, paint: ((w: number) => void) | null = null;
    // Signature handover: the illustration drains away along La Paz's real contour lines, valley floor first.
    // The mask is the real DEM on the hillshade grid; the moving siena line is a true contour of it.
    const load = (u: string) => new Promise<HTMLImageElement>((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = u; });
    const cv = root.querySelector<HTMLCanvasElement>("canvas.ill");
    if (cv && getComputedStyle(cv).display !== "none") Promise.all([load(ENDING_URL), load(`${DATA}lapaz_elevation.png`)]).then(([ill, dem]) => {
      const W = dem.naturalWidth, H = dem.naturalHeight, N = W * H;
      cv.width = W; cv.height = H;
      const ctx = cv.getContext("2d", { willReadFrequently: true })!;
      const k = Math.max(W / ill.naturalWidth, H / ill.naturalHeight), sw = W / k, sh = H / k;
      ctx.drawImage(ill, (ill.naturalWidth - sw) / 2, (ill.naturalHeight - sh) / 2, sw, sh, 0, 0, W, H);
      const src = ctx.getImageData(0, 0, W, H).data;
      ctx.clearRect(0, 0, W, H); ctx.drawImage(dem, 0, 0);
      const e = ctx.getImageData(0, 0, W, H).data, z = new Uint8Array(N), cdf = new Float64Array(256);
      for (let i = 0; i < N; i++) { z[i] = e[i * 4]; cdf[z[i]]++; }
      for (let v = 0, acc = 0; v < 256; v++) { acc += cdf[v]; cdf[v] = acc / N; }   // level by area, so the wipe advances evenly
      const out = ctx.createImageData(W, H), o = out.data;
      paint = (w) => {
        let lv = -1;
        if (w >= 1) lv = 256; else if (w > 0) while (lv < 255 && cdf[lv + 1] < w) lv++;
        for (let i = 0; i < N; i++) {
          const j = i * 4;
          if (z[i] <= lv) { o[j + 3] = 0; continue; }
          const x = i % W;
          const edge = lv >= 0 && ((x > 0 && z[i - 1] <= lv) || (x < W - 1 && z[i + 1] <= lv) || (i >= W && z[i - W] <= lv) || (i < N - W && z[i + W] <= lv));
          if (edge) { o[j] = 154; o[j + 1] = 75; o[j + 2] = 44; o[j + 3] = 255; }
          else { o[j] = src[j]; o[j + 1] = src[j + 1]; o[j + 2] = src[j + 2]; o[j + 3] = 255; }
        }
        ctx.putImageData(out, 0, 0);
      };
      paint(clamp((lastP - 0.03) / 0.13, 0, 1));
    }).catch(() => cv.remove());
    let lastW = -1;
    const write = () => {
      raf = null;
      const rect = root.getBoundingClientRect();
      const range = rect.height - innerHeight;
      const pr = range > 0 ? clamp(-rect.top / range, 0, 1) : 0;
      if (Math.abs(pr - lastP) < 0.002) return;
      lastP = pr;
      root.style.setProperty("--p", pr.toFixed(4));
      root.dataset.beat = String(Math.min(4, Math.floor(pr * 5)));
      root.classList.toggle("isdata", (pr - 0.03) / 0.13 >= 1);   // label says "real data" only once no illustration is left
      const w = clamp((pr - 0.03) / 0.13, 0, 1);
      if (paint && w !== lastW) { lastW = w; paint(w); }
    };
    const onScroll = () => { if (raf === null) raf = requestAnimationFrame(write); };
    addEventListener("scroll", onScroll, { passive: true });
    write();
    return () => { removeEventListener("scroll", onScroll); if (raf !== null) cancelAnimationFrame(raf); };
  }, []);

  // ---------- entrances below the fold; pause loops on hidden tabs ----------
  useEffect(() => {
    const vis = () => document.body.classList.toggle("paused", document.hidden);
    document.documentElement.classList.add("js-reveal");   // content stays visible if this never runs
    document.addEventListener("visibilitychange", vis);
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && e.target.classList.add("in")), { threshold: 0.2 });
    document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
    return () => { io.disconnect(); document.removeEventListener("visibilitychange", vis); document.documentElement.classList.remove("js-reveal"); };
  }, []);

  const beats = [
    { key: "hillshade", fig: `${dec(r.quality.slope_deg_in_valid.median, 1)}°`, ...c.beats.relief },
    { key: "coherence", fig: dec(r.quality.coherence_in_valid.median, 3), ...c.beats.coherence },
    { key: "abs_sensitivity", fig: dec(r.quality.abs_S_in_valid.median, 3), ...c.beats.sens },
    { key: "state", fig: `${pct(lp.fractions.interpretable)} %`, ...c.beats.state },
  ];
  const STATES = [["1", "interpretable"], ["2", "visible_incoherent"], ["3", "coherent_low_sensitivity"], ["0", "not_observable_or_invalid"]] as const;
  const pass = c.pass[p.orbit_pass.toLowerCase() as keyof typeof c.pass] ?? p.orbit_pass;
  const b2 = c.b2.replace("{pass}", pass).replace("{ref}", fmtDate(p.reference_acquisition[0], lang)).replace("{sec}", fmtDate(p.secondary_acquisition[0], lang));

  return (
    <main id="main" tabIndex={-1} className="cover">
      <section ref={hero} className="hero" aria-label={c.hero_label}>
        <div className="stage" style={{ ["--still" as string]: `url('${ENDING_URL}')` }}>
          <div className="poster" aria-hidden="true" />
          <video muted playsInline preload="none" aria-hidden="true" tabIndex={-1} />
          <div className="scrim" aria-hidden="true" />
          <svg className="neatline" aria-hidden="true" preserveAspectRatio="none" viewBox="0 0 100 100">
            <rect x="1.2" y="1.8" width="97.6" height="96.4" />
            {Array.from({ length: 9 }, (_, i) => 10 + i * 10).map((v) => (
              <g key={v}><line x1={v} y1="1.8" x2={v} y2="3.3" /><line x1={v} y1="96.7" x2={v} y2="98.2" />
                <line x1="1.2" y1={v} x2="2.1" y2={v} /><line x1="97.9" y1={v} x2="98.8" y2={v} /></g>
            ))}
          </svg>
          <p className="mapnote chip"><span className="dot" aria-hidden="true" />{c.note_ai}</p>
          <svg className="ring" viewBox="0 0 48 48" aria-hidden="true">
            <circle cx="24" cy="24" r="20" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="126" style={{ strokeDashoffset: "var(--ld,126)" }} />
          </svg>

          <div className="band b1">
            <h1 className="sheet-title">QHANTAR</h1>
            <p className="lede rise"><Words text={c.b1} seed={7} /></p>
          </div>
          <div className="band b2">
            <p className="lede drift"><Words text={b2} seed={11} spread={0.6} /></p>
          </div>
          <div className="band b3">
            <p className="lede clear"><span className="soft" aria-hidden="true">{c.b3}</span><span className="sharp">{c.b3}</span></p>
            <p className="sub">{c.b3_sub}</p>
            <div className="cta-row">
              <button className="btn primary" onClick={() => open("mission")}>{c.open}</button>
            </div>
          </div>
          <p className="cue chip" aria-hidden="true">{c.scroll}</p>
        </div>
      </section>

      <section ref={hand} className="handover" aria-label={c.handover_label} data-beat="0">
        <div className="hstage">
          <figure className="sheet">
            <div className="plate">
              <canvas className="ill" aria-hidden="true" />
              <img className="layer base" src={`${DATA}lapaz_hillshade.png`} alt={c.alt_hillshade} />
              {beats.slice(1).map((b, i) => (
                <img key={b.key} className={`layer l${i + 1}`} src={`${DATA}lapaz_${b.key}.png`} alt={b.title} />
              ))}
              <span className="handnote chip"><span className="dot" aria-hidden="true" /><span className="was">{c.note_ai}</span><span className="now dem">{c.note_dem}</span><span className="now nisar">{c.note_data}</span></span>
            </div>
            <figcaption className="margin">
              <span>NISAR L2 GUNW · {p.crid} · {p.maturity}</span>
              <span>EPSG:{p.grid.epsg} · {p.grid.spacing_m} m</span>
            </figcaption>
          </figure>
          <div className="beats">
            <div className="beat intro"><h2>{c.handover_title}</h2><p>{c.handover_body}</p></div>
            {beats.map((b, i) => (
              <div key={b.key} className={`beat n${i + 1}`}>
                <h2>{b.title}</h2>
                <p className="fig">{b.fig}</p>
                <p className="figlabel">{b.figlabel}</p>
                <p>{b.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="states reveal" aria-labelledby="st-h">
        <h2 id="st-h">{c.states_title}</h2>
        <p className="lead">{c.states_lead}</p>
        <table className="legend-sheet">
          <thead><tr><th>{c.col_state}</th><th className="num">{t.region.lapaz}</th><th className="num">{t.region.scene}</th></tr></thead>
          <tbody>
            {STATES.map(([k, key], i) => (
              <tr key={k} style={{ ["--i" as string]: i }}>
                <td>
                  <span className="swatch" style={{ background: r.colors.state[k] }} aria-hidden="true" />
                  <strong>{t.states[k]}</strong>
                  <span className="desc">{t.state_desc[k]}</span>
                </td>
                <td className="num"><span className="bar" style={{ ["--w" as string]: lp.fractions[key], background: r.colors.state[k] }} />{pct(lp.fractions[key])} %</td>
                <td className="num">{pct(sc.fractions[key])} %</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="small muted">{c.thresholds.replace("{s}", dec(r.parameters.s_min, 1)).replace("{c}", dec(r.parameters.coh_min, 1)).replace("{f}", pct(r.fractions.la_paz_crop.reasons.fractions.flat))}</p>
      </section>

      <section className="isnot reveal" aria-labelledby="no-h">
        <h2 id="no-h">{c.not_title}</h2>
        <ul>{t.mission.not.map((x) => <li key={x}>{x}</li>)}</ul>
        <p className="slow">{t.mission.slow}</p>
        <p className="prior">{t.mission.prior}</p>
      </section>

      <section className="close reveal" aria-labelledby="cl-h">
        <h2 id="cl-h">{c.close_title}</h2>
        <dl className="marginalia">
          <dt>{t.fields.granule}</dt><dd className="mono">{p.granule}</dd>
          <dt>{t.fields.maturity}</dt><dd>{p.maturity} · {p.crid}</dd>
          <dt>{t.fields.doi}</dt><dd><a href={`https://doi.org/${p.doi}`}>{p.doi}</a></dd>
          <dt>{t.fields.dem}</dt><dd>{p.dem.name}</dd>
        </dl>
        <div className="cta-row">
          <button className="btn primary" onClick={() => open("mission")}>{c.open}</button>
          <button className="btn" onClick={() => open("passport")}>{c.passport}</button>
        </div>
      </section>
    </main>
  );
}
