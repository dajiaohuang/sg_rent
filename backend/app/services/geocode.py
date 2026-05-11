import httpx
from app.config import settings


async def geocode_address(address: str) -> tuple[float, float] | None:
    """Geocode an address using OneMap API. Returns (lat, lng) or None."""
    url = f"{settings.onemap_api_url}/commonapi/search"
    params = {"searchVal": address, "returnGeom": "Y", "getAddrDetails": "Y"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if results:
                return float(results[0]["LATITUDE"]), float(results[0]["LONGITUDE"])
    except Exception:
        pass
    return None
