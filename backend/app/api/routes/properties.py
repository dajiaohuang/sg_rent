from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.property import Property
from app.models.search import PropertyResult

router = APIRouter(prefix="/api/v1")


@router.get("/properties")
async def list_properties(
    property_type: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    min_beds: int | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Property)
    if property_type:
        stmt = stmt.where(Property.property_type == property_type)
    if min_price is not None:
        stmt = stmt.where(Property.monthly_rent >= min_price)
    if max_price is not None:
        stmt = stmt.where(Property.monthly_rent <= max_price)
    if min_beds is not None:
        stmt = stmt.where(Property.bedrooms >= min_beds)

    result = await db.execute(stmt.limit(limit).offset(offset))
    properties = result.scalars().all()

    items = []
    for p in properties:
        lat, lng = _extract_coords(p)
        items.append(PropertyResult(
            id=p.id,
            title=p.title,
            property_type=p.property_type,
            address=p.address,
            lat=lat,
            lng=lng,
            monthly_rent=p.monthly_rent,
            bedrooms=p.bedrooms,
            bathrooms=p.bathrooms,
            sqft=p.sqft,
            furnished=p.furnished,
            nearest_mrt=p.nearest_mrt,
            nearest_mrt_dist=p.nearest_mrt_dist,
            commute_times={},
            score=0,
        ))
    return {"items": items, "total": len(items)}


@router.get("/properties/{property_id}")
async def get_property(property_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()
    if not prop:
        return {"error": "not found"}
    lat, lng = _extract_coords(prop)
    return PropertyResult(
        id=prop.id,
        title=prop.title,
        property_type=prop.property_type,
        address=prop.address,
        lat=lat,
        lng=lng,
        monthly_rent=prop.monthly_rent,
        bedrooms=prop.bedrooms,
        bathrooms=prop.bathrooms,
        sqft=prop.sqft,
        furnished=prop.furnished,
        nearest_mrt=prop.nearest_mrt,
        nearest_mrt_dist=prop.nearest_mrt_dist,
        commute_times={},
        score=0,
    )


def _extract_coords(p: Property) -> tuple[float, float]:
    loc = p.location
    if hasattr(loc, "data"):
        from geoalchemy2.shape import to_shape
        pt = to_shape(loc)
        return pt.y, pt.x
    s = str(loc)
    if s.startswith("POINT"):
        parts = s.replace("POINT(", "").replace(")", "").split()
        return float(parts[1]), float(parts[0])
    return 0.0, 0.0
