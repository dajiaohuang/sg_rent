import json
import random
import math
from pathlib import Path

from app.models.property import MRTStation, Property
from app.config import settings
from geoalchemy2 import WKTElement


DATA_DIR = Path(__file__).parent.parent.parent / "data"

CONDO_NAMES = [
    "The Sail @ Marina Bay", "Reflections at Keppel Bay", "The Interlace",
    "d'Leedon", "Parc Esta", "Stirling Residences", "Avenue South Residence",
    "Normanton Park", "Penrose", "Treasure at Tampines", "The Florence Residences",
    "Jadescape", "Parc Clematis", "The Garden Residences", "Riverfront Residences",
    "Whistler Grand", "Twin VEW", "Mayfair Gardens", "Affinity at Serangoon",
    "The Woodleigh Residences", "Sengkang Grand Residences", "Piermont Grand",
    "The Tapestry", "The Alps Residences", "Coco Palms", "Watertown",
    "The Terrace", "Kingsford Waterbay", "High Park Residences", "The Wisteria",
    "Hundred Palms Residences", "Sol Acres", "Inz Residence", "The Visionaire",
    "The Brownstone", "Bellewoods", "Northwave", "Parc Life", "Watercove",
    "Seaside Residences", "The Glades", "Eco", "Sant Ritz", "Thomson Impressions",
    "Sky Vue", "Sky Habitat", "The Poiz Residences", "Stars of Kovan",
    "River Isles", "The Santorini", "Forest Woods", "The Clement Canopy",
    "Botanique at Bartley", "Kingsford Hillview Peak", "The Lanai",
    "The Minton", "The Quinn", "Watten House", "Dalvey Haus",
    "Boulevard 88", "South Beach Residences", "Wallich Residence",
    "Marina One Residences", "DUO Residences", "Principal Garden",
]

HDB_PREFIXES = ["Blk", "Block"]
HDB_STREETS = [
    "Ang Mo Kio Ave", "Bedok North St", "Bishan St", "Bukit Batok St",
    "Clementi Ave", "Hougang Ave", "Jurong East St", "Jurong West St",
    "Pasir Ris St", "Queenstown St", "Sengkang East Way", "Serangoon Ave",
    "Tampines St", "Toa Payoh Lor", "Woodlands St", "Yishun St",
    "Choa Chu Kang St", "Bukit Panjang Ring Rd", "Punggol Central",
    "Telok Blangah St",
]


def point_wkt(lat: float, lng: float) -> WKTElement:
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def load_mrt_stations() -> list[dict]:
    data_path = Path(settings.data_dir) / "mrt_stations.json"
    with open(data_path) as f:
        return json.load(f)


def create_mrt_seed() -> list[MRTStation]:
    stations = load_mrt_stations()
    seen = set()
    result = []
    for s in stations:
        key = (s["name"], s["code"])
        if key in seen:
            continue
        seen.add(key)
        result.append(MRTStation(
            name=s["name"],
            code=s["code"],
            line=s["line"],
            location=point_wkt(s["lat"], s["lng"]),
        ))
    return result


def generate_properties(stations: list[dict], count: int = 200) -> list[Property]:
    properties = []
    rng = random.Random(42)

    condo_amenities_pool = [
        ["pool", "gym", "bbq", "tennis", "playground"],
        ["pool", "gym", "function_room", "jacuzzi"],
        ["pool", "gym", "sauna", "bbq", "sky_garden"],
        ["pool", "gym", "bbq", "reading_room"],
        ["pool", "gym", "tennis", "basketball", "sauna", "jacuzzi"],
        ["pool", "gym"],
        ["pool", "gym", "bbq", "yoga_deck"],
        ["pool", "gym", "clubhouse", "steam_room", "bbq"],
    ]
    hdb_amenities_pool = [
        ["market", "food_court", "playground", "clinic"],
        ["market", "coffee_shop", "park", "community_club"],
        ["food_court", "playground", "convenience_store"],
        ["market", "park", "sports_complex", "library"],
    ]

    for i in range(count):
        station = rng.choice(stations)
        # Place property within 50-700m of a random MRT station
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(50, 700)
        lat_offset = (dist / 111320) * math.cos(angle)
        lng_offset = (dist / (111320 * math.cos(math.radians(station["lat"])))) * math.sin(angle)
        prop_lat = station["lat"] + lat_offset
        prop_lng = station["lng"] + lng_offset

        is_condo = rng.random() < 0.45
        property_type = "condo" if is_condo else "hdb"
        bedrooms = rng.choices([1, 2, 3, 4, 5], weights=[5, 30, 35, 20, 10])[0]
        bathrooms = max(1, min(bedrooms, rng.choices([1, 2, 3], weights=[30, 50, 20])[0]))

        if is_condo:
            sqft = bedrooms * rng.uniform(350, 550) + rng.uniform(0, 200)
            price_per_sqft = rng.uniform(3.5, 7.0)
            monthly_rent = round(sqft * price_per_sqft, -1)
            amenities = rng.choice(condo_amenities_pool).copy()
            if rng.random() < 0.3:
                amenities.append("partial_furnished")
                furnished = False
            else:
                amenities.append("fully_furnished")
                furnished = True
            title = rng.choice(CONDO_NAMES)
            blk = rng.randint(1, 999)
            address = f"{title}, #{rng.randint(1,40):02d}-{rng.randint(1,99):02d}, Singapore {rng.randint(100000, 799999)}"
        else:
            sqft = bedrooms * rng.uniform(200, 350) + rng.uniform(0, 100)
            price_per_sqft = rng.uniform(2.0, 4.5)
            monthly_rent = round(sqft * price_per_sqft, -1)
            amenities = rng.choice(hdb_amenities_pool).copy()
            furnished = rng.random() < 0.3
            if furnished:
                amenities.append("furnished")
            blk_num = rng.randint(1, 999)
            street = rng.choice(HDB_STREETS)
            unit = f"#{rng.randint(1,40):02d}-{rng.randint(1,999):03d}"
            address = f"Blk {blk_num} {street} {rng.randint(1,4)}, {unit}, Singapore {rng.randint(100000, 799999)}"
            title = f"Blk {blk_num} {street} {unit}"

        properties.append(Property(
            title=title,
            property_type=property_type,
            address=address,
            location=point_wkt(prop_lat, prop_lng),
            monthly_rent=monthly_rent,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            sqft=round(sqft),
            furnished=furnished,
            amenities=amenities,
            images=[],
            source="seed",
            source_id=str(i),
            nearest_mrt=station["name"],
            nearest_mrt_dist=round(dist),
        ))

    return properties
