import { useEffect, useRef } from "react";
import L from "leaflet";
import type { PropertyResult, StationInfo } from "../types";

interface Props {
  results: PropertyResult[];
  stations: StationInfo[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}

// Fix default marker icon path issue with bundlers
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

const STATION_COLOR = "#27ae60";

function scoreColor(score: number): string {
  if (score >= 0.7) return "#2ecc71";
  if (score >= 0.5) return "#f1c40f";
  return "#e74c3c";
}

export default function PropertyMap({
  results,
  stations,
  selectedId,
  onSelect,
}: Props) {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<Map<number, L.Marker>>(new Map());

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current).setView([1.3521, 103.8198], 12);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update markers when results change
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Clear existing property markers
    markersRef.current.forEach((m) => {
      map.removeLayer(m);
    });
    markersRef.current.clear();

    // Add property markers
    for (const p of results) {
      const isSelected = p.id === selectedId;
      const color = scoreColor(p.score);
      const icon = L.divIcon({
        className: "custom-marker",
        html: `
          <div style="
            width:${isSelected ? "28" : "20"}px;
            height:${isSelected ? "28" : "20"}px;
            background:${color};
            border:3px solid white;
            border-radius:50%;
            box-shadow:0 2px 6px rgba(0,0,0,0.3);
            cursor:pointer;
            transition:all 0.2s;
          "></div>`,
        iconSize: [isSelected ? 28 : 20, isSelected ? 28 : 20],
        iconAnchor: [isSelected ? 14 : 10, isSelected ? 14 : 10],
      });

      const marker = L.marker([p.lat, p.lng], { icon })
        .addTo(map)
        .bindPopup(
          `<b>${p.title}</b><br/>
           ${p.property_type.toUpperCase()} · ${p.bedrooms} bed<br/>
           S$${p.monthly_rent.toLocaleString()}/mo<br/>
           ${Object.entries(p.commute_times).map(([n, m]) => `${n}: ${m}min`).join("<br>")}
           <br/>Score: ${Math.round(p.score * 100)}%`
        );
      marker.on("click", () => onSelect(p.id));
      markersRef.current.set(p.id, marker);
    }

    // Add station markers
    const stationMarkers: L.Marker[] = [];
    for (const s of stations) {
      const icon = L.divIcon({
        className: "station-marker",
        html: `<div style="
          width:10px;height:10px;
          background:${STATION_COLOR};
          border:2px solid white;
          border-radius:50%;
          box-shadow:0 1px 4px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [10, 10],
        iconAnchor: [5, 5],
      });
      const m = L.marker([s.lat, s.lng], { icon }).addTo(map);
      m.bindTooltip(`${s.name} (${s.code})`, { direction: "top" });
      stationMarkers.push(m);
    }

    return () => {
      stationMarkers.forEach((m) => map.removeLayer(m));
    };
  }, [results, stations, selectedId, onSelect]);

  // Pan to selected property
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !selectedId) return;
    const marker = markersRef.current.get(selectedId);
    if (marker) {
      map.panTo(marker.getLatLng(), { animate: true });
    }
  }, [selectedId]);

  return <div ref={containerRef} className="map-container" />;
}
