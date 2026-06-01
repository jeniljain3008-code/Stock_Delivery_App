# Smart Delivery Analytics & Swing Trading Platform

Production-oriented monorepo for an AI-powered NSE delivery analytics platform focused on detecting smart-money accumulation before price breakouts and finding 5–20% swing opportunities over a 1–8 week horizon.

## Architecture

```mermaid
flowchart LR
  U[Trader] --> F[Next.js Frontend]
  F -->|Firebase ID token| API[FastAPI API]
  API --> ING[Ingestion Service]
  API --> AN[Analytics Engine]
  API --> AI[AI Analyst]
  API --> REP[Reports]
  ING --> DB[(PostgreSQL)]
  AN --> DB
  REP --> DB
  SCH[Scheduler] --> ING
  SCH --> AN
  SCH --> REP
```

## Phased Delivery

### Phase 1 — MVP
- CSV/XLSX upload with schema validation.
- PostgreSQL persistence for OHLCV and delivery history.
- Dashboard, stock explorer, gold-stock scanner, and stock detail charts.
- Delivery-first accumulation score prioritizing NSE delivery quantity trends.

### Phase 2 — Advanced Analytics
- Relative strength against NIFTY, sector leadership, sector rotation heatmaps.
- Institutional buying detector and swing signal generation.
- Strategy backtesting with win rate, CAGR, profit factor, max drawdown, Sharpe ratio, and trade logs.

### Phase 3 — AI Analyst
- Natural-language explanations for accumulation, delivery surge, breakout readiness, and Gold Stocks membership.
- Daily AI market summary endpoint and report-ready prose.

### Phase 4 — Production Deployment
- Docker Compose for local production parity.
- GCP Cloud Run deployment guide, Cloud SQL Postgres, Secret Manager, Firebase Auth, Cloud Scheduler.

## Repository Structure

```text
frontend/      Next.js + TypeScript + Tailwind UI
backend/       FastAPI application, API routes, services, repositories
analytics/     Pandas/NumPy scoring, RS, sector, backtesting engines
ingestion/     File validation and parsing
database/      SQL schema and migrations seed data
reports/       Excel/PDF report generation helpers
ai_engine/     AI analyst prompt and deterministic explanation engine
sample_data/   Example NSE delivery dataset
tests/         Unit tests for ingestion and analytics
```

## Local Development Guide

See [`docs/LOCAL_DEVELOPMENT.md`](docs/LOCAL_DEVELOPMENT.md) for prerequisites, Docker setup, backend/frontend workflows, lint/test commands, sample upload instructions, API endpoint verification, and troubleshooting.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Open:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Local Backend Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/stock_delivery
uvicorn backend.app.main:app --reload
```

## Local Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Required Upload Fields

`Date, Symbol, Open, High, Low, Close, Volume, DeliveryQty, DeliveryPercent`

## Scoring Philosophy

The accumulation model intentionally weights delivery behavior above classic technical indicators:

- 40% Delivery Strength — delivery surge versus 1M/3M/6M averages, delivery percent expansion, and sustained rising delivery.
- 20% Price Strength — price above 20/50 DMA and controlled advance rather than exhausted spikes.
- 20% Volume Strength — above-average participation confirming institutional activity.
- 20% Trend Strength — 20/50/200 DMA alignment and breakout readiness.

The Gold Stocks scanner highlights stocks with current delivery quantity above 2x the one-month average, above 1.5x the three-month average, above 20/50 DMA, and volume above average.

## API Highlights

- `POST /api/v1/uploads/delivery-data`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/stocks`
- `GET /api/v1/stocks/{symbol}/analytics`
- `GET /api/v1/scanners/gold-stocks`
- `GET /api/v1/sectors/rotation`
- `POST /api/v1/backtests/run`
- `POST /api/v1/ai/ask`
- `GET /api/v1/reports/gold-stocks.xlsx`

## GCP Deployment Notes

1. Build frontend and backend containers with Cloud Build.
2. Deploy backend to Cloud Run with `DATABASE_URL`, Firebase project settings, and AI provider keys in Secret Manager.
3. Use Cloud SQL PostgreSQL with private IP.
4. Deploy frontend to Cloud Run or Firebase Hosting.
5. Trigger `/api/v1/jobs/daily-refresh` from Cloud Scheduler after NSE files are available.
6. Store uploaded files and generated reports in Cloud Storage.

## Disclaimer

This platform provides analytics and educational signals only. It is not investment advice. Always validate risk, liquidity, and position sizing before trading.
