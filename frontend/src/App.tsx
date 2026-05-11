import { useState, useCallback, useEffect, useRef } from "react";
import SearchBar from "./components/SearchBar";
import FilterPanel from "./components/FilterPanel";
import PropertyMap from "./components/PropertyMap";
import PropertyList from "./components/PropertyList";
import { performSearch } from "./engine";
import type {
  CommuteLocation,
  SearchFilters,
  PropertyResult,
  StationInfo,
  AppData,
} from "./types";

const STATION_COORDS_CACHE: Map<string, { lat: number; lng: number }> = new Map();

function resolveCoords(
  loc: CommuteLocation,
  stations: StationInfo[]
): CommuteLocation {
  if (loc.lat != null && loc.lng != null) return loc;
  const addr = loc.address.trim();
  // Check station name cache
  let coords = STATION_COORDS_CACHE.get(addr.toLowerCase());
  if (!coords) {
    const match = stations.find(
      (s) => s.name.toLowerCase() === addr.toLowerCase()
    );
    if (match) {
      coords = { lat: match.lat, lng: match.lng };
      STATION_COORDS_CACHE.set(addr.toLowerCase(), coords);
    }
  }
  return coords ? { ...loc, ...coords } : loc;
}

export default function App() {
  const [data, setData] = useState<AppData | null>(null);
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState<PropertyResult[]>([]);
  const [stations, setStations] = useState<StationInfo[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [searching, setSearching] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({});
  const [locations, setLocations] = useState<CommuteLocation[]>([]);

  const searchRef = useRef<{
    locations: CommuteLocation[];
    filters: SearchFilters;
  } | null>(null);

  // Load data on mount
  useEffect(() => {
    fetch(import.meta.env.BASE_URL + "data.json")
      .then((r) => r.json())
      .then((d: AppData) => {
        setData(d);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load property data:", err);
        setLoading(false);
      });
  }, []);

  const doSearch = useCallback(
    (locs: CommuteLocation[], filts: SearchFilters) => {
      if (!data) return;
      setSearching(true);

      // Resolve coordinates for locations
      const resolved = locs.map((l) => resolveCoords(l, data.stations));

      // Use setTimeout to keep UI responsive for large dataset
      setTimeout(() => {
        const result = performSearch(
          data.properties,
          data.stations,
          resolved,
          filts
        );
        setResults(result.results);
        setStations(result.stations);
        if (result.results.length > 0) setSelectedId(result.results[0].id);
        setSearching(false);
      }, 50);
    },
    [data]
  );

  const handleSearch = useCallback(
    (locs: CommuteLocation[]) => {
      setLocations(locs);
      searchRef.current = { locations: locs, filters };
      doSearch(locs, filters);
    },
    [filters, doSearch]
  );

  const handleFilterChange = useCallback(
    (f: SearchFilters) => {
      setFilters(f);
      if (locations.length > 0) {
        doSearch(locations, f);
      }
    },
    [locations, doSearch]
  );

  if (loading) {
    return (
      <div className="app-loading">
        <h2>Loading SG Rent...</h2>
        <p>Loading property and MRT data</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>SG Rent</h1>
        <p className="subtitle">
          {data
            ? `${data.properties.length} properties · ${data.stations.length} MRT stations`
            : "Find your ideal home near where you need to be"}
        </p>
      </header>
      <div className="search-section">
        <SearchBar onSearch={handleSearch} loading={searching} />
        <FilterPanel filters={filters} onChange={handleFilterChange} />
      </div>
      <div className="main-content">
        <div className="map-area">
          <PropertyMap
            results={results}
            stations={stations}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>
        <div className="sidebar">
          <PropertyList
            results={results}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>
      </div>
    </div>
  );
}
