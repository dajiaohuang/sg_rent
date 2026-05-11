import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.property import MRTStation

router = APIRouter(prefix="/api/v1")

STATIONS_CACHE: list[dict] = []


def _get_stations() -> list[dict]:
    global STATIONS_CACHE
    if not STATIONS_CACHE:
        with open(f"{settings.data_dir}/mrt_stations.json") as f:
            raw = json.load(f)
        seen = set()
        for s in raw:
            key = (s["name"], s["code"])
            if key not in seen:
                seen.add(key)
                STATIONS_CACHE.append(s)
    return STATIONS_CACHE


@router.get("/stations")
async def list_stations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MRTStation))
    db_stations = result.scalars().all()
    if db_stations:
        items = []
        for s in db_stations:
            loc = s.location
            lat, lng = 0.0, 0.0
            if hasattr(loc, "data"):
                from geoalchemy2.shape import to_shape
                pt = to_shape(loc)
                lat, lng = pt.y, pt.x
            items.append({
                "id": s.id,
                "name": s.name,
                "code": s.code,
                "line": s.line,
                "lat": lat,
                "lng": lng,
            })
        return {"items": items}
    return {"items": _get_stations()}


@router.get("/stations/lines")
async def list_lines():
    lines = {}
    for s in _get_stations():
        lines.setdefault(s["line"], []).append({
            "name": s["name"],
            "code": s["code"],
            "lat": s["lat"],
            "lng": s["lng"],
        })
    return {"lines": lines}
