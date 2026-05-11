export interface CommuteLocation {
  name: string;
  address: string;
  lat?: number;
  lng?: number;
}

export interface SearchFilters {
  max_price?: number;
  min_price?: number;
  min_beds?: number;
  max_beds?: number;
  property_type?: string;
  max_commute_min?: number;
}

export interface PropertyResult {
  id: number;
  title: string;
  property_type: string;
  address: string;
  lat: number;
  lng: number;
  monthly_rent: number;
  bedrooms: number;
  bathrooms: number;
  sqft: number | null;
  furnished: boolean;
  nearest_mrt: string | null;
  nearest_mrt_dist: number | null;
  commute_times: Record<string, number>;
  score: number;
}

export interface StationInfo {
  name: string;
  code: string;
  line: string;
  lat: number;
  lng: number;
}

export interface SearchResults {
  results: PropertyResult[];
  total: number;
  stations: StationInfo[];
}

// Raw data from static JSON
export interface PropertyData {
  id: number;
  title: string;
  type: 'hdb' | 'condo';
  address: string;
  lat: number;
  lng: number;
  rent: number;
  beds: number;
  baths: number;
  sqft: number | null;
  furnished: boolean;
  amenities: string[];
  mrt: string | null;
  mrt_dist: number | null;
}

export interface StationData {
  name: string;
  code: string;
  line: string;
  lat: number;
  lng: number;
}

export interface AppData {
  properties: PropertyData[];
  stations: StationData[];
}
