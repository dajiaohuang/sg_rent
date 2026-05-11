import { useState } from "react";
import type { CommuteLocation } from "../types";

interface Props {
  onSearch: (locations: CommuteLocation[]) => void;
  loading: boolean;
}

export default function SearchBar({ onSearch, loading }: Props) {
  const [locations, setLocations] = useState<CommuteLocation[]>([
    { name: "", address: "" },
  ]);

  const addLocation = () => {
    if (locations.length < 5) {
      setLocations([...locations, { name: "", address: "" }]);
    }
  };

  const removeLocation = (i: number) => {
    setLocations(locations.filter((_, idx) => idx !== i));
  };

  const updateLocation = (
    i: number,
    field: keyof CommuteLocation,
    value: string
  ) => {
    const next = [...locations];
    next[i] = { ...next[i], [field]: value };
    setLocations(next);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const valid = locations.filter((l) => l.name.trim());
    if (valid.length > 0) onSearch(valid);
  };

  return (
    <form onSubmit={handleSubmit} className="search-bar">
      <div className="search-locations">
        {locations.map((loc, i) => (
          <div key={i} className="location-row">
            <input
              type="text"
              placeholder="Label (e.g. Work, School)"
              value={loc.name}
              onChange={(e) => updateLocation(i, "name", e.target.value)}
              className="loc-name"
            />
            <input
              type="text"
              placeholder="Address (e.g. Raffles Place MRT)"
              value={loc.address}
              onChange={(e) => updateLocation(i, "address", e.target.value)}
              className="loc-address"
            />
            {locations.length > 1 && (
              <button
                type="button"
                onClick={() => removeLocation(i)}
                className="btn-remove"
              >
                x
              </button>
            )}
          </div>
        ))}
      </div>
      <div className="search-actions">
        <button
          type="button"
          onClick={addLocation}
          disabled={locations.length >= 5}
          className="btn-add"
        >
          + Add Location
        </button>
        <button type="submit" disabled={loading} className="btn-search">
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
    </form>
  );
}
