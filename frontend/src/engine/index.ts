// Singapore MRT-based commute engine and property ranking
// Pure TypeScript — no backend required

import type { CommuteLocation, SearchFilters, SearchResults } from '../types';

// ============================================================
// Data types (matching the static JSON export)
// ============================================================
export interface RawProperty {
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

export interface RawStation {
  name: string;
  code: string;
  line: string;
  lat: number;
  lng: number;
}

interface StationGraph {
  [code: string]: { [neighborCode: string]: number };
}

// ============================================================
// MRT inter-station travel times (minutes)
// ============================================================
const INTER_STATION_TIMES: [string, string, number][] = [
  // North-South Line
  ['NS1','NS2',2.5],['NS2','NS3',2.0],['NS3','NS4',2.5],['NS4','NS5',2.5],
  ['NS5','NS7',3.0],['NS7','NS8',2.5],['NS8','NS9',2.0],['NS9','NS10',2.5],
  ['NS10','NS11',3.0],['NS11','NS12',2.0],['NS12','NS13',2.5],['NS13','NS14',2.0],
  ['NS14','NS15',3.5],['NS15','NS16',2.5],['NS16','NS17',3.0],['NS17','NS18',2.0],
  ['NS18','NS19',2.0],['NS19','NS20',2.5],['NS20','NS21',2.0],['NS21','NS22',2.0],
  ['NS22','NS23',2.0],['NS23','NS24',2.0],['NS24','NS25',2.0],['NS25','NS26',2.0],
  ['NS26','NS27',2.0],['NS27','NS28',3.0],
  // East-West Line
  ['EW1','EW2',3.0],['EW2','EW3',2.5],['EW3','EW4',2.5],['EW4','EW5',2.5],
  ['EW5','EW6',2.0],['EW6','EW7',2.0],['EW7','EW8',2.0],['EW8','EW9',2.0],
  ['EW9','EW10',2.0],['EW10','EW11',2.0],['EW11','EW12',2.0],['EW12','EW13',2.0],
  ['EW13','EW14',2.0],['EW14','EW15',2.0],['EW15','EW16',2.0],['EW16','EW17',2.0],
  ['EW17','EW18',2.0],['EW18','EW19',2.5],['EW19','EW20',2.0],['EW20','EW21',2.0],
  ['EW21','EW22',2.0],['EW22','EW23',2.5],['EW23','EW24',3.0],['EW24','EW25',2.5],
  ['EW25','EW26',2.5],['EW26','EW27',2.5],['EW27','EW28',2.5],['EW28','EW29',2.5],
  ['EW4','CG1',3.0],['CG1','CG2',4.0],
  // North East Line
  ['NE1','NE3',3.0],['NE3','NE4',2.0],['NE4','NE5',2.0],['NE5','NE6',2.0],
  ['NE6','NE7',2.0],['NE7','NE8',2.0],['NE8','NE9',2.0],['NE9','NE10',2.5],
  ['NE10','NE11',2.0],['NE11','NE12',2.5],['NE12','NE13',2.5],['NE13','NE14',2.5],
  ['NE14','NE15',2.5],['NE15','NE16',2.5],['NE16','NE17',3.0],
  // Circle Line
  ['CC1','CC2',2.0],['CC2','CC3',2.0],['CC3','CC4',2.0],['CC4','CC5',2.0],
  ['CC5','CC6',2.0],['CC6','CC7',2.0],['CC7','CC8',2.0],['CC8','CC9',2.0],
  ['CC9','CC10',2.5],['CC10','CC11',2.5],['CC11','CC12',2.0],['CC12','CC13',2.5],
  ['CC13','CC14',2.5],['CC14','CC15',2.5],['CC15','CC16',2.0],['CC16','CC17',2.0],
  ['CC17','CC19',3.0],['CC19','CC20',2.5],['CC20','CC21',2.0],['CC21','CC22',2.0],
  ['CC22','CC23',2.0],['CC23','CC24',2.0],['CC24','CC25',2.0],['CC25','CC26',2.0],
  ['CC26','CC27',2.0],['CC27','CC28',2.0],['CC28','CC29',2.0],
  // Downtown Line
  ['DT1','DT2',2.0],['DT2','DT3',2.0],['DT3','DT5',3.0],['DT5','DT6',2.5],
  ['DT6','DT7',2.0],['DT7','DT8',2.0],['DT8','DT9',2.0],['DT9','DT10',2.5],
  ['DT10','DT11',2.5],['DT11','DT12',2.0],['DT12','DT13',2.0],['DT13','DT14',2.0],
  ['DT14','DT15',2.5],['DT15','DT16',2.5],['DT16','DT17',2.0],['DT17','DT18',2.0],
  ['DT18','DT19',2.0],['DT19','DT20',2.0],['DT20','DT21',2.0],['DT21','DT22',2.0],
  ['DT22','DT23',2.0],['DT23','DT24',2.0],['DT24','DT25',2.0],['DT25','DT26',2.0],
  ['DT26','DT27',2.0],['DT27','DT28',2.0],['DT28','DT29',2.5],['DT29','DT30',2.0],
  ['DT30','DT31',2.5],['DT31','DT32',2.5],['DT32','DT33',2.5],['DT33','DT34',2.5],
  ['DT34','DT35',2.5],
  // Thomson-East Coast Line
  ['TE1','TE2',3.0],['TE2','TE3',3.0],['TE3','TE4',3.5],['TE4','TE5',3.0],
  ['TE5','TE6',2.5],['TE6','TE7',2.5],['TE7','TE8',2.5],['TE8','TE9',3.0],
  ['TE9','TE11',3.0],['TE11','TE12',2.5],['TE12','TE13',2.5],['TE13','TE14',2.0],
  ['TE14','TE15',2.5],['TE15','TE16',2.0],['TE16','TE17',2.0],['TE17','TE18',2.0],
  ['TE18','TE19',2.0],['TE19','TE20',2.0],['TE20','TE22',3.0],['TE22','TE23',2.5],
  ['TE23','TE24',2.5],['TE24','TE25',3.0],['TE25','TE26',2.5],['TE26','TE27',2.5],
  ['TE27','TE28',3.0],['TE28','TE29',3.0],
];

// ============================================================
// Math utils
// ============================================================
function haversine(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function walkingTimeMin(meters: number): number {
  return meters / 1.4 / 60; // 1.4 m/s walking speed
}

// ============================================================
// Station graph + Dijkstra
// ============================================================
let _graph: StationGraph | null = null;
let _stationIndex: Map<string, { lat: number; lng: number }> | null = null;

function buildGraph(stations: RawStation[]): StationGraph {
  const graph: StationGraph = {};

  // Add inter-station edges
  for (const [c1, c2, t] of INTER_STATION_TIMES) {
    (graph[c1] ??= {})[c2] = t;
    (graph[c2] ??= {})[c1] = t;
  }

  // Add transfer edges (5 min for same-name stations, different codes)
  const nameToCodes = new Map<string, string[]>();
  for (const s of stations) {
    const codes = nameToCodes.get(s.name) ?? [];
    codes.push(s.code);
    nameToCodes.set(s.name, codes);
  }
  for (const codes of nameToCodes.values()) {
    for (let i = 0; i < codes.length; i++) {
      for (let j = i + 1; j < codes.length; j++) {
        (graph[codes[i]] ??= {})[codes[j]] = 5.0;
        (graph[codes[j]] ??= {})[codes[i]] = 5.0;
      }
    }
  }
  return graph;
}

function dijkstra(graph: StationGraph, start: string): Map<string, number> {
  const dist = new Map<string, number>();
  const pq: [number, string][] = []; // [distance, node]
  dist.set(start, 0);
  pq.push([0, start]);

  while (pq.length > 0) {
    // Extract min (simpler than heap for this size)
    let minIdx = 0;
    for (let i = 1; i < pq.length; i++) {
      if (pq[i][0] < pq[minIdx][0]) minIdx = i;
    }
    const [d, u] = pq[minIdx];
    pq[minIdx] = pq[pq.length - 1];
    pq.pop();

    if (d > (dist.get(u) ?? Infinity)) continue;

    for (const [v, w] of Object.entries(graph[u] ?? {})) {
      const nd = d + w;
      if (nd < (dist.get(v) ?? Infinity)) {
        dist.set(v, nd);
        pq.push([nd, v]);
      }
    }
  }
  return dist;
}

function initEngine(stations: RawStation[]) {
  if (!_graph) {
    _graph = buildGraph(stations);
    _stationIndex = new Map(stations.map(s => [s.code, { lat: s.lat, lng: s.lng }]));
  }
}

function nearestStation(lat: number, lng: number): { code: string; distM: number } | null {
  let bestCode = '';
  let bestDist = Infinity;
  for (const [code, coords] of _stationIndex!.entries()) {
    const d = haversine(lat, lng, coords.lat, coords.lng);
    if (d < bestDist) { bestDist = d; bestCode = code; }
  }
  return bestCode ? { code: bestCode, distM: bestDist } : null;
}

const MAX_WALK_M = 800;

function computeCommute(propLat: number, propLng: number, tgtLat: number, tgtLng: number): number | null {
  const propStn = nearestStation(propLat, propLng);
  const tgtStn = nearestStation(tgtLat, tgtLng);
  if (!propStn || !tgtStn) return null;
  if (propStn.distM > MAX_WALK_M || tgtStn.distM > MAX_WALK_M) return null;

  const walkTime = walkingTimeMin(propStn.distM + tgtStn.distM);
  if (propStn.code === tgtStn.code) return walkTime;

  const dists = dijkstra(_graph!, propStn.code);
  const transitTime = dists.get(tgtStn.code) ?? Infinity;
  if (transitTime === Infinity) return null;

  return walkTime + transitTime;
}

// ============================================================
// Ranking
// ============================================================
function amenityScore(amenities: string[]): number {
  const weights: Record<string, number> = {
    pool: 0.15, gym: 0.12, bbq: 0.08, tennis: 0.08,
    function_room: 0.05, sauna: 0.07, jacuzzi: 0.06,
    sky_garden: 0.07, clubhouse: 0.05, yoga_deck: 0.05,
    reading_room: 0.03, basketball: 0.05, steam_room: 0.05,
    market: 0.08, food_court: 0.08, coffee_shop: 0.06,
    playground: 0.04, park: 0.06, clinic: 0.05,
    community_club: 0.04, sports_complex: 0.06, library: 0.05,
    convenience_store: 0.03,
    fully_furnished: 0.05, partial_furnished: 0.02,
  };
  return Math.min(amenities.reduce((s, a) => s + (weights[a] ?? 0.02), 0), 1.0);
}

function normalizeMinMax(values: number[]): number[] {
  if (values.length <= 1) return values.map(() => 0.5);
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) return values.map(() => 0.5);
  return values.map(v => (max - v) / (max - min));
}

interface RankableProperty {
  id: number;
  title: string;
  type: string;
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
  commuteTimes: Record<string, number>; // locationName -> minutes
  avgCommute: number | null;
  score: number;
}

function rankProperties(
  properties: RankableProperty[],
  weights?: { commute?: number; price?: number; amenity?: number }
): RankableProperty[] {
  const w = {
    commute: weights?.commute ?? 0.5,
    price: weights?.price ?? 0.3,
    amenity: weights?.amenity ?? 0.2,
  };

  const valid = properties.filter(p => p.avgCommute != null);
  const invalid = properties.filter(p => p.avgCommute == null);

  for (const p of invalid) p.score = 0;

  if (valid.length === 0) {
    return [...invalid, ...valid];
  }

  const normCommute = normalizeMinMax(valid.map(p => p.avgCommute!));
  const normPrice = normalizeMinMax(valid.map(p => p.rent));

  for (let i = 0; i < valid.length; i++) {
    const p = valid[i];
    p.score = w.commute * normCommute[i]
      + w.price * normPrice[i]
      + w.amenity * amenityScore(p.amenities);
  }

  valid.sort((a, b) => b.score - a.score);
  return [...valid, ...invalid];
}

// ============================================================
// Main search function (called from the app)
// ============================================================
export function performSearch(
  properties: RawProperty[],
  stations: RawStation[],
  locations: CommuteLocation[],
  filters: SearchFilters,
  weights?: { commute?: number; price?: number; amenity?: number },
): SearchResults {
  initEngine(stations);

  const ranked: RankableProperty[] = [];

  for (const p of properties) {
    // Apply filters
    if (filters.property_type && p.type !== filters.property_type) continue;
    if (filters.min_price != null && p.rent < filters.min_price) continue;
    if (filters.max_price != null && p.rent > filters.max_price) continue;
    if (filters.min_beds != null && p.beds < filters.min_beds) continue;
    if (filters.max_beds != null && p.beds > filters.max_beds) continue;

    const commuteTimes: Record<string, number> = {};
    for (const loc of locations) {
      if (loc.lat != null && loc.lng != null) {
        const t = computeCommute(p.lat, p.lng, loc.lat, loc.lng);
        if (t != null) commuteTimes[loc.name] = Math.round(t * 10) / 10;
      }
    }

    let avgCommute: number | null = null;
    const times = Object.values(commuteTimes);
    if (times.length > 0) {
      avgCommute = times.reduce((a, b) => a + b, 0) / times.length;
      if (filters.max_commute_min != null && avgCommute > filters.max_commute_min) continue;
    }

    ranked.push({
      id: p.id, title: p.title, type: p.type, address: p.address,
      lat: p.lat, lng: p.lng, rent: p.rent, beds: p.beds, baths: p.baths,
      sqft: p.sqft, furnished: p.furnished, amenities: p.amenities,
      mrt: p.mrt, mrt_dist: p.mrt_dist,
      commuteTimes, avgCommute, score: 0,
    });
  }

  const sorted = rankProperties(ranked, weights);

  return {
    results: sorted.map(p => ({
      id: p.id, title: p.title, property_type: p.type as 'hdb' | 'condo',
      address: p.address, lat: p.lat, lng: p.lng,
      monthly_rent: p.rent, bedrooms: p.beds, bathrooms: p.baths,
      sqft: p.sqft, furnished: p.furnished,
      nearest_mrt: p.mrt, nearest_mrt_dist: p.mrt_dist,
      commute_times: p.commuteTimes, score: Math.round(p.score * 10000) / 10000,
    })),
    total: sorted.length,
    stations: stations.map(s => ({
      name: s.name, code: s.code, line: s.line, lat: s.lat, lng: s.lng,
    })),
  };
}
