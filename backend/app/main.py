from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func

from app.database import init_db, async_session
from app.models.property import Property, MRTStation
from app.api.routes import search, properties, transit
from app.seed import create_mrt_seed, generate_properties, load_mrt_stations


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_if_empty()
    yield


app = FastAPI(title="SG Rent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(properties.router)
app.include_router(transit.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


async def seed_if_empty():
    async with async_session() as db:
        result = await db.execute(select(func.count()).select_from(Property))
        count = result.scalar()
        if count == 0:
            # Seed MRT stations
            mrt_seeds = create_mrt_seed()
            db.add_all(mrt_seeds)
            await db.flush()

            # Seed properties
            stations_data = load_mrt_stations()
            prop_seeds = generate_properties(stations_data, count=200)
            db.add_all(prop_seeds)
            await db.commit()
