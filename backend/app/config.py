from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://sg_rent:sg_rent_dev@localhost:5432/sg_rent"
    redis_url: str = "redis://localhost:6379/0"
    onemap_api_url: str = "https://developers.onemap.sg"
    data_dir: str = str(Path(__file__).parent.parent.parent / "data")

    # Commute scoring defaults
    commute_weight: float = 0.5
    price_weight: float = 0.3
    amenity_weight: float = 0.2
    walking_speed_mps: float = 1.4  # meters per second (~5 km/h)
    max_walk_to_station_m: int = 800  # don't consider properties >800m from MRT

    class Config:
        env_file = ".env"


settings = Settings()
