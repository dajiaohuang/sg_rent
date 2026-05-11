import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.property import Property, MRTStation
from app.models.search import SearchRequest, SearchResponse, PropertyResult
from app.services.commute import compute_commute, build_station_graph
from app.services.ranking import rank_properties
from app.services.geocode import geocode_address

router = APIRouter(prefix="/api/v1")

STATIONS_DATA: list[dict] = []


def _load_stations() -> list[dict]:
    global STATIONS_DATA
    if not STATIONS_DATA:
        with open(f"{settings.data_dir}/mrt_stations.json") as f:
            STATIONS_DATA = json.load(f)
    return STATIONS_DATA


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest, db: AsyncSession = Depends(get_db)):
    stations = _load_stations()
    graph = build_station_graph(stations)

    # Resolve geocoding for locations without lat/lng
    for loc in req.locations:
        if loc.lat is None or loc.lng is None:
            # Try station name match first (fast & reliable)
            match = next((s for s in stations if s["name"].lower() == loc.address.strip().lower()), None)
            if match:
                loc.lat, loc.lng = match["lat"], match["lng"]
            else:
                coords = await geocode_address(loc.address)
                if coords:
                    loc.lat, loc.lng = coords

    # Fetch properties from DB
    stmt = select(Property)
    if req.filters.property_type:
        stmt = stmt.where(Property.property_type == req.filters.property_type)
    if req.filters.min_price is not None:
        stmt = stmt.where(Property.monthly_rent >= req.filters.min_price)
    if req.filters.max_price is not None:
        stmt = stmt.where(Property.monthly_rent <= req.filters.max_price)
    if req.filters.min_beds is not None:
        stmt = stmt.where(Property.bedrooms >= req.filters.min_beds)
    if req.filters.max_beds is not None:
        stmt = stmt.where(Property.bedrooms <= req.filters.max_beds)

    result = await db.execute(stmt)
    properties = result.scalars().all()

    # Compute commute times
    # Extract lat/lng from PostGIS geography (returns WKT or extended WKB)
    prop_data = []
    for p in properties:
        # geoalchemy2 Geography columns return WKTElement; we need the coordinates
        lat, lng = _extract_coords(p)

        commute_times = {}
        for loc in req.locations:
            if loc.lat is not None and loc.lng is not None:
                t = compute_commute(lat, lng, loc.lat, loc.lng, stations, graph)
                if t is not None:
                    commute_times[loc.name] = round(t, 1)

        # Use average commute time for ranking
        if commute_times:
            avg_commute = sum(commute_times.values()) / len(commute_times)
        else:
            avg_commute = None

        prop_data.append({
            "id": p.id,
            "title": p.title,
            "property_type": p.property_type,
            "address": p.address,
            "lat": lat,
            "lng": lng,
            "monthly_rent": p.monthly_rent,
            "bedrooms": p.bedrooms,
            "bathrooms": p.bathrooms,
            "sqft": p.sqft,
            "furnished": p.furnished,
            "nearest_mrt": p.nearest_mrt,
            "nearest_mrt_dist": p.nearest_mrt_dist,
            "amenities": p.amenities,
            "commute_time": avg_commute,
            "commute_times": commute_times,
        })

    # Apply max_commute filter
    if req.filters.max_commute_min is not None:
        prop_data = [p for p in prop_data
                     if p["commute_time"] is not None and p["commute_time"] <= req.filters.max_commute_min]

    # Rank
    weights = req.weights
    ranked = rank_properties(prop_data, weights)

    # Build station list for map
    station_list = []
    seen = set()
    for s in stations:
        key = (s["name"], s["code"])
        if key in seen:
            continue
        seen.add(key)
        station_list.append({
            "name": s["name"],
            "code": s["code"],
            "line": s["line"],
            "lat": s["lat"],
            "lng": s["lng"],
        })

    results = [
        PropertyResult(
            id=p["id"],
            title=p["title"],
            property_type=p["property_type"],
            address=p["address"],
            lat=p["lat"],
            lng=p["lng"],
            monthly_rent=p["monthly_rent"],
            bedrooms=p["bedrooms"],
            bathrooms=p["bathrooms"],
            sqft=p["sqft"],
            furnished=p["furnished"],
            nearest_mrt=p["nearest_mrt"],
            nearest_mrt_dist=p["nearest_mrt_dist"],
            commute_times=p["commute_times"],
            score=round(p["score"], 4),
        )
        for p in ranked
    ]

    return SearchResponse(results=results, total=len(results), stations=station_list)


def _extract_coords(p: Property) -> tuple[float, float]:
    """Extract lat/lng from a geoalchemy2 Geography column."""
    loc = p.location
    if hasattr(loc, "data"):
        # WKBElement from geoalchemy2
        from geoalchemy2.shape import to_shape
        pt = to_shape(loc)
        return pt.y, pt.x
    # Fallback for string representation
    s = str(loc)
    # Format: "POINT(lng lat)" or "01010000..."
    if s.startswith("POINT"):
        parts = s.replace("POINT(", "").replace(")", "").split()
        return float(parts[1]), float(parts[0])
    return 0.0, 0.0
