import { useEffect, useRef } from "react";
import maplibregl, { type Map as MlMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Corners } from "./types";

export interface MapLayer {
  id: string; // web_layers key, e.g. "lapaz_state"
  url: string;
  corners: Corners;
  opacity: number;
}

// Keyless basemap: OpenStreetMap standard tiles, attribution shown in the map.
const STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      maxzoom: 19,
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm", paint: { "raster-saturation": -0.6 } }],
};

function boundsOf(c: Corners): [[number, number], [number, number]] {
  const xs = c.map((p) => p[0]);
  const ys = c.map((p) => p[1]);
  return [[Math.min(...xs), Math.min(...ys)], [Math.max(...xs), Math.max(...ys)]];
}

export default function MapView({ layers, fit, label }: { layers: MapLayer[]; fit: Corners; label: string }) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<MlMap | null>(null);
  const shown = useRef<string[]>([]);

  useEffect(() => {
    if (!el.current) return;
    const m = new maplibregl.Map({ container: el.current, style: STYLE, bounds: boundsOf(fit), fitBoundsOptions: { padding: 20 } });
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    m.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
    map.current = m;
    (window as unknown as { qhantarMap: MlMap }).qhantarMap = m; // for inspection from the browser console
    return () => m.remove();
    // the map is created once; region changes are handled below
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    map.current?.fitBounds(boundsOf(fit), { padding: 20, duration: 600 });
  }, [fit]);

  useEffect(() => {
    const m = map.current;
    if (!m) return;
    const apply = () => {
      for (const id of shown.current) {
        if (!layers.find((l) => l.id === id)) {
          if (m.getLayer(id)) m.removeLayer(id);
          if (m.getSource(id)) m.removeSource(id);
        }
      }
      for (const l of layers) {
        if (!m.getSource(l.id)) {
          m.addSource(l.id, { type: "image", url: l.url, coordinates: l.corners });
          m.addLayer({ id: l.id, type: "raster", source: l.id, paint: { "raster-resampling": "nearest", "raster-fade-duration": 0 } });
        }
        m.setPaintProperty(l.id, "raster-opacity", l.opacity);
      }
      shown.current = layers.map((l) => l.id);
    };
    if (m.isStyleLoaded()) apply();
    else m.once("load", apply);
  }, [layers]);

  return <div ref={el} className="map" role="region" aria-label={label} />;
}
