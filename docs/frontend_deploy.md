# Frontend Deploy

Backend URL: `https://cvfit.onrender.com`

That URL is the FastAPI backend service. Its root page serves the legacy Jinja fallback from `frontend/templates/` with static assets from `frontend/static/`. It is not the Next frontend.

The Next frontend lives in:

```powershell
frontend/
```

Deploy the Next frontend as its own service, preferably on Vercel or as a separate Render frontend service. The backend root fallback can remain in place for smoke-test and demo safety.

## Build

```powershell
cd frontend
npm install
npm run build
```

## Frontend Environment

Set this on the frontend hosting service:

```text
NEXT_PUBLIC_API_BASE_URL=https://cvfit.onrender.com
```

## Backend CORS

After the frontend is deployed, update the backend Render environment:

```text
CORS_ALLOWED_ORIGINS=https://<frontend-domain>
```

Do not include a trailing slash in the CORS origin.

For demos, use the deployed frontend domain once it exists. Use `https://cvfit.onrender.com` only as the backend API/Jinja fallback domain.
