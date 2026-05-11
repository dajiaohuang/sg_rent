import type { PropertyResult } from "../types";

interface Props {
  property: PropertyResult;
  isSelected: boolean;
  onClick: () => void;
}

export default function PropertyCard({ property, isSelected, onClick }: Props) {
  const p = property;
  const typeLabel = p.property_type === "condo" ? "Condo" : "HDB";
  const typeClass = p.property_type === "condo" ? "type-condo" : "type-hdb";

  return (
    <div
      className={`property-card ${isSelected ? "selected" : ""}`}
      onClick={onClick}
    >
      <div className="card-header">
        <span className={`property-type-badge ${typeClass}`}>{typeLabel}</span>
        <span className="card-score">
          {Math.round(p.score * 100)}%
        </span>
      </div>
      <h3 className="card-title">{p.title}</h3>
      <p className="card-address">{p.address}</p>
      <div className="card-details">
        <span>{p.bedrooms} bed</span>
        <span>{p.bathrooms} bath</span>
        {p.sqft && <span>{p.sqft} sqft</span>}
        {p.furnished && <span>Furnished</span>}
      </div>
      <div className="card-rent">S$ {p.monthly_rent.toLocaleString()}/mo</div>
      {p.nearest_mrt && (
        <div className="card-mrt">
          MRT: {p.nearest_mrt} ({p.nearest_mrt_dist}m)
        </div>
      )}
      <div className="card-commute">
        {Object.entries(p.commute_times).map(([name, mins]) => (
          <span key={name} className="commute-chip">
            {name}: {mins}min
          </span>
        ))}
      </div>
    </div>
  );
}
