# Local Development Setup Guide

This guide helps contributors run the Smart Delivery Analytics & Swing Trading Platform locally, verify every API endpoint, and keep backend/frontend quality checks consistent.

## 1. Prerequisites

Install the following tools:

- Python 3.12+
- Node.js 22+
- Docker Desktop or Docker Engine with Compose v2
- PostgreSQL client tools, optional but useful for debugging
- Firebase project credentials, optional for local demo mode

## 2. Environment Configuration

From the repository root:

```bash
cp .env.example .env
```

For Docker Compose, the default `.env.example` values are enough to run locally. For direct backend execution, set:

```bash
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/stock_delivery
```

Firebase Auth is wired as a production-ready integration point. Local development accepts unauthenticated requests as `demo-user`; production should verify bearer tokens with Firebase Admin.

## 3. Run the Full Stack with Docker

```bash
docker compose up --build
```

Services:

- Frontend: <http://localhost:3000>
- Backend: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>
- PostgreSQL: `localhost:5432`

Stop services with:

```bash
docker compose down
```

Reset the database volume with:

```bash
docker compose down -v
```

## 4. Backend-Only Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Run backend checks:

```bash
ruff check .
python -m compileall backend analytics ingestion reports ai_engine tests
pytest -q
```

## 5. Frontend-Only Development

```bash
cd frontend
npm install
npm run dev
```

Run frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## 6. Upload Sample Delivery Data

Use the included sample file:

```bash
curl -X POST \
  -F "file=@sample_data/nse_delivery_sample.csv" \
  http://localhost:8000/api/v1/uploads/delivery-data
```

Required upload columns are:

```text
Date, Symbol, Open, High, Low, Close, Volume, DeliveryQty, DeliveryPercent
```

Extra columns such as `Sector` and `MarketCap` are allowed in the sample dataset for analytics enrichment.

## 7. Verify API Endpoints

Start the backend first, then run:

```bash
python scripts/verify_api_endpoints.py --base-url http://localhost:8000
```

The script checks:

- `GET /health`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/stocks`
- `GET /api/v1/stocks/BEL/analytics`
- `GET /api/v1/scanners/gold-stocks`
- `GET /api/v1/sectors/rotation`
- `POST /api/v1/backtests/run`
- `POST /api/v1/ai/ask`
- `POST /api/v1/jobs/daily-refresh`
- `GET /api/v1/reports/gold-stocks.xlsx`
- `POST /api/v1/uploads/delivery-data`

## 8. Development Workflow

1. Create a feature branch.
2. Update analytics/backend/frontend code in small, testable slices.
3. Run linting and tests before committing.
4. Verify API endpoints against a running backend.
5. Update documentation when setup, environment variables, or endpoints change.

## 9. Troubleshooting

### Dependency installation fails behind a proxy

Configure `pip`, `npm`, and Docker with your organization proxy settings, then retry dependency installation.

### Backend starts but dashboard endpoints fail

Confirm `sample_data/nse_delivery_sample.csv` exists and that `PYTHONPATH` points to the repository root when running without Docker.

### Upload fails with 422 validation errors

Verify that the file includes all required columns and that numeric columns do not contain commas, blanks, or negative values.
