# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Implemented: a FastAPI + SQLite Todo REST API. Stack choices made (package manager: pip + `requirements.txt`; ORM: SQLAlchemy).

## Commands

```bash
# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt

# Run (dev server with reload)
uvicorn app.main:app --reload

# Manual smoke test — no automated test suite exists yet
# Swagger UI at http://127.0.0.1:8000/docs once running
```

There is no linter, formatter, or automated test suite configured yet. If one is added, update this section with the exact commands (including how to run a single test).

## Architecture

Small layered FastAPI app under `app/`:

- `app/database.py` — SQLAlchemy engine/session setup. SQLite file `todos.db` is created in the project root on first run (`Base.metadata.create_all` in `main.py`, no migrations/Alembic).
- `app/models.py` — SQLAlchemy `Todo` model plus `PriorityEnum` (low/medium/high). `tags` is stored as a JSON column (SQLite has no native array type).
- `app/schemas.py` — Pydantic v2 request/response models (`TodoCreate`, `TodoUpdate` with all-optional fields for partial updates, `TodoResponse`, `TodoListResponse` for the paginated list envelope).
- `app/crud.py` — DB access functions taking a `Session` and returning ORM objects; no business logic in the route handlers themselves.
- `app/main.py` — FastAPI app and route definitions; wires `Depends(get_db)` for per-request sessions.

Request flow: route handler in `main.py` → `crud.py` function (raw SQLAlchemy query against `models.Todo`) → ORM object returned and serialized via the `schemas.py` response model. 404s are raised directly in `main.py` when `crud.get_todo` returns `None`; validation errors (422) are handled automatically by Pydantic/FastAPI.

`GET /todos` supports pagination (`skip`/`limit`), a `completed` boolean filter, and substring search (`q`) across title/description — all implemented in `crud.list_todos`.
