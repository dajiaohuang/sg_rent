"""Export all properties and stations to static JSON for GitHub Pages."""
import asyncio
import json

from sqlalchemy import select
from geoalchemy2.shape import to_shape

from app.database import async_session
from app.models.property import Property, MRTStation


async def export():
    async with async_session() as db:
        props = (await db.execute(select(Property))).scalars().all()
        prop_data = []
        for p in props:
            pt = to_shape(p.location)
            prop_data.append({
                "id": p.id,
                "title": p.title,
                "type": p.property_type,
                "address": p.address,
                "lat": pt.y,
                "lng": pt.x,
                "rent": p.monthly_rent,
                "beds": p.bedrooms,
                "baths": p.bathrooms,
                "sqft": p.sqft,
                "furnished": p.furnished,
                "amenities": p.amenities or [],
                "mrt": p.nearest_mrt,
                "mrt_dist": p.nearest_mrt_dist,
            })

        stations = (await db.execute(select(MRTStation))).scalars().all()
        station_data = []
        for s in stations:
            pt = to_shape(s.location)
            station_data.append({
                "name": s.name,
                "code": s.code,
                "line": s.line,
                "lat": pt.y,
                "lng": pt.x,
            })

    output = {
        "properties": prop_data,
        "stations": station_data,
    }
    with open("/app/export.json", "w") as f:
        json.dump(output, f)
    print(f"Exported {len(prop_data)} properties, {len(station_data)} stations")


if __name__ == "__main__":
    asyncio.run(export())
