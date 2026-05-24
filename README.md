# base_fastapi

Lightweight fullstack FastAPI app built on a **clean architecture + CQRS** layout.

## Stack

- **FastAPI** + **uvicorn** — HTTP layer
- **Jinja2** + **HTMX** — server-rendered pages
- **SQLAlchemy (async)** + **asyncpg** — persistence
- **Alembic** — migrations
- **Pydantic v2** + **pydantic-settings** — schemas, DTOs, and config
- **PyJWT**, **bcrypt** — auth primitives
- **pytest** + **pytest-asyncio** — tests
- **ruff** — lint + format
- **uv** — dependency management (Python ≥ 3.13; pinned to 3.14)

## Architecture at a glance

Four layers with strict inward-only dependencies:

```
presentation → application → domain
              infrastructure ⤴  (implements domain/application interfaces)
```

```
src/
├── core/
│   ├── domain/         # entities, value objects, repository protocols, domain exceptions
│   └── application/    # commands, queries, handlers, DTOs, application exceptions (CQRS)
├── infrastructure/     # SQLAlchemy models + repos, services (JWT, bcrypt), config, migrations
└── presentation/       # FastAPI app
    ├── api/            # JSON API under /api/v1
    └── web/            # Jinja + HTMX pages + /static assets
tests/                  # mirrors src/, with in-memory fakes under tests/mocks/
```

**Core rules** (see `CLAUDE.md` for the full list):

1. 100% type annotations.
2. CQRS — every use case is a `Command` or `Query` with a dedicated handler (`CommandHandler[Cmd, Res]` / `QueryHandler[Q, Res]`).
3. Business logic lives only in `core/` (domain + application handlers).
4. Dependencies injected through `Protocol` interfaces; no concrete-class imports inside handlers.
5. APIs under `presentation/api/`; server-rendered pages under `presentation/web/`.
6. Repository interfaces in `core/domain/repositories/`; DB implementations in `infrastructure/database/repositories/`. Signatures take domain types (`Email`, `UserUUID`, `User`) — never raw strings or ORM models.
7. Exceptions are translated **once**, by the global handler in `presentation/exception_handlers.py`. No per-endpoint try/except.

## Getting started

```bash
# bootstrap venv + deps
make dev

# install pre-commit hooks
make pre-commit

# create .env (see .env.example — you'll need to create that manually; template below)
cp .env.example .env

# bring Postgres up
make db-up

# apply migrations
make migrate-up

# run the app (API on /api/v1/, pages on /)
make run
```

Open `http://localhost:8000/` for the HTMX-enabled index, and `http://localhost:8000/docs` for the OpenAPI UI.

### `.env.example` template

```
DATABASE_URL=postgresql+asyncpg://base_fastapi:base_fastapi@localhost:5432/base_fastapi
JWT_SECRET_KEY=replace-me-in-prod
JWT_ACCESS_TOKEN_LIFETIME=600
JWT_REFRESH_TOKEN_LIFETIME=86400
```

## Common tasks

```bash
make install-requirements         # uv sync
make ruff                         # ruff check --fix
uv run ruff format .
make tests                        # coverage run -m pytest -v -s
uv run pytest path/to/test.py::test_name
```

### Migrations

```bash
make migrate-new m="describe the change"
make migrate-up
make migrate-down   # rolls back the last revision
```

## Environment

Configuration is loaded from environment variables and `.env` by `src/infrastructure/config.py` (`pydantic-settings`). **Never commit `.env`.**
