from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography

from app.database import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    property_type: Mapped[str] = mapped_column(String(10))  # "hdb" or "condo"
    address: Mapped[str] = mapped_column(String(500))
    location: Mapped[str] = mapped_column(Geography("POINT", srid=4326))
    monthly_rent: Mapped[float] = mapped_column(Float)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[int] = mapped_column(Integer)
    sqft: Mapped[float | None] = mapped_column(Float, nullable=True)
    furnished: Mapped[bool] = mapped_column(Boolean, default=False)
    amenities: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    images: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="seed")  # "seed", "propertyguru", "99co"
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nearest_mrt: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nearest_mrt_dist: Mapped[float | None] = mapped_column(Float, nullable=True)  # meters
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MRTStation(Base):
    __tablename__ = "mrt_stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(10))  # e.g. "EW1", "NS2"
    line: Mapped[str] = mapped_column(String(50))   # e.g. "East-West Line", "North-South Line"
    location: Mapped[str] = mapped_column(Geography("POINT", srid=4326))


class CommuteCache(Base):
    __tablename__ = "commute_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(Integer)
    target_name: Mapped[str] = mapped_column(String(200))
    target_lat: Mapped[float] = mapped_column(Float)
    target_lng: Mapped[float] = mapped_column(Float)
    duration_min: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
