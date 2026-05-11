# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

SG Rent is a Singapore rental housing recommendation system. Users input commuting destinations and the system ranks nearby HDB and Condo properties by MRT-based commute time, price, and amenities. Results are displayed on an interactive Leaflet map.

**Two modes**: Docker-based backend + frontend (dev), and pure static frontend (GitHub Pages).

## Commands

```bash
# Start full stack (Docker)
docker compose up -d

# Frontend only dev (no backend needed)
cd frontend && npm install && npm run dev

# Build for GitHub Pages
cd frontend && npm run build

# Type check
cd frontend && npx tsc --noEmit

# Export fresh property data from Docker DB to static JSON
docker compose exec backend python -m app.export_data
docker cp sg_rent-backend-1:/app/export.json frontend/public/data.json
```

## Architecture

### Static Mode (GitHub Pages — primary)
- Everything runs in the browser
- `frontend/public/data.json` — 1535 properties + 163 MRT stations (502 KB, loaded on startup)
- `frontend/src/engine/index.ts` — TypeScript port of the commute engine and ranking
- No API calls, no backend

### Backend Mode (Docker — for data management)
- `POST /api/v1/search`, `GET /api/v1/properties`, `GET /api/v1/stations`
- PostgreSQL + PostGIS for spatial data, Redis for caching

### Commute Engine (`frontend/src/engine/index.ts`)

Dijkstra shortest-path on an MRT station graph:
- **Inter-station travel times** (~2-3 min between adjacent stations, hardcoded)
- **Transfer edges** (5 min penalty for interchanges at same-name stations)
- **Walking time** = haversine distance / 1.4 m/s, capped at 800m from station
- For each property→destination: walk to station + MRT transit + walk from station

### Ranking (same file)

Weighted min-max normalized scoring: commute=0.5, price=0.3, amenity=0.2.

### Data Sources

- `data/mrt_stations.json` — 163 MRT/LRT stations (NS, EW, NE, CC, DT, TE lines)
- `backend/app/ingest_script.py` — Generates 115 condos (real names, area-placed near MRT) + 1420 HDB blocks (distributed across 24 estates)
- `frontend/public/data.json` — Exported snapshot for static mode

## Data Pipeline

1. Edit `CONDO_LIST` / `HDB_ESTATES` in `backend/app/ingest_script.py`
2. Start Docker: `docker compose up -d`
3. Run: `docker compose exec backend python -m app.ingest_script`
4. Export: `docker compose exec backend python -m app.export_data && docker cp ... frontend/public/data.json`
5. Commit the updated data.json

## Project Conventions

- Coordinate order: (lat, lng) in frontend/types. Geoalchemy2 backend uses WKT (lng, lat).
- Property type is `"hdb"` or `"condo"` (lowercase).
- The `data.json` at frontend/public/ is the single source of truth for static mode — keep it committed.
