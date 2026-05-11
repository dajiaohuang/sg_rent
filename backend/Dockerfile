FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir \
    "fastapi>=0.115" \
    "uvicorn[standard]>=0.34" \
    "sqlalchemy[asyncio]>=2.0" \
    "asyncpg>=0.30" \
    "psycopg2-binary>=2.9" \
    "alembic>=1.14" \
    "redis>=5.2" \
    "httpx>=0.28" \
    "pydantic>=2.10" \
    "pydantic-settings>=2.7" \
    "geoalchemy2[shapely]>=0.15"

COPY . .
