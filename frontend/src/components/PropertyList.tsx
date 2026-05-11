import type { PropertyResult } from "../types";
import PropertyCard from "./PropertyCard";

interface Props {
  results: PropertyResult[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}

export default function PropertyList({ results, selectedId, onSelect }: Props) {
  if (results.length === 0) {
    return (
      <div className="property-list empty">
        <p>No properties found. Try adjusting your filters or search locations.</p>
      </div>
    );
  }

  return (
    <div className="property-list">
      <div className="list-header">
        <h2>{results.length} Properties Found</h2>
      </div>
      <div className="list-scroll">
        {results.map((p) => (
          <PropertyCard
            key={p.id}
            property={p}
            isSelected={selectedId === p.id}
            onClick={() => onSelect(p.id)}
          />
        ))}
      </div>
    </div>
  );
}
