# Production Deployment Guide: Vercel + Render + Supabase

This guide connects the imported GitHub repository to:

- **Frontend:** Vercel
- **Backend:** Render
- **Database:** Supabase PostgreSQL

> I cannot access your Vercel, Render, Supabase, or GitHub account credentials from this container, so I cannot click through the hosted dashboards or read the final generated URLs directly. The repository now includes the deployment configuration files those platforms need. Follow the steps below in your already-created accounts and then paste the generated URLs back into the environment variables where noted.

## 1. Supabase PostgreSQL

### Create or open your Supabase project

1. Open Supabase and select your project.
2. Go to **Project Settings → Database**.
3. Copy the **Session Pooler** or **Transaction Pooler** connection string, not the Direct Connection string.
4. The pooler URL is required for Render deployments because Supabase direct database hosts can resolve to IPv6 addresses, while some Render networking environments only have outbound IPv4. If you use a Direct Connection URL and see `Network is unreachable` for an IPv6 address, replace `DATABASE_URL` with the Supabase pooler connection string.
5. Convert the connection protocol for SQLAlchemy/psycopg if needed:
   - Supabase usually shows `postgresql://...`.
   - The backend accepts that format and normalizes it to `postgresql+psycopg://...` automatically.

### Apply the schema

Use one of these options:

#### Option A — Supabase SQL editor

1. Open **SQL Editor**.
2. Paste the contents of `database/schema.sql`.
3. Run the SQL.

#### Option B — Supabase CLI

```bash
supabase link --project-ref <your-project-ref>
supabase db push
```

The migration file is available at `supabase/migrations/20260601000000_initial_schema.sql`.

## 2. Deploy backend to Render

The root `render.yaml` defines a Docker web service named `smart-delivery-analytics-api`.

1. Open Render.
2. Choose **New → Blueprint**.
3. Select this GitHub repository.
4. Render should detect `render.yaml`.
5. Create the service.
6. Add these environment variables in Render:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | Supabase **Session Pooler** or **Transaction Pooler** PostgreSQL connection string, not Direct Connection |
| `DATABASE_CONNECT_TIMEOUT` | `10` |
| `DATABASE_POOL_RECYCLE_SECONDS` | `1800` |
| `DATABASE_SSLMODE` | Optional; use `require` if your hosted PostgreSQL URL requires TLS and does not already include SSL settings |
| `CORS_ORIGINS` | JSON list with your Vercel URL, for example `["https://your-frontend.vercel.app"]` |
| `FIREBASE_PROJECT_ID` | Firebase project ID, if Firebase Auth is enabled |
| `FIREBASE_CREDENTIALS_JSON` | Firebase service account JSON string, if Firebase Auth is enabled |
| `AI_PROVIDER` | `deterministic` |

7. Deploy.
8. Open the Render service URL and verify:

```bash
curl https://your-render-service.onrender.com/health
```

Expected response:

```json
{"status":"ok"}
```

## Supabase connection troubleshooting

If Render logs show an error like `connection to server at "...IPv6...", port 5432 failed: Network is unreachable`, the backend is healthy but Render cannot reach the Supabase Direct Connection host over IPv6. Fix it by updating Render's `DATABASE_URL` to the Supabase **Session Pooler** or **Transaction Pooler** connection string, then redeploy. The API now returns a clear `503` JSON response for database connectivity failures instead of an unhandled ASGI traceback.

## 3. Deploy frontend to Vercel

The frontend is a Next.js app inside `frontend/` and includes `frontend/vercel.json`.

1. Open Vercel.
2. Select the imported GitHub repository.
3. In **Project Settings → General**, set **Root Directory** to `frontend`.
4. Confirm framework is **Next.js**.
5. Add these environment variables:

| Variable | Value |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Render backend URL, for example `https://your-render-service.onrender.com` |
| `NEXT_TELEMETRY_DISABLED` | `1` |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase web API key, if Firebase Auth is enabled |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Firebase auth domain, if Firebase Auth is enabled |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project ID, if Firebase Auth is enabled |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Firebase storage bucket, if Firebase Auth is enabled |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Firebase messaging sender ID, if Firebase Auth is enabled |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Firebase app ID, if Firebase Auth is enabled |

6. Deploy.
7. Copy the Vercel production URL.

## 4. Connect frontend and backend CORS

After Vercel deploys, return to Render and update:

```text
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

Redeploy the Render service so the FastAPI CORS middleware allows browser requests from Vercel.

## 5. Final production smoke test

Replace the placeholders and run:

```bash
curl https://your-render-service.onrender.com/health
curl https://your-render-service.onrender.com/api/v1/dashboard/summary
curl https://your-render-service.onrender.com/api/v1/scanners/gold-stocks
curl -I https://your-frontend.vercel.app
```

Then open the frontend URL in a browser and verify the dashboard loads.

## Disable Next.js telemetry

The frontend explicitly sets `NEXT_TELEMETRY_DISABLED=1` in `frontend/package.json`, `frontend/vercel.json`, the frontend Docker image, Docker Compose, and `.env.example`. This suppresses the anonymous Next.js telemetry notice during Vercel and local builds.

## Deployment URL checklist

Fill these in after the hosted platforms finish provisioning:

| Component | URL |
| --- | --- |
| Frontend | `https://<your-vercel-project>.vercel.app` |
| Backend | `https://<your-render-service>.onrender.com` |
| Backend health check | `https://<your-render-service>.onrender.com/health` |
| Supabase project | `https://supabase.com/dashboard/project/<your-project-ref>` |

## Important notes

- Do not commit real Supabase passwords, Firebase credentials, or API keys.
- Use Supabase's pooled connection string for serverless/high-concurrency deployment.
- Use JSON syntax for `CORS_ORIGINS`, because the backend setting is a list.
- Render's free instances can sleep; the first request after inactivity may be slow.
