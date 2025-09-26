# SideQuest (Clean Rebuild)

This repository contains a fresh SideQuest scaffold:

- **Backend:** Flask 3 + SQLAlchemy + PostgreSQL
- **Frontend:** React 18 + Vite + Tailwind
- **Auth:** KeyN SSO integration stub with debug-header fallback

The goal is to provide a minimal, reliable starting point that you can iterate on quickly without fighting legacy scaffolding.

## Getting Started

1. Copy the environment template and edit values as needed:
   ```bash
   cp .env.example .env
   ```

2. Build and start the stack:
   ```bash
   make up
   ```

3. Visit the dev UI at <http://localhost:5173>. Set a debug username in the form and the UI will talk to the API using the `X-Debug-User` header so you can exercise the onboarding flow without OAuth.

4. Backend API is exposed on <http://localhost:8001>. Quick smoke tests:
   ```bash
   make api-health
   make onboarding-status
   ```

## Project Layout

```
api/         Flask application (app factory, routes, models)
web/         React + Vite frontend
notes/       Planning documents
ops/         Infrastructure configs (unused for now)
```

### Backend Highlights
- `app.py` registers a single blueprint (`/api/...`).
- `models/` currently defines `User` and `Location` with onboarding-friendly fields.
- `routes/onboarding.py` exposes:
  - `GET /api/me`
  - `PATCH /api/me/preferences`
  - `POST /api/me/location`
  - `POST /api/me/onboarding/complete-step`
  - `GET /api/me/onboarding/status`
  - `GET /api/geocode?q=...`
- `routes/quests.py` serves a placeholder quest for the current user.
- `auth.py` auto-provisions users when `X-Debug-User` is present and will validate KeyN JWTs when configured.

### Frontend Highlights
- Minimal React app for exercising onboarding status.
- Stores a chosen debug username in `localStorage` and sends it with every request.
- Tailwind is wired up for rapid iteration.

## Common Commands
- `make up` / `make down` — start or stop the stack.
- `make logs` — follow API logs.
- `make reset` — destroy DB volume and rebuild everything.
- `make web-dev` — run the Vite dev server directly on the host (optional).

## Development Notes
- Database migrations are not set up yet; SQLAlchemy auto-creates tables on start. Add Alembic once the schema stabilizes.
- Redis/MinIO/Celery were intentionally omitted from this reset; add them back when you need background work or object storage.
- KeyN OAuth routes are stubs—wire up the full flow once credentials and redirect URIs are finalized.

Happy building! 🚀
