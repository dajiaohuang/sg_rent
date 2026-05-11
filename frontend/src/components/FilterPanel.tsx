import type { SearchFilters } from "../types";

interface Props {
  filters: SearchFilters;
  onChange: (f: SearchFilters) => void;
}

export default function FilterPanel({ filters, onChange }: Props) {
  const update = (k: keyof SearchFilters, v: unknown) =>
    onChange({ ...filters, [k]: v });

  return (
    <div className="filter-panel">
      <div className="filter-group">
        <label>Type</label>
        <select
          value={filters.property_type ?? ""}
          onChange={(e) =>
            update("property_type", e.target.value || undefined)
          }
        >
          <option value="">All</option>
          <option value="hdb">HDB</option>
          <option value="condo">Condo</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Min Beds</label>
        <select
          value={filters.min_beds ?? ""}
          onChange={(e) =>
            update("min_beds", e.target.value ? Number(e.target.value) : undefined)
          }
        >
          <option value="">Any</option>
          {[1, 2, 3, 4, 5].map((n) => (
            <option key={n} value={n}>{n}+</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Max Price (S$/mo)</label>
        <input
          type="number"
          placeholder="No max"
          value={filters.max_price ?? ""}
          onChange={(e) =>
            update("max_price", e.target.value ? Number(e.target.value) : undefined)
          }
        />
      </div>

      <div className="filter-group">
        <label>Max Commute (min)</label>
        <input
          type="number"
          placeholder="No max"
          value={filters.max_commute_min ?? ""}
          onChange={(e) =>
            update(
              "max_commute_min",
              e.target.value ? Number(e.target.value) : undefined
            )
          }
        />
      </div>
    </div>
  );
}
