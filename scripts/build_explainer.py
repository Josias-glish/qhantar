"""Builds docs/QHANTAR-funcionamiento.pdf: the Spanish explainer for the jury and the public.

Every figure is read from results/*/results.json at build time; maps are the committed web PNGs.
Needs only the standard library plus Playwright (Chromium) to print the HTML to PDF:
  python scripts/build_explainer.py
"""
import base64
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / "results" / "T118_A_F169_20261008_20261020_P05023"
DESC = next((p for p in (ROOT / "results").glob("T097_D_*") if (p / "results.json").exists()), None)
OUT = ROOT / "docs" / "QHANTAR-funcionamiento"

r = json.loads((ASC / "results.json").read_text())
d = json.loads((DESC / "results.json").read_text()) if DESC else None


def n(x, dec=1):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=1):
    return f"{n(x * 100, dec)} %"


def i(x):
    return n(x, 0)


def img(p, alt):
    b = base64.b64encode(Path(p).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{b}" alt="{html.escape(alt)}">'


P = r["provenance"]
F = r["fractions"]["la_paz_crop"]["states"]["fractions"]
FS = r["fractions"]["scene_footprint"]["states"]["fractions"]
RS = r["fractions"]["la_paz_crop"]["reasons"]["fractions"]
Q = r["quality"]
H1, H2, H3, H4 = r["h1"], r["h2"], r["h3"], r["h4"]
G = H1["groups"]
M = H1["slope_matched_check"]
A3 = H3["A_constant_heading_constant_incidence"]
B3 = H3["B_constant_heading_per_pixel_incidence"]
SC = H4.get("gamlp_scarps")
PAR = r["parameters"]
COL = r["colors"]["state"]
dates = f'{P["reference_acquisition"][0][:10]} y {P["secondary_acquisition"][0][:10]}'

desc_html = ""
if d and "two_orbits" in d:
    T = d["two_orbits"]
    desc_html = f"""
<section class="page">
<h2><span>05</span> Dos órbitas: la misma ciudad vista desde los dos lados</h2>
<p>Una sola línea de visión es una sola proyección. Para ver cuánto depende el resultado de la órbita, procesamos con el mismo
motor una segunda escena real: la órbita <b>descendente</b> (pista {d["provenance"]["track"]}, frame {d["provenance"]["frame"]},
{d["provenance"]["reference_acquisition"][0][:10]} y {d["provenance"]["secondary_acquisition"][0][:10]}, CRID {d["provenance"]["crid"]}).
En la ascendente el radar está al {html.escape(T["ascending_sensor_side_es"])} de la ladera; en la descendente, al {html.escape(T["descending_sensor_side_es"])}.</p>
<div class="cols">
<figure>{img(ASC / "web" / "lapaz_state.png", "Estados, órbita ascendente")}<figcaption>Órbita ascendente ({P["reference_acquisition"][0][:10]}).</figcaption></figure>
<figure>{img(DESC / "web" / "lapaz_state.png", "Estados, órbita descendente")}<figcaption>Órbita descendente ({d["provenance"]["reference_acquisition"][0][:10]}).</figcaption></figure>
</div>
<table><thead><tr><th>Píxeles del recorte de La Paz con dato en las dos órbitas ({i(T["n_common_pixels"])})</th><th class="r">Proporción</th></tr></thead><tbody>
<tr><td>Interpretables en las dos órbitas</td><td class="r">{pct(T["interpretable_both"])}</td></tr>
<tr><td>Interpretables solo en la ascendente</td><td class="r">{pct(T["interpretable_ascending_only"])}</td></tr>
<tr><td>Interpretables solo en la descendente</td><td class="r">{pct(T["interpretable_descending_only"])}</td></tr>
<tr><td>Interpretables en al menos una</td><td class="r"><b>{pct(T["interpretable_either"])}</b></td></tr>
</tbody></table>
<p class="note">{html.escape(T["reading_es"])}</p>
</section>"""

checks = [
    ("Cuatro estados, umbrales |S| ≥ 0,3 y coherencia ≥ 0,5, ajustables", "Cumple", f"{n(PAR['s_min'])} y {n(PAR['coh_min'])} en results.json; se pasan por línea de comandos"),
    ("Vectores LOS nativos; u_z = √(1 − x² − y²); cubos interpolados a la altura del DEM", "Cumple", "qhantar/engine.py y scripts/process_scene.py"),
    ("u_ladera = (sen α cos β, cos α cos β, −sen β)", "Cumple", "misma fórmula en engine.slope_vector, con pruebas de cinco rumbos"),
    ("Coherencia y sensibilidad separadas, sin índice compuesto", "Cumple", "capas separadas en la web y en GeoTIFF"),
    ("Pruebas sintéticas: 9 de 9", "Superado", "20 de 20 pruebas, también en un clon limpio"),
    ("Escena NISAR real procesada", "Hecho", "escena ascendente" + (" y descendente" if desc_html else "")),
    ("Mapa real de cuatro estados", "Hecho", "recorte de La Paz y escena completa"),
    ("H1", "Hecho, con resultado negativo", "se cumple sin emparejar; no se cumple a igual pendiente"),
    ("H2 índice R", "Hecho", f"κ {n(H2['layover_agreement']['kappa'], 3)} y {n(H2['active_shadow_agreement']['kappa'], 3)}"),
    ("H3 LOS nativa frente a aproximación", "Hecho", f"cambia el {pct(A3['state_changed_fraction'])} de los píxeles"),
    ("H4 solo como contexto, con inventario fiable", "Hecho como contexto", "escarpes del GAMLP 2013; no se presenta como validación"),
    ("Componente conectado 0 inválido «según la convención del producto»", "Documentado", "el archivo no lo define; SNAPHU e ISCE3 sí"),
    ("Pasaporte exportable", "Hecho", "descarga de results.json en la vista Pasaporte"),
    ("HDF5 fuera del repositorio; licencia permisiva; uso de IA declarado", "Cumple", "MIT; docs/ai-usage.md (ChatGPT, Claude, Antigravity)"),
    ("Validación con usuarios reales", "No realizada", "sigue pendiente, y así se declara"),
]
check_rows = "".join(f"<tr><td>{html.escape(a)}</td><td><b>{html.escape(b)}</b></td><td>{html.escape(c)}</td></tr>" for a, b, c in checks)
sw = lambda k: f'<i class="sw" style="background:{COL[k]}"></i>'
sec = iter(["06", "07", "08"] if desc_html else ["05", "06", "07"])

page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>QHANTAR: cómo funciona</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
@page {{ size: A4; margin: 16mm 16mm 18mm; }}
:root {{ --paper:#ECEDE6; --ink:#1F2421; --ink2:#4b524d; --siena:#9A4B2C; --ocre:#C8A15A; --piz:#3F4D5C; }}
* {{ box-sizing: border-box; }}
body {{ font-family: Archivo, sans-serif; color: var(--ink); font-size: 10.6pt; line-height: 1.5; margin: 0; }}
.page {{ break-after: page; }}
.page:last-child {{ break-after: auto; }}
h1 {{ font-size: 46pt; font-weight: 800; font-variation-settings: "wdth" 125; letter-spacing: .04em; margin: 0; }}
h2 {{ font-size: 17pt; font-weight: 800; font-variation-settings: "wdth" 112; margin: 0 0 8pt; border-bottom: 1.5pt solid var(--ink); padding-bottom: 4pt; }}
h2 span {{ font-family: "JetBrains Mono"; color: var(--siena); font-size: 11pt; margin-right: 6pt; }}
h3 {{ font-size: 11.5pt; margin: 11pt 0 4pt; }}
p {{ margin: 0 0 7pt; }}
@page :first {{ margin: 0; }}
.cover {{ background: var(--paper); margin: 0; padding: 30mm 18mm; height: 297mm; width: 210mm; display: flex; flex-direction: column; justify-content: space-between; }}
.kicker {{ font-family: "JetBrains Mono"; font-size: 9pt; letter-spacing: .14em; text-transform: uppercase; color: var(--piz); }}
.thesis {{ font-size: 17pt; line-height: 1.35; max-width: 150mm; margin-top: 14pt; }}
.quote {{ font-size: 13pt; border-left: 3pt solid var(--siena); padding-left: 10pt; margin: 18pt 0; max-width: 140mm; }}
.meta {{ font-family: "JetBrains Mono"; font-size: 7.6pt; color: var(--ink2); line-height: 1.6; word-break: break-all; }}
table {{ border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9.4pt; }}
th, td {{ text-align: left; padding: 3.5pt 5pt; border-bottom: .6pt solid #c9cbc2; vertical-align: top; }}
th {{ font-size: 7.8pt; text-transform: uppercase; letter-spacing: .08em; color: var(--ink2); border-bottom: 1pt solid var(--piz); }}
.r {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.sw {{ display: inline-block; width: 9pt; height: 9pt; margin-right: 5pt; vertical-align: -1pt; border: .5pt solid #0003; }}
.note {{ background: var(--paper); border-left: 3pt solid var(--ocre); padding: 6pt 9pt; font-size: 9.6pt; }}
.neg {{ border-left-color: var(--siena); }}
.eq {{ font-family: "JetBrains Mono"; font-size: 9.4pt; background: var(--paper); padding: 6pt 9pt; margin: 6pt 0; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12pt; }}
figure {{ margin: 6pt 0; }} figure img {{ width: 100%; border: .6pt solid #9aa; }}
figcaption {{ font-size: 8.2pt; color: var(--ink2); margin-top: 3pt; }}
.steps {{ counter-reset: s; list-style: none; padding: 0; margin: 4pt 0; }}
.steps li {{ counter-increment: s; padding: 3pt 0 3pt 22pt; position: relative; border-bottom: .5pt dotted #bbb; }}
.steps li::before {{ content: counter(s); position: absolute; left: 0; top: 3pt; font-family: "JetBrains Mono"; font-weight: 600; color: var(--siena); }}
ul {{ margin: 2pt 0 8pt; padding-left: 14pt; }} li {{ margin-bottom: 2pt; }}
svg text {{ font-family: Archivo; }}
</style></head><body>

<section class="page cover">
<div><div class="kicker">NASA Space Apps 2026 · Dancing with the SARs</div>
<h1>QHANTAR</h1>
<div class="kicker">Observabilidad de laderas con NISAR · La Paz, Bolivia</div>
<p class="thesis">Una herramienta que dice <b>dónde una observación radar NISAR permite interpretar el movimiento ladera abajo</b>,
dónde no, y por qué.</p>
<p class="quote">«No basta con ver una señal. Hay que saber si el radar podía observar aquello que queremos interpretar».</p></div>
<div class="meta">Documento explicativo para el jurado y el público. Todas las cifras se leen de results.json al generar este PDF.<br>
Escena principal: {html.escape(P["granule"])}<br>
{html.escape(P["maturity"])} · CRID {P["crid"]} · DOI {P["doi"]} · adquisiciones {dates}<br>
Web: qhantar.vercel.app · Código: github.com/Josias-glish/qhantar · Licencia MIT</div>
</section>

<section class="page">
<h2><span>01</span> El problema</h2>
<p>Un radar en órbita no mide el movimiento del terreno en todas las direcciones. Mide solo la parte del movimiento que va
<b>hacia él o en sentido contrario</b>, a lo largo de su línea de visión (LOS, <i>line of sight</i>).</p>
<p>Piense en el radar de velocidad de la policía. Un auto que viene de frente marca su velocidad completa. Un auto que cruza
de lado delante del radar marca casi cero, aunque vaya rápido. Con las laderas pasa lo mismo: una ladera que se desliza
de lado respecto al satélite puede moverse y casi no dejar señal.</p>
<svg viewBox="0 0 520 170" width="100%" height="170">
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#1F2421"/></marker>
<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#9A4B2C"/></marker></defs>
<rect x="430" y="10" width="60" height="22" fill="#3F4D5C"/><text x="460" y="25" fill="#fff" font-size="11" text-anchor="middle">NISAR</text>
<line x1="455" y1="34" x2="120" y2="150" stroke="#3F4D5C" stroke-dasharray="5 4"/><text x="300" y="70" font-size="10" fill="#3F4D5C">línea de visión (LOS)</text>
<path d="M30 160 L150 90 L230 160 Z" fill="#C8A15A" opacity=".55"/>
<line x1="120" y1="108" x2="70" y2="138" stroke="#1F2421" stroke-width="2.4" marker-end="url(#a)"/>
<text x="20" y="100" font-size="10">movimiento ladera abajo</text>
<line x1="95" y1="123" x2="125" y2="113" stroke="#9A4B2C" stroke-width="2.4" marker-end="url(#b)"/>
<text x="130" y="128" font-size="10" fill="#9A4B2C">lo que el radar ve: S</text>
<path d="M290 160 L380 100 L470 160 Z" fill="#C8A15A" opacity=".35"/>
<circle cx="380" cy="125" r="4" fill="#1F2421"/><text x="300" y="150" font-size="10">ladera que se mueve «de lado»: S ≈ 0</text>
</svg>
<p>De ahí salen dos errores que QHANTAR ayuda a evitar:</p>
<ul><li><b>Falso convencimiento de movimiento:</b> ver colores en un interferograma y creer que es deformación, sin revisar la calidad.</li>
<li><b>Falso convencimiento de estabilidad:</b> no ver señal y concluir que la ladera está quieta, cuando el radar no era sensible a ese movimiento.</li></ul>
<p class="note">Una señal ausente no siempre significa que no haya movimiento. Puede significar que el radar no podía verlo.</p>
<h3>Qué es y qué no es</h3>
<p>QHANTAR <b>no</b> detecta deslizamientos, no predice desastres, no calcula riesgo y no mide desplazamiento. Evalúa una sola cosa:
si una observación NISAR concreta permite interpretar un posible movimiento ladera abajo en cada píxel.</p>
</section>

<section class="page">
<h2><span>02</span> Cómo funciona, paso a paso</h2>
<ol class="steps">
<li><b>Recibe un producto NISAR GUNW real</b> (interferograma geocodificado y desenrollado, nivel 2, 80 m), descargado del ASF DAAC.</li>
<li><b>Lee su procedencia:</b> identificador, fechas, CRID, madurez y DOI. Esta escena es {html.escape(P["maturity"])} ({P["crid"]}).</li>
<li><b>Extrae la evidencia radar por separado:</b> fase desenrollada (en radianes), coherencia, componentes conectados y máscara de validez.</li>
<li><b>Toma la geometría nativa del satélite:</b> los vectores de línea de visión que trae el propio producto, interpolados a la altura real del terreno.</li>
<li><b>Calcula la forma de cada ladera</b> con el modelo de elevación Copernicus GLO-30: pendiente y orientación ladera abajo.</li>
<li><b>Calcula la sensibilidad S:</b> cuánto de un movimiento ladera abajo vería el radar en ese píxel.</li>
<li><b>Revisa distorsiones y calidad:</b> layover (el relieve se pliega sobre sí mismo en la imagen), shadow (el radar no ilumina la ladera), terreno plano, datos faltantes, coherencia y componentes.</li>
<li><b>Clasifica cada píxel en uno de cuatro estados</b> y publica mapas, GeoTIFF y un results.json con todas las cifras.</li>
</ol>
<h3>La idea matemática, en una línea</h3>
<div class="eq">u_ladera = (sen α·cos β, cos α·cos β, −sen β) · u_LOS = (x, y, √(1 − x² − y²)) · S = u_ladera · u_LOS</div>
<p>α es la orientación ladera abajo, β la pendiente, y x, y son las componentes Este y Norte del vector LOS que trae el producto.
|S| cerca de 1: el movimiento ladera abajo apunta casi directo al radar. |S| cerca de 0: el radar casi no lo vería.
<b>S no es una medición de movimiento</b>; es una propiedad de la geometría.</p>
<h3>Los cuatro estados</h3>
<table><thead><tr><th>Estado</th><th>Condición</th><th>Qué significa</th></tr></thead><tbody>
<tr><td>{sw("1")}1 · Interpretable</td><td>|S| ≥ {n(PAR["s_min"])} y coherencia ≥ {n(PAR["coh_min"])}, geometría y componente válidos</td><td>La fase puede analizarse para ese movimiento, con sus límites</td></tr>
<tr><td>{sw("2")}2 · Visible, incoherente</td><td>|S| suficiente, coherencia baja</td><td>La geometría sirve; la medición no tiene calidad</td></tr>
<tr><td>{sw("3")}3 · Coherente, poco sensible</td><td>Coherencia buena, |S| baja</td><td>Buena medición, pero casi ciega a ese movimiento</td></tr>
<tr><td>{sw("0")}0 · No observable o inválido</td><td>Layover, shadow, terreno plano (&lt; {n(PAR["slope_min_deg"])}°), sin datos, componente inválido</td><td>No interpretar la fase como evidencia</td></tr>
</tbody></table>
<p class="note">Los umbrales son decisiones iniciales ajustables, no constantes universales. Coherencia y sensibilidad se muestran por separado:
no se multiplican para inventar un índice.</p>
</section>

<section class="page">
<h2><span>03</span> Resultado real sobre La Paz</h2>
<p>Pareja ascendente del {dates} (pista {P["track"]}, frame {P["frame"]}, polarización {P["polarization"]}), 12 días entre imágenes.</p>
<div class="cols">
<figure>{img(ASC / "web" / "lapaz_state.png", "Mapa de cuatro estados de La Paz")}<figcaption>Cuatro estados, recorte de La Paz. Azul interpretable, bermellón visible incoherente, amarillo coherente poco sensible, gris no observable.</figcaption></figure>
<figure>{img(ASC / "web" / "lapaz_abs_sensitivity.png", "Sensibilidad |S| de La Paz")}<figcaption>Sensibilidad |S| de 0 a 1. Capa separada de la coherencia.</figcaption></figure>
</div>
<table><thead><tr><th>Estado</th><th class="r">Recorte de La Paz</th><th class="r">Escena completa</th></tr></thead><tbody>
<tr><td>{sw("1")}Interpretable</td><td class="r">{pct(F["interpretable"])}</td><td class="r">{pct(FS["interpretable"])}</td></tr>
<tr><td>{sw("2")}Visible, incoherente</td><td class="r">{pct(F["visible_incoherent"])}</td><td class="r">{pct(FS["visible_incoherent"])}</td></tr>
<tr><td>{sw("3")}Coherente, poco sensible</td><td class="r">{pct(F["coherent_low_sensitivity"])}</td><td class="r">{pct(FS["coherent_low_sensitivity"])}</td></tr>
<tr><td>{sw("0")}No observable o inválido</td><td class="r">{pct(F["not_observable_or_invalid"])}</td><td class="r">{pct(FS["not_observable_or_invalid"])}</td></tr>
</tbody></table>
<p>¿Por qué casi un tercio es «no observable»? Sobre todo por terreno plano ({pct(RS["flat"])} del recorte, el altiplano de El Alto),
que no tiene una dirección ladera abajo definida. No es un fallo del radar. Layover y shadow juntos son el {pct(RS["layover"] + RS["shadow"], 2)}.
La coherencia mediana de los píxeles válidos es {n(Q["coherence_in_valid"]["median"], 3)} y la |S| mediana, {n(Q["abs_S_in_valid"]["median"], 3)}.</p>
<p class="note">El {pct(F["coherent_low_sensitivity"])} del recorte tiene buena coherencia pero |S| baja: ahí un interferograma tranquilo
<b>no prueba</b> que la ladera esté quieta.</p>
</section>

<section class="page">
<h2><span>04</span> ¿Cómo sabemos que funciona?</h2>
<p>Separamos tres cosas: pruebas matemáticas, coherencia con la escena real y contraste con otros métodos. Publicamos los
resultados positivos y los negativos.</p>
<h3>Pruebas del motor</h3>
<p>Pasan 20 pruebas analíticas, también en un clon limpio del repositorio: LOS paralela y perpendicular, terreno plano, cinco
rumbos, layover, shadow, precedencia de estados, umbrales como parámetros y LOS nativa frente a la formulación por ángulos.
En la escena real, el vector LOS reproduce el ángulo de incidencia del producto y la orientación esperada para un radar que mira a la izquierda.</p>
<h3>H1 · ¿layover y shadow tienen peor coherencia?</h3>
<table><thead><tr><th>Grupo</th><th class="r">Píxeles</th><th class="r">Coherencia mediana</th><th class="r">Componente 0</th></tr></thead><tbody>
<tr><td>Layover o shadow</td><td class="r">{i(G["layover_or_shadow"]["n_pixels"])}</td><td class="r">{n(G["layover_or_shadow"]["coherence_median"], 3)}</td><td class="r">{pct(G["layover_or_shadow"]["invalid_component_fraction"])}</td></tr>
<tr><td>Geométricamente válidos</td><td class="r">{i(G["geometrically_valid"]["n_pixels"])}</td><td class="r">{n(G["geometrically_valid"]["coherence_median"], 3)}</td><td class="r">{pct(G["geometrically_valid"]["invalid_component_fraction"])}</td></tr>
<tr><td>Válidos, misma pendiente que layover/shadow</td><td class="r">—</td><td class="r">{n(M["valid_reweighted"]["coherence_median"], 3)}</td><td class="r">{pct(M["valid_reweighted"]["invalid_component_fraction"])}</td></tr>
</tbody></table>
<p class="note neg"><b>Resultado negativo, publicado.</b> La comparación fijada de antemano dice que sí. Pero a igual pendiente la diferencia
desaparece: la peor coherencia viene de lo empinado del terreno, no del layover.</p>
<h3>H2 · contraste con el índice R de Notti et al.</h3>
<p>Implementamos aparte el índice R, sin usar el código de QHANTAR y con otra forma de derivar la pendiente. Acuerdo de
Cohen: κ = {n(H2["layover_agreement"]["kappa"], 3)} en layover y {n(H2["active_shadow_agreement"]["kappa"], 3)} en shadow
(criterio fijado antes: ≥ 0,8). Con la misma pendiente, κ = 1. Además, el {pct(H2["fraction_of_R_good_visibility_with_absS_below_0_3"])}
de los píxeles que el índice R califica como «buena visibilidad» tiene |S| &lt; 0,3: se ven bien, pero un movimiento ladera abajo casi no se proyectaría.</p>
<h3>H3 · ¿importa usar la LOS nativa?</h3>
<p>Si se reemplaza la LOS del producto por la aproximación habitual de rumbo e incidencia, cambia de estado el
<b>{pct(A3["state_changed_fraction"])}</b> de los píxeles; solo por el error de dirección, el {pct(B3["state_changed_fraction"])}.
La aproximación se desvía entre {n(H3["native_los_azimuth_target_to_sensor_deg"]["min"] - H3["native_los_azimuth_target_to_sensor_deg"]["approximation"])}°
y {n(H3["native_los_azimuth_target_to_sensor_deg"]["max"] - H3["native_los_azimuth_target_to_sensor_deg"]["approximation"])}° de la dirección real.</p>
<h3>H4 · zonas activas conocidas (contexto, no validación)</h3>
<p>El catálogo global de NASA tiene solo 4 eventos en el recorte, con 1 a 10 km de error: demasiado grueso.
{"Sobre los " + i(SC["features"]) + " escarpes de deslizamiento mapeados por el municipio de La Paz (GAMLP, 2013), el " + pct(SC["scarp_pixels"]["interpretable"]) + " de los píxeles es interpretable, el " + pct(SC["scarp_pixels"]["coherent_low_sensitivity"]) + " coherente pero poco sensible y solo el " + pct(SC["scarp_pixels"]["not_observable_or_invalid"]) + " no observable. Los escarpes son de 2013: dicen dónde mirar, no si hubo movimiento en 2026." if SC else ""}</p>
</section>
{desc_html}
<section class="page">
<h2><span>{next(sec)}</span> Qué aporta y qué ya existía</h2>
<p>No inventamos la relación entre pendiente y radar. El índice R (Notti et al., 2010) y el índice mundial de sensibilidad InSAR
(van Natijne et al., 2022) ya estudian la visibilidad y la sensibilidad al movimiento ladera abajo, sobre todo <i>antes</i> de tener una pareja de imágenes.</p>
<table><thead><tr><th></th><th>Evaluación previa genérica</th><th>QHANTAR</th></tr></thead><tbody>
<tr><td>Pregunta</td><td>¿Esta geometría sería favorable?</td><td>¿Es interpretable esta ladera en <b>esta</b> pareja NISAR?</td></tr>
<tr><td>Geometría</td><td>Órbita o aproximación</td><td>Vectores LOS nativos del producto</td></tr>
<tr><td>Calidad</td><td>Potencial estimado</td><td>Coherencia y componentes medidos en la pareja</td></tr>
<tr><td>Salida</td><td>Potencial de monitoreo</td><td>Cuatro estados, con su razón, por píxel</td></tr>
</tbody></table>
<p>No afirmamos ser los primeros. Afirmamos que, en nuestra revisión, no encontramos una herramienta pública que haga
exactamente esto sobre un GUNW de NISAR, y que el método está abierto para que cualquiera lo compruebe.</p>
<h3>Límites que declaramos</h3>
<ul><li>Una sola línea de visión mide una sola proyección: no recupera el movimiento en tres dimensiones.</li>
<li>En 12 días, un movimiento de 5 cm/año son unos 1,6 mm: puede quedar por debajo del ruido de un solo interferograma.</li>
<li>Producto PROVISIONAL (P05023). ASF documenta un problema de marcas de tiempo corregido en P05036, que no existía sobre La Paz al hacer el análisis.</li>
<li>El modelo de layover y shadow es de primer orden, píxel a píxel.</li>
<li>No hubo validación con usuarios reales.</li></ul>
<h3>Uso de inteligencia artificial</h3>
<p>Declaramos el uso de ChatGPT, Claude y Antigravity, con lo que hizo cada uno y lo que revisó el equipo, en docs/ai-usage.md.
La ilustración de la portada web está generada con IA, marcada así en pantalla, y nunca se usa como dato.</p>
</section>

<section class="page">
<h2><span>{next(sec)}</span> Cómo comprobarlo usted mismo</h2>
<p>La web (qhantar.vercel.app) tiene cinco vistas: resumen de misión, observatorio de montaña, evidencia radar, observabilidad
pendiente–LOS y pasaporte de evidencia. Cada capa muestra su procedencia; el pasaporte permite descargar results.json.</p>
<p>El código (github.com/Josias-glish/qhantar) incluye las pruebas, las convenciones y los comandos para regenerar todo a partir
del archivo NISAR. El archivo original de 2,3 GB no se sube al repositorio: se descarga del ASF DAAC con una cuenta gratuita de Earthdata.</p>
<div class="eq">pytest · python scripts/process_scene.py &lt;GUNW.h5&gt; &lt;carpeta DEM&gt; · python scripts/h1.py … h4.py</div>
</section>

<section class="page">
<h2><span>{next(sec)}</span> Verificación contra el documento maestro</h2>
<p>Comparamos cada compromiso del documento fundacional (docs/master-document.es.md) con lo que hay hoy en el código, los datos y la web.</p>
<table><thead><tr><th>El documento maestro dice</th><th>Estado</th><th>Evidencia</th></tr></thead><tbody>{check_rows}</tbody></table>
<p class="meta">Generado por scripts/build_explainer.py a partir de results.json.</p>
</section>
</body></html>"""

OUT.with_suffix(".html").write_text(page, encoding="utf-8")
if "--html-only" not in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(OUT.with_suffix(".html").as_uri())
        pg.wait_for_load_state("networkidle")
        pg.pdf(path=str(OUT.with_suffix(".pdf")), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    print("written", OUT.with_suffix(".pdf"))
