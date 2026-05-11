from pydantic import BaseModel, Field


class CommuteLocation(BaseModel):
    name: str
    address: str = ""
    lat: float | None = None
    lng: float | None = None


class SearchFilters(BaseModel):
    max_price: float | None = None
    min_price: float | None = None
    min_beds: int | None = None
    max_beds: int | None = None
    property_type: str | None = None  # "hdb", "condo", or None for all
    max_commute_min: float | None = None


class SearchRequest(BaseModel):
    locations: list[CommuteLocation] = Field(min_length=1, max_length=5)
    filters: SearchFilters = Field(default_factory=SearchFilters)
    weights: dict[str, float] | None = None  # {"commute": 0.5, "price": 0.3, "amenity": 0.2}


class PropertyResult(BaseModel):
    id: int
    title: str
    property_type: str
    address: str
    lat: float
    lng: float
    monthly_rent: float
    bedrooms: int
    bathrooms: int
    sqft: float | None
    furnished: bool
    nearest_mrt: str | None
    nearest_mrt_dist: float | None
    commute_times: dict[str, float]  # {"Raffles Place": 25.5, "Orchard": 32.0}
    score: float

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    results: list[PropertyResult]
    total: int
    stations: list[dict]  # MRT stations for map overlay


class StationResponse(BaseModel):
    id: int
    name: str
    code: str
    line: str
    lat: float
    lng: float

    class Config:
        from_attributes = True
