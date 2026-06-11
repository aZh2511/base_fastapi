# CLAUDE.md

Compact reference for Claude Code (claude.ai/code) when working with this repository. Full detail and rationale live in [`GUIDELINES.md`](GUIDELINES.md). When this file disagrees with GUIDELINES, **GUIDELINES wins**.

## Project

Lightweight fullstack FastAPI app. Clean architecture + CQRS. Entry point: `src/presentation/http/main.py` (exposes `app`). Run with `uv run uvicorn --app-dir src presentation.http.main:app --reload` (or `make run`).

## Tooling

- **uv** for dependency management (`uv add`, `uv sync`, lockfile is `uv.lock`).
- Python **≥ 3.13** (`.python-version` currently pins 3.14).
- **ruff** for lint + format. Alembic versions dir is excluded.
- **pytest** with `pytest-asyncio` (`asyncio_mode = "auto"`, `pythonpath = "src"`).
- **PostgreSQL** via **SQLAlchemy (async)** + **asyncpg**. Migrations via **Alembic** (handwritten only — never `--autogenerate`).
- **Pydantic v2** + **pydantic-settings** for config.
- **Jinja2** + **HTMX** (CDN) for server-rendered pages.
- **httpx** (`AsyncClient` singleton on `app.state`) for outbound HTTP.
- **PyJWT** + **bcrypt** for auth primitives.

## Common commands

```bash
make run                          # uv run uvicorn --app-dir src presentation.http.main:app --reload
make db-up                        # docker compose up -d postgres
make migrate-up                   # alembic upgrade head
make migrate-new m="description"  # alembic revision -m "description"  (handwritten)

make install-requirements         # uv sync
make dev                          # wipe .venv, recreate, sync (dev deps)
make prod                         # wipe .venv, recreate, sync --no-dev

make ruff                         # ruff check --fix
uv run ruff format .

make tests                        # coverage run -m pytest -v -s
uv run pytest path/to/test.py::test_name
uv run pytest -m integration      # real-DB / real-service tests (opt in)
```

## Architecture — clean layers + CQRS

Four layers. **Dependencies point inward only**: `presentation → application → domain`; `infrastructure → application/domain` (implements their interfaces). `domain` imports nothing from the other layers.

```
src/
├── core/
│   ├── domain/                # Pure business. Zero framework/DB/pydantic imports.
│   │   ├── entities/          # Dataclasses. Business objects + invariants.
│   │   ├── value_objects.py   # Frozen slotted dataclasses (UserUUID, Email, Password). Validate in __post_init__.
│   │   ├── repositories/      # Protocol interfaces (IUserRepository, ...). NO implementations.
│   │   ├── interfaces.py      # Other domain-service protocols (IPasswordHasher, ...).
│   │   └── exceptions.py      # DomainException and subclasses.
│   └── application/           # Use-case orchestration (CQRS).
│       ├── commands/          # Write intents. Pydantic BaseModel subclasses of `Command`.
│       ├── queries/           # Read intents. Subclass `Query`; sibling `*Result(BaseResultDTO)` class.
│       ├── handlers/
│       │   ├── base.py        # CommandHandler[CmdT, CmdResultT], QueryHandler[QueryT, QueryResultT].
│       │   ├── commands/      # Handlers for write intents.
│       │   └── queries/       # Handlers for read intents.
│       ├── interfaces.py      # Application-service protocols (IDBSession, IJWTService).
│       ├── dto.py             # Cross-layer data carriers (dataclasses). JWTToken is a NewType.
│       └── exceptions.py      # ApplicationException, AuthenticationFailed.
├── infrastructure/            # Concrete implementations of domain/application interfaces.
│   ├── config.py              # pydantic-settings BaseSettings — single flat Config, .env loaded.
│   ├── database/
│   │   ├── models/            # SQLAlchemy ORM models. Never leak into domain/application.
│   │   ├── repositories/      # SQL* classes implementing IRepository protocols. Translate ORM → domain entity.
│   │   ├── db_session.py      # Engine + session maker.
│   │   └── alembic/           # Migrations (env.py reads Config().database_url).
│   └── services/              # JWTService (translates PyJWT errors → AuthenticationFailed), PasswordHasher (bcrypt).
└── presentation/              # Delivery mechanisms. Siblings are mutually isolated.
    ├── http/                  # FastAPI app.
    │   ├── main.py            # create_app(): Config, logging, lifespan, CORS, exception handlers, /static, routers.
    │   ├── wiring.py          # Shared DI: get_config (lru_cache), get_db_session, get_jwt_service, get_http_client, typed aliases.
    │   ├── exception_handlers.py  # DomainException / ApplicationException → HTTP via type-status map.
    │   ├── api/
    │   │   ├── router.py      # api_router = APIRouter(prefix="/api/v1") aggregates feature routers.
    │   │   ├── dependencies.py    # API auth (Bearer → 401). Exposes AuthenticatedUser.
    │   │   └── <feature>/
    │   │       ├── endpoints.py   # Routes. Build Command/Query, call handler, return schema response.
    │   │       ├── providers.py   # Per-feature DI wiring: FastAPI Depends() factories that assemble handlers.
    │   │       └── schemas.py     # Pydantic request/response models (NOT commands/queries).
    │   └── web/
    │       ├── router.py      # Jinja2Templates + web routes that render HTML.
    │       ├── dependencies.py    # Web auth (cookie → 303 redirect to /login).
    │       ├── templates/     # Jinja templates (base.html, index.html, ...).
    │       └── static/        # Served at /static (CSS, images, client JS).
    ├── scripts/               # Standalone CLIs. Module-private files prefixed with `_`. Run via `python -m presentation.scripts.<name>`.
    └── playground/            # Local experiments. Never imported elsewhere.
tests/                         # Mirror src/. tests/mocks/ for in-memory fakes of Protocol interfaces.
```

## Layer import rules

1. **`core/domain/` → stdlib only.** No pydantic, no infra, no presentation.
2. **`core/application/` → `core.domain` + `pydantic`.** Never infrastructure or presentation.
3. **`infrastructure/` → `core.*`.** Never presentation.
4. **`presentation/` → `core.*` and `infrastructure.*`** — but handler deps are declared as **Protocols**, not concrete classes.
5. **Presentation siblings are isolated.** `http/`, `scripts/`, `playground/` must NOT import from each other.
6. **Within `http/`, `api/` and `web/` are isolated.** They share only `http/wiring.py`, `http/exception_handlers.py`, and the lifespan in `http/main.py`. Only `main.py` may include routers from both.

## Non-negotiable rules

1. **100% type annotations.** No untyped `def`, no implicit `Any`. Use `Protocol` for interfaces. Prefer `X | None`. Never `# type: ignore` to escape a typing problem.
2. **CQRS.** Every use case is a Command or Query with a matching handler subclassing `CommandHandler[Cmd, Res]` / `QueryHandler[Q, Res]`.
3. **Business logic lives in `core/domain/` only.** Application handlers orchestrate; presentation and infrastructure contain no business rules.
4. **Dependency injection, always.** Handlers receive collaborators as constructor arguments typed as **Protocols**, never concrete classes.
5. **Repositories return domain entities**, not ORM models or raw IDs. Protocol interfaces in `core/domain/repositories/`; SQL implementations in `infrastructure/database/repositories/`.
6. **Bounded flows.** Each use case owns its command/handler. Outer handlers depend on inner handlers, not on the inner handler's private collaborators. Don't reuse one command across flows.
7. **One commit per use-case.** Each command handler ends with one `await self._db_session.commit()`. Use `flush()` (not `commit()`) inside a handler if you need an FK to be assigned before subsequent inserts.
8. **DB tables, not files, for runtime-mutable data.** Files only seed.
9. **Imports at the top of the file.** No bottom-of-file or in-function imports. Use `if TYPE_CHECKING:` for forward refs.
10. **One facade + one API client per external service.** No sync/async dual wrappers — prefer the SDK's async client.
11. **Constants → config or constants module.** Hoist hard-coded paths/URLs/timeouts into `Config` (env-tunable) or a constants module.
12. **Presentation siblings are isolated.** `http/`, `scripts/`, `playground/` must not import from each other. Within `http/`, `api/` ↔ `web/` are isolated.
13. **Exceptions translated once, centrally.** No per-endpoint try/except ladders. Add a new exception class + a row in `_EXCEPTION_STATUS_MAP`.
14. **Infrastructure translates its own errors.** Library-specific exceptions are caught inside the infrastructure service and re-raised as `ApplicationException` / `DomainException` subclasses. Application handlers never `import jwt`, `import sqlalchemy`, etc.
15. **TDD, inside-out.** For every feature: domain → application → infrastructure → presentation. At each layer, write tests first, watch them fail, then implement. Test **business behavior**, not mock-call wiring.
16. **Don't reinvent the wheel.** Before hand-rolling a non-trivial utility, check PyPI and the project's existing dependencies for a maintained library that already solves the problem. Prefer `uv add <pkg>` over a from-scratch implementation. The stdlib is the right default for trivial helpers, not a hard ceiling — reach for `httpx`, `tenacity`, `structlog`, `python-slugify`, `pendulum`, `email-validator`, etc., when they fit. Note the library choice (or the conscious decision to avoid one) in the PR description.

## Conventions (pointers — full detail in GUIDELINES.md)

- **Value objects** — frozen slotted dataclasses, invariants in `__post_init__`, raise `DomainException` subclasses (§6).
- **Central exception map** — `presentation/http/exception_handlers.py`. Add an exception class + a `_EXCEPTION_STATUS_MAP` row (§10).
- **Transactions** — session injected as `IDBSession`; lifecycle owned by `get_db_session` in `presentation/http/wiring.py` (§9.2).
- **Schemas vs. commands** — `schemas.py` holds HTTP-facing Pydantic models with `ConfigDict(extra="forbid")`; the endpoint builds a Command/Query from the schema payload (§9.3).
- **Repositories** translate ORM rows to domain entities (`_to_entity`). Signatures take domain types (`Email`, `UserUUID`) — never raw `str` IDs (§8).
- **Queries return sibling `*Result` DTOs**, not nested inner classes — `GetMeQuery` + `GetMeResult` side by side (§7).
- **Config is flat.** `Config(BaseSettings)` exposes aliased env vars at the top level. Services take the whole `Config` and read the fields they need; no nested settings sub-objects (§8).
- **External services** — one facade + one API client per service; library errors translated at the facade boundary (§8).
- **Background tasks** open a fresh DB session via the session maker (§8).
- **Tests mirror src/**; fakes live under `tests/mocks/` at the path of the Protocol they implement (§12).
- `__init__.py` files re-export public symbols (`from core.application.commands import Command`).

## Notes

- `CLAUDE.md` is intentionally untracked locally; `.env` is gitignored.
- `.env.example` is checked in; create `.env` from it (`cp .env.example .env`) and edit values.
- Run order from a fresh clone: `make dev && cp .env.example .env && make db-up && make migrate-up && make run`.

## Knowledge workflow

This project uses a structured knowledge ecosystem. Every session follows it.

1. **Start with `/plan-feature`** for any non-trivial new work — features, behavior changes, new domain rules. Skip only for typo fixes, single-line bug fixes, or mechanical refactors. When in doubt, ask the user once: "fix or new feature?"
2. **Before settling on an approach, call `/recall`** to surface relevant prior business and architecture knowledge. If `recall` flags a conflict between the proposed work and an existing invariant or pattern, resolve it with the user before continuing.
3. **TDD from the plan's Given/When/Then scenarios.** The plan's "Business scenarios" section IS the test contract. Write failing tests for those scenarios first, layer by layer (inside-out).
4. **When the feature ships, run `/learn`** to persist business + architecture knowledge into `.claude/knowledge/`. Business and architecture are written to two separate files and cross-linked — architecture entries are written to stand alone without business context so they're portable to other projects.
5. **When backend work needs UI, run `/handover-frontend`** to produce a handover doc under `docs/handovers/` that the FE team can pick up without context.
6. **At session end, evaluate** whether `/learn` or `/handover-frontend` is owed. The Stop hook will remind you; act on it if appropriate.

Knowledge base layout:

```
.claude/knowledge/
├── INDEX.md              # the only thing always in context; keep under ~200 lines
├── business/<slug>.md    # what the system does, invariants, scenarios
└── architecture/<slug>.md # patterns, rationale, trade-offs — written without business context

docs/handovers/<YYYY-MM-DD>-<slug>.md   # backend → frontend contracts
```
