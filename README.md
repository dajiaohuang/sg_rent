# SG Rent

Singapore rental housing recommendation system. Enter your commuting destinations, get ranked HDB and Condo properties by MRT-based commute time, price, and amenities.

**[Live Demo](https://dajiaohuang.github.io/sg_rent/)**

## Features

- **Multi-destination commute search** — up to 5 locations (work, school, etc.)
- **MRT-based routing** — Dijkstra shortest-path on all 6 MRT/LRT lines with transfer edges
- **Interactive map** — Leaflet with color-coded property markers and MRT station overlay
- **Smart ranking** — weighted scoring by commute time, price, and amenities
- **Filters** — property type, bedrooms, price range, max commute time
- **1,535 properties** — 115 real condo developments + 1,420 HDB blocks across 24 estates

## Quick Start

```bash
# Install and run locally
cd frontend
npm install
npm run dev
```

Open http://localhost:5173/sg_rent/

## Data

| Type | Count | Source |
|------|-------|--------|
| Condos | 115 | Real Singapore developments, placed near MRT stations by area |
| HDB blocks | 1,420 | Distributed across 24 HDB estates |
| MRT stations | 163 | NS, EW, NE, CC, DT, TE lines |

The static data lives in `frontend/public/data.json`. To refresh it from the Docker backend:

```bash
docker compose up -d
docker compose exec backend python -m app.ingest_script
docker compose exec backend python -m app.export_data
docker cp sg_rent-backend-1:/app/export.json frontend/public/data.json
```

## Architecture

Pure static frontend — no backend required at runtime. The commute engine (Dijkstra MRT routing), ranking algorithm, and all data run entirely in the browser.

```
frontend/src/engine/index.ts   # Commute engine + ranking (TypeScript)
frontend/public/data.json      # All property & station data (502 KB)
```

The Docker backend is only needed for data ingestion and management.

## Deployment

```bash
cd frontend
npm run build
npx gh-pages -d dist
```

Or push to `main` with GitHub Actions (requires `workflow` scope token).
