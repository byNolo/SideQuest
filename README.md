# SideQuest

Small SideQuest web app with Flask API + Vite/React SPA, Redis, Postgres, and MinIO. Includes KeyN (byNolo) OAuth-like login integration.

## Prerequisites
- Docker + Docker Compose
- KeyN client credentials (Client ID + Secret)

## Quick Start
1. Copy `.env.example` → `.env` and fill required values:
   - `DATABASE_URL` (already set for local compose)
   - `PUBLIC_URL` (default `http://localhost:8080`)
   - `KEYN_AUTH_SERVER_URL` (default `https://auth-keyn.bynolo.ca`)
   - `KEYN_CLIENT_ID`, `KEYN_CLIENT_SECRET`
   - Optional cookie settings (`COOKIE_SECURE` should be `true` when using HTTPS)
2. Register redirect URI in KeyN to match:
   - `http://localhost:8080/api/auth/callback`
3. Start services:
```bash
docker compose up -d
```
4. Visit the app:
   - http://localhost:8080

## Common Commands
- View status and logs:
```bash
docker compose ps
docker compose logs -f proxy
```
- Build images:
```bash
docker compose build api web proxy
```
- Restart services after code/config changes:
```bash
docker compose restart api web proxy
```
- Recreate the web build (if UI changes don’t appear):
```bash
# Fully rebuild frontend and refresh the shared dist volume
docker compose stop proxy web
docker volume rm sidequest_webdist
docker compose build --no-cache web
docker compose up -d web proxy
```
- Recreate everything (fresh):
```bash
docker compose down
# Optional: remove volumes (DB, MinIO data will be wiped!)
# docker volume rm sidequest_dbdata sidequest_minio sidequest_webdist

docker compose up -d --build
```

## Auth (KeyN)
- Login endpoints are exposed by the API:
  - `GET /api/auth/login-url` → JSON with KeyN authorize URL
  - `GET /api/auth/login` → Redirects to KeyN
  - `GET /api/auth/callback` → Handles code, sets cookie
  - `GET /api/auth/me` → Returns `{ authenticated, user? }`
  - `POST /api/auth/logout` → Clears cookie
- Frontend shows a “Login with KeyN” button in the header when not authenticated.

## Service Ports
- UI via Nginx proxy: http://localhost:8080
- API (internal to Docker): `api:8000` (proxied at `/api/`)
- MinIO Console: exposed internally; configure `.env` to use MinIO programmatically

## Troubleshooting
- 502 from Nginx: ensure `api` service is up before `proxy`:
```bash
docker compose up -d db redis minio api
sleep 2
docker compose up -d proxy
```
- Login URL 500: check `.env` for `KEYN_CLIENT_ID`/`KEYN_CLIENT_SECRET` and that `PUBLIC_URL` is correct.
- UI changes not visible: rebuild `web` and reset `sidequest_webdist` volume (see above).

## Notes
- Dev server uses Flask’s built-in server; for production, swap to a WSGI server (e.g., gunicorn + proper health checks).
- See `notes/KEYN_INTEGRATION.md` for more KeyN details.