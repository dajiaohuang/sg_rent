"""
Bulk property data ingester for Singapore HDB and Condo locations.
Uses MRT station data as reference points for placing properties in realistic areas.
"""
import asyncio
import json
import math
import random

from sqlalchemy import select, func
from geoalchemy2 import WKTElement

from app.database import async_session
from app.models.property import Property

# Area name -> MRT station name mapping for condo placement
AREA_TO_STATION = {
    "Marina Bay": "Marina Bay",
    "Keppel Bay": "HarbourFront",
    "Gillman Heights": "Labrador Park",
    "Alexandra": "Queenstown",
    "Queenstown": "Queenstown",
    "Bukit Merah": "Redhill",
    "Redhill": "Redhill",
    "Telok Blangah": "Telok Blangah",
    "Tanjong Pagar": "Tanjong Pagar",
    "City Hall": "City Hall",
    "Bugis": "Bugis",
    "Chinatown": "Chinatown",
    "Outram": "Outram Park",
    "Normanton Park": "Kent Ridge",
    "Kent Ridge": "Kent Ridge",
    "One-North": "one-north",
    "Buona Vista": "Buona Vista",
    "Farrer Road": "Farrer Road",
    "Holland Village": "Holland Village",
    "Bukit Timah": "Botanic Gardens",
    "Newton": "Newton",
    "Orchard": "Orchard",
    "Balestier": "Toa Payoh",
    "Bishan": "Bishan",
    "Upper Thomson": "Upper Thomson",
    "Caldecott": "Caldecott",
    "Eunos": "Eunos",
    "Tampines": "Tampines",
    "Punggol": "Punggol",
    "Pasir Ris": "Pasir Ris",
    "Hougang": "Hougang",
    "Serangoon": "Serangoon",
    "Potong Pasir": "Potong Pasir",
    "Sengkang": "Sengkang",
    "Yishun": "Yishun",
    "Bedok": "Bedok",
    "Tanjong Katong": "Tanjong Katong",
    "Katong": "Tanjong Katong",
    "Tanjong Rhu": "Tanjong Rhu",
    "Woodleigh": "Woodleigh",
    "Sembawang": "Sembawang",
    "Woodlands": "Woodlands",
    "Ang Mo Kio": "Ang Mo Kio",
    "Clementi": "Clementi",
    "Jurong West": "Boon Lay",
    "Jurong Lake": "Lakeside",
    "Jurong East": "Jurong East",
    "Lakeside": "Lakeside",
    "Bartley": "Bartley",
    "Hillview": "Hillview",
    "Dairy Farm": "Hillview",
    "Choa Chu Kang": "Choa Chu Kang",
    "Canberra": "Canberra",
    "Kovan": "Kovan",
}

CONDO_LIST = [
    ("Marina One Residences", "Marina Bay"),
    ("The Sail @ Marina Bay", "Marina Bay"),
    ("Marina Bay Suites", "Marina Bay"),
    ("Reflections at Keppel Bay", "Keppel Bay"),
    ("Caribbean at Keppel Bay", "Keppel Bay"),
    ("The Interlace", "Gillman Heights"),
    ("Principal Garden", "Alexandra"),
    ("Stirling Residences", "Queenstown"),
    ("Commonwealth Towers", "Queenstown"),
    ("Queens Peak", "Queenstown"),
    ("Avenue South Residence", "Bukit Merah"),
    ("Artra", "Redhill"),
    ("Skyline Residences", "Telok Blangah"),
    ("Spottiswoode Residences", "Tanjong Pagar"),
    ("Wallich Residence", "Tanjong Pagar"),
    ("Altez", "Tanjong Pagar"),
    ("Lumiere", "Tanjong Pagar"),
    ("South Beach Residences", "City Hall"),
    ("The M", "Bugis"),
    ("DUO Residences", "Bugis"),
    ("Midtown Bay", "Bugis"),
    ("Midtown Modern", "Bugis"),
    ("The Landmark", "Chinatown"),
    ("One Pearl Bank", "Outram"),
    ("Sky Everton", "Outram"),
    ("Normanton Park", "Normanton Park"),
    ("Kent Ridge Hill Residences", "Kent Ridge"),
    ("One-North Eden", "One-North"),
    ("The Rochester", "Buona Vista"),
    ("d'Leedon", "Farrer Road"),
    ("Leedon Green", "Farrer Road"),
    ("Wilshire Residences", "Farrer Road"),
    ("Hyll on Holland", "Holland Village"),
    ("Van Holland", "Holland Village"),
    ("One Holland Village Residences", "Holland Village"),
    ("Mayfair Gardens", "Bukit Timah"),
    ("Mayfair Modern", "Bukit Timah"),
    ("The Atelier", "Newton"),
    ("Kopar at Newton", "Newton"),
    ("Pullman Residences Newton", "Newton"),
    ("Boulevard 88", "Orchard"),
    ("Park Nova", "Orchard"),
    ("Perfect Ten", "Bukit Timah"),
    ("Royalgreen", "Bukit Timah"),
    ("Juniper Hill", "Bukit Timah"),
    ("The Hyde", "Balestier"),
    ("Jadescape", "Bishan"),
    ("Sky Vue", "Bishan"),
    ("Sky Habitat", "Bishan"),
    ("Thomson Impressions", "Upper Thomson"),
    ("Parc Esta", "Eunos"),
    ("Treasure at Tampines", "Tampines"),
    ("Watertown", "Punggol"),
    ("Coco Palms", "Pasir Ris"),
    ("The Florence Residences", "Hougang"),
    ("Riverfront Residences", "Hougang"),
    ("Affinity at Serangoon", "Serangoon"),
    ("The Garden Residences", "Serangoon"),
    ("Forest Woods", "Serangoon"),
    ("Sant Ritz", "Potong Pasir"),
    ("The Poiz Residences", "Potong Pasir"),
    ("The Minton", "Hougang"),
    ("Kingsford Waterbay", "Sengkang"),
    ("Seaside Residences", "Bedok"),
    ("The Glades", "Tanjong Katong"),
    ("Amber Park", "Katong"),
    ("Coastline Residences", "Katong"),
    ("Meyer Mansion", "Katong"),
    ("The Line @ Tanjong Rhu", "Tanjong Rhu"),
    ("Pebble Bay", "Tanjong Rhu"),
    ("Water Place", "Tanjong Rhu"),
    ("The Tembusu", "Tampines"),
    ("The Alps Residences", "Tampines"),
    ("The Santorini", "Tampines"),
    ("Watercove", "Pasir Ris"),
    ("Sea Horizon", "Pasir Ris"),
    ("The Woodleigh Residences", "Woodleigh"),
    ("Symphony Suites", "Yishun"),
    ("North Park Residences", "Yishun"),
    ("Nine Residences", "Yishun"),
    ("Northwave", "Woodlands"),
    ("Parc Life", "Sembawang"),
    ("Riverbank @ Fernvale", "Sengkang"),
    ("High Park Residences", "Sengkang"),
    ("Luxus Hills", "Ang Mo Kio"),
    ("Panorama", "Ang Mo Kio"),
    ("Parc Clematis", "Clementi"),
    ("Clavon", "Clementi"),
    ("The Clement Canopy", "Clementi"),
    ("Whistler Grand", "Jurong West"),
    ("Twin VEW", "Jurong West"),
    ("Lake Grande", "Jurong Lake"),
    ("Lakeville", "Jurong Lake"),
    ("J Gateway", "Jurong East"),
    ("West Bay Condominium", "Jurong West"),
    ("The Lakefront Residences", "Lakeside"),
    ("The Trilinq", "Clementi"),
    ("Botanique at Bartley", "Bartley"),
    ("Kingsford Hillview Peak", "Hillview"),
    ("Hillview Regency", "Hillview"),
    ("The Skywoods", "Dairy Farm"),
    ("Sol Acres", "Choa Chu Kang"),
    ("Inz Residence", "Choa Chu Kang"),
    ("The Visionaire", "Canberra"),
    ("The Brownstone", "Canberra"),
    ("The Tapestry", "Tampines"),
    ("Stars of Kovan", "Kovan"),
    ("The Quinn", "Kovan"),
    ("Jansen 28", "Kovan"),
    ("Parc Colonial", "Woodleigh"),
    ("Park Colonial", "Woodleigh"),
    ("Piermont Grand", "Punggol"),
    ("Parc Central Residences", "Tampines"),
    ("The Wisteria", "Yishun"),
    ("Starlight Suites", "Serangoon"),
]

HDB_ESTATES = [
    ("Ang Mo Kio", 1.3700, 103.8495, 80),
    ("Bedok", 1.3239, 103.9303, 70),
    ("Bishan", 1.3509, 103.8485, 45),
    ("Bukit Batok", 1.3491, 103.7495, 55),
    ("Bukit Merah", 1.2860, 103.8271, 50),
    ("Bukit Panjang", 1.3786, 103.7637, 60),
    ("Choa Chu Kang", 1.3852, 103.7444, 70),
    ("Clementi", 1.3151, 103.7650, 45),
    ("Geylang", 1.3199, 103.8930, 35),
    ("Hougang", 1.3713, 103.8924, 70),
    ("Jurong East", 1.3331, 103.7422, 40),
    ("Jurong West", 1.3387, 103.7061, 80),
    ("Kallang", 1.3115, 103.8714, 30),
    ("Pasir Ris", 1.3724, 103.9495, 60),
    ("Punggol", 1.4046, 103.9020, 90),
    ("Queenstown", 1.2941, 103.8024, 40),
    ("Sembawang", 1.4490, 103.8187, 55),
    ("Sengkang", 1.3917, 103.8954, 85),
    ("Serangoon", 1.3500, 103.8734, 35),
    ("Tampines", 1.3532, 103.9452, 80),
    ("Tiong Bahru", 1.2860, 103.8271, 25),
    ("Toa Payoh", 1.3328, 103.8476, 50),
    ("Woodlands", 1.4369, 103.7864, 90),
    ("Yishun", 1.4294, 103.8352, 80),
]

def load_stations() -> dict[str, tuple[float, float]]:
    """Return dict of station_name -> (lat, lng) from MRT data."""
    from app.config import settings
    with open(f"{settings.data_dir}/mrt_stations.json") as f:
        raw = json.load(f)
    result = {}
    for s in raw:
        if s["name"] not in result:
            result[s["name"]] = (s["lat"], s["lng"])
    return result


def point_wkt(lat: float, lng: float) -> WKTElement:
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


async def ingest_condos():
    stations = load_stations()
    rng = random.Random(42)
    added = 0
    skipped = 0

    async with async_session() as db:
        for name, area in CONDO_LIST:
            result = await db.execute(
                select(func.count()).select_from(Property).where(
                    Property.title == name, Property.source == "condo_area"
                )
            )
            if result.scalar() > 0:
                skipped += 1
                continue

            station_name = AREA_TO_STATION.get(area)
            coords = stations.get(station_name) if station_name else None

            if not coords:
                print(f"  SKIP: {name} — no station for area '{area}'")
                continue

            center_lat, center_lng = coords
            # Place condo 100-800m from the MRT station
            angle = rng.uniform(0, 2 * math.pi)
            dist = rng.uniform(100, 800)
            lat = center_lat + (dist / 111320) * math.cos(angle)
            lng = center_lng + (dist / (111320 * math.cos(math.radians(center_lat)))) * math.sin(angle)

            bedrooms = rng.choices([1, 2, 3, 4, 5], weights=[5, 25, 40, 20, 10])[0]
            bathrooms = max(1, min(bedrooms, rng.choices([1, 2, 3], weights=[25, 50, 25])[0]))
            sqft = bedrooms * rng.uniform(300, 500) + rng.uniform(0, 300)
            f = rng.random() < 0.5

            db.add(Property(
                title=name,
                property_type="condo",
                address=f"{name}, Singapore",
                location=point_wkt(lat, lng),
                monthly_rent=round(sqft * rng.uniform(3.0, 7.0), -1),
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                sqft=round(sqft),
                furnished=f,
                amenities=["pool", "gym", "bbq"] + (["tennis"] if rng.random() < 0.5 else []),
                images=[],
                source="condo_area",
                source_id=f"condo_{name}",
                nearest_mrt=station_name,
                nearest_mrt_dist=round(dist),
            ))
            added += 1
            print(f"  [{added}] {name} → near {station_name} ({round(dist)}m)")

        if added > 0:
            await db.commit()
    print(f"Condos: {added} added, {skipped} skipped")


async def ingest_hdb_blocks():
    rng = random.Random(12345)
    added = 0

    async with async_session() as db:
        for estate_name, center_lat, center_lng, block_count in HDB_ESTATES:
            result = await db.execute(
                select(func.count()).select_from(Property).where(
                    Property.source == "hdb_estate",
                    Property.address.like(f"%{estate_name}%"),
                )
            )
            existing = result.scalar()
            remaining = block_count - existing
            if remaining <= 0:
                print(f"  SKIP: {estate_name} — already has {existing} blocks")
                continue

            for _ in range(remaining):
                angle = rng.uniform(0, 2 * math.pi)
                dist = rng.uniform(50, 1200)
                lat = center_lat + (dist / 111320) * math.cos(angle)
                lng = center_lng + (dist / (111320 * math.cos(math.radians(center_lat)))) * math.sin(angle)

                blk_num = rng.randint(1, 999)
                unit = f"#{rng.randint(2, 40):02d}-{rng.randint(1, 999):03d}"
                street_num = rng.randint(1, 6)
                address = f"Blk {blk_num} {estate_name} St {street_num}, {unit}, Singapore"
                bedrooms = rng.choices([1, 2, 3, 4, 5], weights=[3, 20, 40, 25, 12])[0]
                bathrooms = max(1, min(bedrooms, rng.choices([1, 2], weights=[50, 50])[0]))
                sqft = bedrooms * rng.uniform(180, 320) + rng.uniform(0, 80)

                db.add(Property(
                    title=f"Blk {blk_num} {estate_name} St {street_num} {unit}",
                    property_type="hdb",
                    address=address,
                    location=point_wkt(lat, lng),
                    monthly_rent=round(sqft * rng.uniform(1.8, 4.0), -1),
                    bedrooms=bedrooms,
                    bathrooms=bathrooms,
                    sqft=round(sqft),
                    furnished=rng.random() < 0.25,
                    amenities=rng.choice([
                        ["market", "food_court"], ["park", "playground"],
                        ["market", "park", "clinic"], ["coffee_shop", "park"],
                    ]),
                    images=[],
                    source="hdb_estate",
                    source_id=f"hdb_{estate_name}_{blk_num}",
                    nearest_mrt=estate_name,
                    nearest_mrt_dist=round(dist),
                ))
                added += 1
            print(f"  {estate_name}: {remaining} blocks added")

        if added > 0:
            await db.commit()
    print(f"HDB blocks: {added} added")


async def main():
    print("=== Ingesting Condos ===")
    await ingest_condos()
    print("\n=== Ingesting HDB Blocks ===")
    await ingest_hdb_blocks()


if __name__ == "__main__":
    asyncio.run(main())
