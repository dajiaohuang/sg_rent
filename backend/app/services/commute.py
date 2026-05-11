import math
from app.config import settings

# Approximate inter-station travel times (minutes) between connected stations.
# Keyed by line, each is a list of (code1, code2, minutes) for adjacent stations.
INTER_STATION_TIMES: dict[str, list[tuple[str, str, float]]] = {
    "North-South Line": [
        ("NS1", "NS2", 2.5), ("NS2", "NS3", 2.0), ("NS3", "NS4", 2.5),
        ("NS4", "NS5", 2.5), ("NS5", "NS7", 3.0), ("NS7", "NS8", 2.5),
        ("NS8", "NS9", 2.0), ("NS9", "NS10", 2.5), ("NS10", "NS11", 3.0),
        ("NS11", "NS12", 2.0), ("NS12", "NS13", 2.5), ("NS13", "NS14", 2.0),
        ("NS14", "NS15", 3.5), ("NS15", "NS16", 2.5), ("NS16", "NS17", 3.0),
        ("NS17", "NS18", 2.0), ("NS18", "NS19", 2.0), ("NS19", "NS20", 2.5),
        ("NS20", "NS21", 2.0), ("NS21", "NS22", 2.0), ("NS22", "NS23", 2.0),
        ("NS23", "NS24", 2.0), ("NS24", "NS25", 2.0), ("NS25", "NS26", 2.0),
        ("NS26", "NS27", 2.0), ("NS27", "NS28", 3.0),
    ],
    "East-West Line": [
        ("EW1", "EW2", 3.0), ("EW2", "EW3", 2.5), ("EW3", "EW4", 2.5),
        ("EW4", "EW5", 2.5), ("EW5", "EW6", 2.0), ("EW6", "EW7", 2.0),
        ("EW7", "EW8", 2.0), ("EW8", "EW9", 2.0), ("EW9", "EW10", 2.0),
        ("EW10", "EW11", 2.0), ("EW11", "EW12", 2.0), ("EW12", "EW13", 2.0),
        ("EW13", "EW14", 2.0), ("EW14", "EW15", 2.0), ("EW15", "EW16", 2.0),
        ("EW16", "EW17", 2.0), ("EW17", "EW18", 2.0), ("EW18", "EW19", 2.5),
        ("EW19", "EW20", 2.0), ("EW20", "EW21", 2.0), ("EW21", "EW22", 2.0),
        ("EW22", "EW23", 2.5), ("EW23", "EW24", 3.0), ("EW24", "EW25", 2.5),
        ("EW25", "EW26", 2.5), ("EW26", "EW27", 2.5), ("EW27", "EW28", 2.5),
        ("EW28", "EW29", 2.5),
        ("EW4", "CG1", 3.0), ("CG1", "CG2", 4.0),
    ],
    "North East Line": [
        ("NE1", "NE3", 3.0), ("NE3", "NE4", 2.0), ("NE4", "NE5", 2.0),
        ("NE5", "NE6", 2.0), ("NE6", "NE7", 2.0), ("NE7", "NE8", 2.0),
        ("NE8", "NE9", 2.0), ("NE9", "NE10", 2.5), ("NE10", "NE11", 2.0),
        ("NE11", "NE12", 2.5), ("NE12", "NE13", 2.5), ("NE13", "NE14", 2.5),
        ("NE14", "NE15", 2.5), ("NE15", "NE16", 2.5), ("NE16", "NE17", 3.0),
    ],
    "Circle Line": [
        ("CC1", "CC2", 2.0), ("CC2", "CC3", 2.0), ("CC3", "CC4", 2.0),
        ("CC4", "CC5", 2.0), ("CC5", "CC6", 2.0), ("CC6", "CC7", 2.0),
        ("CC7", "CC8", 2.0), ("CC8", "CC9", 2.0), ("CC9", "CC10", 2.5),
        ("CC10", "CC11", 2.5), ("CC11", "CC12", 2.0), ("CC12", "CC13", 2.5),
        ("CC13", "CC14", 2.5), ("CC14", "CC15", 2.5), ("CC15", "CC16", 2.0),
        ("CC16", "CC17", 2.0), ("CC17", "CC19", 3.0), ("CC19", "CC20", 2.5),
        ("CC20", "CC21", 2.0), ("CC21", "CC22", 2.0), ("CC22", "CC23", 2.0),
        ("CC23", "CC24", 2.0), ("CC24", "CC25", 2.0), ("CC25", "CC26", 2.0),
        ("CC26", "CC27", 2.0), ("CC27", "CC28", 2.0), ("CC28", "CC29", 2.0),
    ],
    "Downtown Line": [
        ("DT1", "DT2", 2.0), ("DT2", "DT3", 2.0), ("DT3", "DT5", 3.0),
        ("DT5", "DT6", 2.5), ("DT6", "DT7", 2.0), ("DT7", "DT8", 2.0),
        ("DT8", "DT9", 2.0), ("DT9", "DT10", 2.5), ("DT10", "DT11", 2.5),
        ("DT11", "DT12", 2.0), ("DT12", "DT13", 2.0), ("DT13", "DT14", 2.0),
        ("DT14", "DT15", 2.5), ("DT15", "DT16", 2.5), ("DT16", "DT17", 2.0),
        ("DT17", "DT18", 2.0), ("DT18", "DT19", 2.0), ("DT19", "DT20", 2.0),
        ("DT20", "DT21", 2.0), ("DT21", "DT22", 2.0), ("DT22", "DT23", 2.0),
        ("DT23", "DT24", 2.0), ("DT24", "DT25", 2.0), ("DT25", "DT26", 2.0),
        ("DT26", "DT27", 2.0), ("DT27", "DT28", 2.0), ("DT28", "DT29", 2.5),
        ("DT29", "DT30", 2.0), ("DT30", "DT31", 2.5), ("DT31", "DT32", 2.5),
        ("DT32", "DT33", 2.5), ("DT33", "DT34", 2.5), ("DT34", "DT35", 2.5),
    ],
    "Thomson-East Coast Line": [
        ("TE1", "TE2", 3.0), ("TE2", "TE3", 3.0), ("TE3", "TE4", 3.5),
        ("TE4", "TE5", 3.0), ("TE5", "TE6", 2.5), ("TE6", "TE7", 2.5),
        ("TE7", "TE8", 2.5), ("TE8", "TE9", 3.0), ("TE9", "TE11", 3.0),
        ("TE11", "TE12", 2.5), ("TE12", "TE13", 2.5), ("TE13", "TE14", 2.0),
        ("TE14", "TE15", 2.5), ("TE15", "TE16", 2.0), ("TE16", "TE17", 2.0),
        ("TE17", "TE18", 2.0), ("TE18", "TE19", 2.0), ("TE19", "TE20", 2.0),
        ("TE20", "TE22", 3.0), ("TE22", "TE23", 2.5), ("TE23", "TE24", 2.5),
        ("TE24", "TE25", 3.0), ("TE25", "TE26", 2.5), ("TE26", "TE27", 2.5),
        ("TE27", "TE28", 3.0), ("TE28", "TE29", 3.0),
    ],
}


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance in meters."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def walking_time(meters: float) -> float:
    """Walking time in minutes."""
    return meters / settings.walking_speed_mps / 60


def build_station_graph(stations: list[dict]) -> dict[str, dict[str, float]]:
    """
    Build an adjacency graph of station code -> {neighbor_code: travel_time_min}.
    Uses inter-station times and adds transfer edges (walking) between
    stations with the same name (different codes).
    """
    graph: dict[str, dict[str, float]] = {}

    # Add edges from inter-station times
    for line, edges in INTER_STATION_TIMES.items():
        for c1, c2, t in edges:
            graph.setdefault(c1, {})[c2] = t
            graph.setdefault(c2, {})[c1] = t

    # Add transfer edges between stations with same name (different codes)
    name_to_codes: dict[str, list[str]] = {}
    for s in stations:
        name_to_codes.setdefault(s["name"], []).append(s["code"])

    for name, codes in name_to_codes.items():
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                transfer_time = 5.0  # ~5 min for line transfer
                graph.setdefault(codes[i], {})[codes[j]] = transfer_time
                graph.setdefault(codes[j], {})[codes[i]] = transfer_time

    return graph


def dijkstra(graph: dict[str, dict[str, float]], start: str) -> dict[str, float]:
    """Shortest path from start to all nodes."""
    import heapq
    dist = {start: 0}
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")):
            continue
        for v, w in graph.get(u, {}).items():
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def nearest_station(lat: float, lng: float, stations: list[dict]) -> tuple[dict, float]:
    """Find the nearest MRT station and its distance in meters."""
    best, best_dist = None, float("inf")
    for s in stations:
        d = haversine(lat, lng, s["lat"], s["lng"])
        if d < best_dist:
            best_dist = d
            best = s
    return best, best_dist


def compute_commute(
    prop_lat: float,
    prop_lng: float,
    target_lat: float,
    target_lng: float,
    stations: list[dict],
    station_graph: dict[str, dict[str, float]],
) -> float | None:
    """
    Compute total commute time from property to target in minutes.
    Returns None if either endpoint is too far (>max_walk_to_station_m) from an MRT.
    """
    prop_stn, prop_walk_m = nearest_station(prop_lat, prop_lng, stations)
    tgt_stn, tgt_walk_m = nearest_station(target_lat, target_lng, stations)

    if prop_walk_m > settings.max_walk_to_station_m:
        return None
    if tgt_walk_m > settings.max_walk_to_station_m:
        return None

    # If same station, just walking
    walk_time = walking_time(prop_walk_m + tgt_walk_m)

    if prop_stn["code"] == tgt_stn["code"]:
        return walk_time

    # Compute transit time via Dijkstra on MRT graph
    dists = dijkstra(station_graph, prop_stn["code"])
    transit_time = dists.get(tgt_stn["code"], float("inf"))

    if transit_time == float("inf"):
        return None

    return walk_time + transit_time
