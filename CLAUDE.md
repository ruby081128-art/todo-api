# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Implemented: a FastAPI + Postgres (Render free plan in production, SQLite fallback for local dev) Todo REST API with JWT-based auth (each Todo belongs to the authenticated user). Stack choices made (package manager: pip + `requirements.txt`; ORM: SQLAlchemy).

## Commands

```bash
# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt

# Set a real secret in production — falls back to an insecure dev default otherwise
# export SECRET_KEY=<random-value>   (Render: set via render.yaml's generateValue)

# By default connects to local SQLite. To use Postgres locally, set DATABASE_URL
# to a postgres:// or postgresql:// connection string before running.

# Run (dev server with reload)
uvicorn app.main:app --reload

# Manual smoke test — no automated test suite exists yet
# Swagger UI at http://127.0.0.1:8000/docs once running
```

There is no linter, formatter, or automated test suite configured yet. If one is added, update this section with the exact commands (including how to run a single test).

## Architecture

Small layered FastAPI app under `app/`:

- `app/database.py` — SQLAlchemy engine/session setup. Reads `DATABASE_URL` from the environment (Render Postgres in production, provisioned via `render.yaml`'s `databases` section — free plan; Render's free Postgres instances expire 30 days after creation and must be recreated/reconnected manually); falls back to a local SQLite file `todos.db` in the project root when unset. A `postgres://` URL is rewritten to `postgresql://` since SQLAlchemy 2.0 requires the latter. Tables are created on first run via `Base.metadata.create_all` in `main.py` — no migrations/Alembic, so schema changes require dropping/recreating tables (delete the local `todos.db` for SQLite, or drop tables manually for Postgres).
- `app/models.py` — SQLAlchemy `User` and `Todo` models plus `PriorityEnum` (low/medium/high). Every `Todo` has a required `owner_id` FK to `User`. `tags` is stored as a JSON column (SQLite has no native array type).
- `app/schemas.py` — Pydantic v2 request/response models (`TodoCreate`, `TodoUpdate` with all-optional fields for partial updates, `TodoResponse`, `TodoListResponse` for the paginated list envelope, `UserCreate`/`UserResponse`/`Token` for auth).
- `app/auth.py` — password hashing (`bcrypt`, called directly rather than via `passlib` — `passlib`'s bcrypt backend detection is broken against `bcrypt>=4.1`, see https://github.com/pyca/bcrypt/issues/684), JWT creation/verification (`pyjwt`), and the `get_current_user` dependency (`OAuth2PasswordBearer`, reads `SECRET_KEY` from the environment — insecure dev default if unset).
- `app/crud.py` — DB access functions taking a `Session` and returning ORM objects; no business logic in the route handlers themselves. All todo functions take `owner_id` and scope every query to it.
- `app/main.py` — FastAPI app and route definitions; wires `Depends(get_db)` for per-request sessions and `Depends(auth.get_current_user)` on every `/todos` route. `GET /` serves `app/static/index.html` directly (`FileResponse`, not a `StaticFiles` mount — there's only the one file).
- `app/static/index.html` — vanilla-JS single-page UI. On load it calls `POST /auth/guest` if no token is in `localStorage`, then drives `/todos` with that token — no login screen. Guest tokens are anonymous, per-browser accounts (`guest-<uuid>@guest.local`, unguessable random password), so the todo list is scoped per browser/device, not shared.

Request flow: route handler in `main.py` → `crud.py` function (raw SQLAlchemy query against `models.Todo`, filtered by the current user's `owner_id`) → ORM object returned and serialized via the `schemas.py` response model. 404s are raised directly in `main.py` when `crud.get_todo` returns `None` (including when the todo exists but belongs to another user — this is deliberate, to avoid leaking existence); validation errors (422) are handled automatically by Pydantic/FastAPI; 401s come from `auth.get_current_user` for missing/invalid/expired tokens.

`GET /todos` supports pagination (`skip`/`limit`), a `completed` boolean filter, and substring search (`q`) across title/description — all implemented in `crud.list_todos`, always scoped to the authenticated user.

Auth flow: `POST /auth/register` (email + password) → `POST /auth/login` (OAuth2 password form: `username`=email, `password`) returns a JWT bearer token, 60 min expiry → send it as `Authorization: Bearer <token>` on every `/todos` request. `POST /auth/guest` (used by the static UI) skips registration entirely and issues a 30-day token for a freshly created anonymous account — `auth.create_access_token`'s `expire_minutes` param exists specifically for this longer guest expiry.
