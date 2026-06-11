# GUIDELINES.md — Starter Architecture Guide

A starting blueprint for a new Python web service. Copy this file to the new repo's root, then delete sections that don't apply.

The guide is **opinionated and Python+FastAPI specific**. Every rule below has been battle-tested in a real codebase. Deviate consciously, not accidentally.

---

## Table of contents

1. [Tooling defaults](#1-tooling-defaults)
2. [Required project files](#2-required-project-files)
3. [Layered architecture](#3-layered-architecture)
4. [Layer import rules](#4-layer-import-rules)
5. [Directory scaffold](#5-directory-scaffold)
6. [Domain layer conventions](#6-domain-layer-conventions)
7. [Application layer / CQRS](#7-application-layer--cqrs)
8. [Infrastructure layer](#8-infrastructure-layer)
9. [Presentation layer](#9-presentation-layer)
10. [Exception handling](#10-exception-handling)
11. [Feature workflow — TDD, inside-out](#11-feature-workflow--tdd-inside-out)
12. [Testing](#12-testing)
13. [Naming conventions](#13-naming-conventions)
14. [Type discipline](#14-type-discipline)
15. [Non-negotiable rules](#15-non-negotiable-rules)
16. [Copy-paste starter scaffold](#16-copy-paste-starter-scaffold)
17. [Verification](#17-verification)

---

## 1. Tooling defaults

| Concern | Choice | Why |
|---|---|---|
| Python version | **≥ 3.13** | Modern typing — `X \| None`, `StrEnum`, `TypeGuard`, `Self`. |
| Package manager | **uv** | Fast, deterministic; replaces pip + venv. `uv sync`, `uv add`, `uv run`. |
| Lint + format | **ruff** | Single tool — replaces flake8 + black + isort. |
| Test runner | **pytest** + **pytest-asyncio** | `asyncio_mode = "auto"`, `asyncio_default_fixture_loop_scope = "function"`. |
| Web framework | **FastAPI** + **uvicorn** (dev) + **gunicorn** (prod) | Async, type-driven, OpenAPI for free. |
| ORM | **SQLAlchemy 2.x async** + **asyncpg** (Postgres) | First-class async, mature ecosystem. |
| Migrations | **Alembic** | Handwritten only; never `--autogenerate`. |
| Validation / config | **Pydantic v2** + **pydantic-settings** | Type-first, integrates with FastAPI. |
| HTTP client | **httpx** `AsyncClient` (singleton on `app.state`) | Async, supports event hooks. |
| Auth primitives | **PyJWT** + **bcrypt** | Standard, no over-engineered framework. |
| Templating | **Jinja2** | Server-side HTML or text rendering (prompts, emails). |

**Makefile** holds environment commands only (`make dev`, `make prod`, `make ruff`). App, test, and migration commands run directly via `uv` — don't hide them behind Make.

`pyproject.toml` is the single source for dependencies + tool config. Keep `[tool.ruff]` minimal — let ruff defaults handle the rules.

**The library table above is a starting point, not a ceiling.** Before hand-rolling a non-trivial utility, check PyPI and the project's existing deps for something maintained. Lean on the ecosystem (`httpx`, `tenacity`, `structlog`, `python-slugify`, `pendulum`, `email-validator`, etc.) before writing a new helper from scratch. See rule 16 in §15.

---

## 2. Required project files

| File | Purpose |
|---|---|
| `pyproject.toml` | Deps + tool config (ruff, pytest, coverage). |
| `uv.lock` | Pinned versions. Commit it. |
| `Makefile` | Env setup only. |
| `alembic.ini` | At repo root; `script_location = src/infrastructure/database/alembic`. |
| `CLAUDE.md` | Project overview for AI assistants — layer rules, common commands, env vars table. |
| `.env` | Local secrets. **NEVER commit.** Must be in `.gitignore`. |
| `.env.example` | Template with placeholders. Checked in. |
| `.gitignore` | Includes `.env`, `.venv/`, `__pycache__/`, `dist/`, `node_modules/`. |
| `GUIDELINES.md` | This file. |

**Never publish secrets.** Before any commit, verify no `.env` or credentials are staged.

---

## 3. Layered architecture

Four layers. Dependencies point inward only.

```
┌─ presentation ─────────────────────────────────┐
│  http (api/, web/), scripts/, playground/      │
│  ↓                                              │
├─ infrastructure ──────────────────────────────┐│
│  config, database (ORM, repos), services       ││
│  ↓                                              ││
├─ application (CQRS) ──────────────────────────┐│
│  commands, queries, handlers, interfaces      │││
│  ↓                                              ││
├─ domain ──────────────────────────────────────┐│
│  entities, value_objects, exceptions,         ││
│  repository protocols                          ││
└────────────────────────────────────────────────┘
```

- **`core/domain/`** — pure business. Stdlib only.
- **`core/application/`** — use-case orchestration (CQRS). May import `core.domain` and `pydantic`.
- **`infrastructure/`** — implements domain/application Protocols. May import `core.*`.
- **`presentation/`** — delivery mechanisms. May import `core.*` and `infrastructure.*`, but declares handler deps via Protocols.

---

## 4. Layer import rules

These rules are **literal**, not aspirational. Every PR must respect them.

1. **`core/domain/` → stdlib only.** No pydantic, no infra, no presentation.
2. **`core/application/` → `core.domain` + `pydantic`.** Never infrastructure or presentation.
3. **`infrastructure/` → `core.*`.** Never presentation.
4. **`presentation/` → `core.*` and `infrastructure.*`** — but handler deps are declared as **Protocols** (interfaces), not concrete classes.
5. **Presentation siblings are isolated.** Sub-packages directly under `presentation/` (`http/`, `scripts/`, `playground/`) must NOT import from each other.
6. **Within `http/`, `api/` and `web/` are isolated.** They share only `http/wiring.py`, `http/exception_handlers.py`, and the lifespan in `http/main.py` (the composition root). Only `main.py` may include routers from both.

---

## 5. Directory scaffold

```
project-root/
├── src/
│   ├── core/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   └── <entity>.py
│   │   │   ├── value_objects.py
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   └── <entity>.py            # I<Entity>Repository Protocol
│   │   │   ├── interfaces.py              # IPasswordHasher and other domain-pure Protocols
│   │   │   └── exceptions.py
│   │   └── application/
│   │       ├── commands/
│   │       │   ├── base.py                # class Command(BaseModel)
│   │       │   └── <feature>.py
│   │       ├── queries/
│   │       │   ├── base.py                # class Query(BaseModel), class BaseResultDTO(BaseModel)
│   │       │   └── <feature>.py
│   │       ├── handlers/
│   │       │   ├── base.py                # CommandHandler/QueryHandler generics
│   │       │   ├── commands/<feature>.py
│   │       │   └── queries/<feature>.py
│   │       ├── interfaces.py              # IDBSession, IJWTService, I<ExternalService>, ...
│   │       ├── dto.py
│   │       └── exceptions.py
│   ├── infrastructure/
│   │   ├── config.py                      # single flat Config(BaseSettings)
│   │   ├── database/
│   │   │   ├── db_session.py              # new_session_maker(config)
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                # UUID PK + created_at/updated_at
│   │   │   │   └── <entity>.py
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   └── <entity>.py            # SQL<Entity>Repository
│   │   │   └── alembic/
│   │   │       ├── env.py
│   │   │       └── versions/<id>_<msg>.py
│   │   └── services/                      # external-service facades, JWT, password hasher
│   └── presentation/
│       ├── http/
│       │   ├── main.py                    # create_app(), lifespan — composition root
│       │   ├── wiring.py                  # shared Depends factories + typed aliases
│       │   ├── exception_handlers.py
│       │   ├── api/
│       │   │   ├── router.py
│       │   │   ├── dependencies.py        # API auth (Bearer → 401)
│       │   │   └── <feature>/
│       │   │       ├── endpoints.py
│       │   │       ├── providers.py
│       │   │       └── schemas.py
│       │   └── web/
│       │       ├── router.py
│       │       ├── dependencies.py        # cookie auth → 303 redirect
│       │       └── <feature>/
│       │           ├── endpoints.py
│       │           ├── providers.py
│       │           └── schemas.py
│       ├── scripts/                       # standalone CLIs (private files: _foo.py)
│       └── playground/                    # local experiments; never imported elsewhere
├── tests/                                 # mirrors src/ structure 1:1
│   ├── __init__.py
│   ├── conftest.py
│   ├── mocks/                             # in-memory Protocol fakes, mirrors src/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── domain/
│   │   │   │   └── repositories/
│   │   │   │       └── <entity>.py        # Fake<Entity>Repository
│   │   │   └── application/
│   │   │       └── interfaces.py          # FakeDBSession, FakeJWTService, ...
│   │   └── infrastructure/
│   │       └── services/
│   │           └── <service>.py           # Fake<Service> for external facades
│   ├── core/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── test_<entity>.py
│   │   │   ├── value_objects/
│   │   │   │   └── test_<value_object>.py
│   │   │   └── services/
│   │   │       └── test_<service>.py
│   │   └── application/
│   │       └── handlers/
│   │           ├── commands/
│   │           │   └── test_<command>.py
│   │           └── queries/
│   │               └── test_<query>.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   └── repositories/
│   │   │       └── test_<entity>.py       # @pytest.mark.integration tests against real DB
│   │   └── services/
│   │       └── test_<service>.py
│   └── presentation/
│       └── http/
│           └── api/
│               └── <feature>/
│                   └── test_endpoints.py  # TestClient + dependency_overrides
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── Makefile
├── .env.example
├── .env                                   # NEVER commit
├── .gitignore
├── CLAUDE.md
└── GUIDELINES.md
```

---

## 6. Domain layer conventions

**Entities** — frozen dataclasses, `slots=True`, no framework imports:

```python
@dataclass(frozen=True, slots=True)
class User:
    uuid: UserUUID
    email: Email
    fullname: str
    hashed_password: str
    is_verified: bool = False
```

**Value objects** — frozen dataclasses with invariants enforced in `__post_init__`. Raise `DomainException` subclasses on violation:

```python
@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise InvalidEmailFormat(f"Invalid email: {self.value!r}")

    def __str__(self) -> str:
        return self.value
```

Wrap primitive IDs as `<Entity>UUID` value objects with a `default_factory=uuid4` and `__str__` returning the underlying string. This makes handler signatures self-documenting and prevents mixing IDs between entity types.

**Enums** — `StrEnum` for fixed sets, lowercase values:

```python
class OrderStatus(StrEnum):
    pending = "pending"
    shipped = "shipped"
```

**Repository protocols** — `Protocol` with `async` methods, taking/returning **domain entities and value objects** (never raw IDs or ORM models):

```python
class IUserRepository(Protocol):
    async def add_user(self, user: User) -> None: ...
    async def get_user_by_email(self, email: Email) -> User | None: ...
    async def get_user_by_uuid(self, user_uuid: UserUUID) -> User | None: ...
    async def list_all(self) -> list[User]: ...
    async def update(self, user: User) -> None: ...
```

**Exceptions** — flat hierarchy under `DomainException`. Carry minimal context via constructor args:

```python
class DomainException(Exception):
    """Base domain exception."""

class InvalidEmailFormat(DomainException): pass
class EmailIsAlreadyInUse(DomainException): pass

class OrderActionNotAllowed(DomainException):
    def __init__(self, status: str, action: str) -> None:
        super().__init__(f"action '{action}' not allowed for status '{status}'")
        self.status = status
        self.action = action
```

**Forbidden in domain**: pydantic, SQLAlchemy, FastAPI, httpx, any infra/presentation imports. Use `if TYPE_CHECKING:` for circular-import resolution.

---

## 7. Application layer / CQRS

Every use case is either a **Command** (mutates state) or a **Query** (reads state).

**Base shapes**:

```python
# core/application/commands/base.py
from pydantic import BaseModel
class Command(BaseModel): pass

# core/application/queries/base.py
from pydantic import BaseModel, ConfigDict
class Query(BaseModel): pass
class BaseResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

**Handler generics** — typed orchestration:

```python
# core/application/handlers/base.py
from typing import Generic, TypeVar
from core.application.commands.base import Command
from core.application.queries.base import BaseResultDTO, Query

CmdT = TypeVar("CmdT", bound=Command)
CmdResultT = TypeVar("CmdResultT")
QueryT = TypeVar("QueryT", bound=Query)
QueryResultT = TypeVar("QueryResultT", bound=BaseResultDTO)

class CommandHandler(Generic[CmdT, CmdResultT]):
    async def handle(self, command: CmdT) -> CmdResultT:
        raise NotImplementedError

class QueryHandler(Generic[QueryT, QueryResultT]):
    async def handle(self, query: QueryT) -> QueryResultT:
        raise NotImplementedError
```

**Handler rules**:

- **Constructor injection only.** `__init__` takes Protocols, never concrete classes.
- **One commit per use-case.** End the handler with one `await self._db_session.commit()`. Use `await self._db_session.flush()` (not `commit()`) inside the handler if you need an FK to be assigned before later inserts.
- **No business logic in handlers.** Load entities, call their methods, persist. Invariants live in domain entities/value objects.
- **Outer handlers inject inner handlers**, not the inner handler's private collaborators. Each use case owns its own command/handler pair — don't reuse one command across flows.
- **Application exceptions** (`ApplicationException` base) for processing failures (`AuthenticationFailed`, `<Service>Error`, `RenderError`). Domain exceptions for business-rule violations.

**Application interfaces** — `core/application/interfaces.py` holds Protocols for infrastructure dependencies plus their frozen DTO return types:

```python
class IDBSession(Protocol):
    async def commit(self) -> None: ...
    async def flush(self) -> None: ...
    async def rollback(self) -> None: ...

class IJWTService(Protocol):
    def encode_token(self, data: UserJWTTokenDTO) -> JWTTokenDTO: ...
    def decode_token(self, token: JWTToken) -> UserJWTTokenDTO: ...

@dataclass(frozen=True, slots=True)
class ExternalServiceResult:
    ok: bool
    status_code: int
    raw_body: str

class IExternalService(Protocol):
    async def do_thing(self, arg: str) -> ExternalServiceResult: ...
```

---

## 8. Infrastructure layer

**Config** — single flat `Config(BaseSettings)`. `.env` loaded once. Map every env var with `Field(alias=...)`:

```python
class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    frontend_origins: list[str] = Field(default_factory=list, alias="FRONTEND_ORIGINS")

    @field_validator("frontend_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value
```

Cache via `@lru_cache` in wiring (`get_config()`). Inject `Config` as a dependency — never read it as a module-level global.

**Database** — `Base(DeclarativeBase)` provides UUID PK + `created_at`/`updated_at`:

```python
class Base(DeclarativeBase):
    uuid: Mapped[UUID] = mapped_column(sa.Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
```

**Session maker** — one factory, pool tuned:

```python
def new_session_maker(config: Config) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(
        config.database_url,
        pool_size=15,
        max_overflow=15,
        connect_args={"timeout": 5},
    )
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
```

**Migrations** — handwritten Alembic only. Never `--autogenerate`. Versions live in `src/infrastructure/database/alembic/versions/`. Use explicit `revision`/`down_revision` IDs.

**SQL repositories** — implement the domain Protocols. Translate ORM rows ↔ entities via a private `_to_entity()` method. Handlers never see ORM models:

```python
class SQLUserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def add_user(self, user: User) -> None:
        self._db_session.add(UserModel(
            uuid=str(user.uuid),
            email=str(user.email),
            fullname=user.fullname,
            hashed_password=user.hashed_password,
            is_verified=user.is_verified,
        ))

    async def get_user_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == str(email))
        row = (await self._db_session.execute(stmt)).scalar_one_or_none()
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            uuid=UserUUID(UUID(str(model.uuid))),
            email=Email(model.email),
            fullname=model.fullname,
            hashed_password=model.hashed_password,
            is_verified=model.is_verified,
        )
```

**External services** — **one facade + one API client** per external service.

- The **API client** wraps the SDK or raw HTTP and exposes minimal typed methods.
- The **facade** implements the application Protocol (`IExternalService`) and adds logging, retry, and error translation.
- **Translate library errors here**, not in handlers. Catch `httpx.HTTPError`, `anthropic.APIError`, `jwt.PyJWTError`, `asyncpg.PostgresError`, etc., and re-raise as `ApplicationException` / `DomainException` subclasses with context.

```python
class ExternalServiceFacade(IExternalService):
    def __init__(self, client: ExternalAPIClient) -> None:
        self._client = client

    async def do_thing(self, arg: str) -> ExternalServiceResult:
        try:
            raw = await self._client.call(arg)
        except SDKError as e:
            raise ExternalServiceError(f"external call failed: {e}") from e
        return ExternalServiceResult(ok=True, status_code=raw.status, raw_body=raw.body)
```

**Background tasks open a fresh DB session.** The request-scoped session is gone by the time the task runs. Pattern:

```python
class BackgroundProcessor(IProcessor):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession], ...) -> None:
        self._session_maker = session_maker
        ...

    async def run(self, entity_uuid: EntityUUID) -> None:
        async with self._session_maker() as session:
            handler = self._build_handler(session)
            await handler.handle(SomeCommand(entity_uuid=str(entity_uuid)))
```

The AI facade and shared `httpx.AsyncClient` stay app-scoped singletons on `app.state`.

---

## 9. Presentation layer

### 9.1 Composition root

`presentation/http/main.py::create_app()` owns:

- `Config()` instantiation.
- Logging setup.
- `lifespan` async context manager (opens shared `httpx.AsyncClient` on `app.state.http_client`; runs external init like webhook registration).
- CORS middleware (`allow_origins=config.frontend_origins`).
- Static file mounts (if any).
- `exception_handlers.register(app)`.
- Router includes (api, web/admin, web/home).

This is the **only** file in `http/` allowed to import from both `api/` and `web/`.

### 9.2 Shared wiring

`presentation/http/wiring.py` is the only module shared by `api/` and `web/`. It exposes:

- `@lru_cache def get_config() -> Config`.
- `get_session_maker(config)` → cached per-process.
- `async def get_db_session(session_maker)` — yields a session; rolls back on exception, closes in `finally`.
- `get_jwt_service(config)`.
- `get_http_client(request)` — reads `request.app.state.http_client`.
- **Typed aliases**:
  ```python
  SessionDep = Annotated[IDBSession, Depends(get_db_session)]
  JWTServiceDep = Annotated[IJWTService, Depends(get_jwt_service)]
  HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]
  ```

Feature providers depend on these aliases; endpoints depend on feature providers.

### 9.3 Feature folder pattern

Every feature under `api/` and `web/` has the same triplet:

- **`schemas.py`** — Pydantic HTTP models. Inputs use `ConfigDict(extra="forbid")` to reject unknown fields. Schemas are **NOT** reused as commands.
- **`providers.py`** — FastAPI `Depends` factories that assemble fully-wired handler instances.
- **`endpoints.py`** — Route handlers. Parse schema → build command → `await handler.handle(command)` → return schema-mapped response.

```python
# endpoints.py
@router.post("/signup")
async def signup(
    data: schemas.UserSignupRequest,
    handler: Annotated[CreateUserCommandHandler, Depends(providers.create_user_handler)],
) -> schemas.UserSignupResponse:
    command = CreateUserCommand(
        email=data.email,
        fullname=data.fullname,
        password_1=data.password_1,
        password_2=data.password_2,
    )
    new_uuid = await handler.handle(command)
    return schemas.UserSignupResponse(uuid=str(new_uuid))
```

```python
# providers.py
def create_user_handler(
    session: SessionDep,
    repository: Annotated[IUserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[IPasswordHasher, Depends(get_password_hasher)],
) -> CreateUserCommandHandler:
    return CreateUserCommandHandler(
        db_session=session,
        repository=repository,
        password_hasher=password_hasher,
    )
```

### 9.4 Auth — JWT shared, transport split

- **API (`api/dependencies.py`)** — Bearer header. Decode JWT. Raise `AuthenticationFailed` → 401.
- **Web (`web/admin/dependencies.py`)** — Cookie. Same JWT decode. On failure, return 303 redirect to `/admin/login`.

Both use the same `IJWTService` and `IUserRepository`. Cookie-setting helper lives in shared `wiring.py` so a single function controls `httponly`/`secure`/`samesite`/`domain`.

### 9.5 Presentation siblings

The three presentation siblings are **mutually isolated**:

- **`http/`** — FastAPI app.
- **`scripts/`** — Standalone CLIs. Module-private files prefixed with `_` (`_sample_data.py`, `_xml_reader.py`). Run as `python -m presentation.scripts.<name>`.
- **`playground/`** — Local experiments. Bypasses DB, calls real external services. Used for development-time verification, never in production paths.

A sibling **never imports from another sibling**. If two areas need the same factory, duplicate it locally.

### 9.6 Router composition

Routers nest hierarchically:

```python
# api/router.py
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(healthcheck_router)

# auth/endpoints.py
router = APIRouter(prefix="/auth", tags=["auth"])
```

`tags=[...]` controls OpenAPI grouping.

---

## 10. Exception handling

Three hierarchies:

- **`DomainException`** — business-rule violations (`InvalidEmailFormat`, `EmailIsAlreadyInUse`, `OrderActionNotAllowed`).
- **`ApplicationException`** — processing failures (`AuthenticationFailed`, `ExternalServiceError`).
- **Built-in errors** — let FastAPI default to 500.

**Central translation** — one map, MRO-walked:

```python
# presentation/http/exception_handlers.py
_EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    InvalidEmailFormat: status.HTTP_400_BAD_REQUEST,
    EmailIsAlreadyInUse: status.HTTP_400_BAD_REQUEST,
    UserNotFound: status.HTTP_404_NOT_FOUND,
    OrderActionNotAllowed: status.HTTP_409_CONFLICT,
    AuthenticationFailed: status.HTTP_401_UNAUTHORIZED,
    ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
}

def _lookup_status(exc_type: type[Exception]) -> int:
    for klass in exc_type.mro():
        if klass in _EXCEPTION_STATUS_MAP:
            return _EXCEPTION_STATUS_MAP[klass]
    return status.HTTP_500_INTERNAL_SERVER_ERROR

async def _domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    return JSONResponse(
        status_code=_lookup_status(type(exc)),
        content={"detail": str(exc) or exc.__class__.__name__},
    )

# similarly for ApplicationException

def register(app: FastAPI) -> None:
    app.add_exception_handler(DomainException, _domain_exception_handler)
    app.add_exception_handler(ApplicationException, _application_exception_handler)
```

**No per-endpoint try/except ladders.** Add a new exception class + a row in the map.

---

## 11. Feature workflow — TDD, inside-out

The order of work for **every** feature, new or modified, is the same: **domain → application → infrastructure → presentation**. Always start from the heart (business logic) and move outward. At every layer, write tests first, watch them fail, then implement.

### 11.1 The cycle, per layer

For each layer, in this order:

1. **Sketch the shape** — define the types this layer needs: entities and value objects (domain), commands and Protocols (application), ORM models and SQL repos (infrastructure), schemas and endpoints (presentation). No implementation bodies yet — just signatures.
2. **Write the tests** — describe behavior, not I/O wiring. Run them; they fail (red) because nothing is implemented.
3. **Implement the minimum** needed to make those tests pass.
4. **Run the tests — green.** Refactor if needed.
5. **Move outward** to the next layer. Repeat.

You don't write a single line of presentation code until the domain and application layers are green.

### 11.2 What to test at each layer

The point of TDD is to encode **business behavior**, not to assert that mocks were called. Each layer has its own kind of behavior:

| Layer | What the tests describe | What they don't describe |
|---|---|---|
| **Domain** | Rules and invariants: "an `Email` value object rejects malformed input", "a `Score` rejects values outside 0–100", "`Order.cancel()` raises when status is `shipped`". | No I/O, no fakes, no Protocols. Just instantiate the value object/entity and assert. |
| **Application** | Use-case orchestration: "creating a duplicate user raises `EmailIsAlreadyInUse`", "successful signup commits exactly once", "the handler calls the inner handler with the right command". Use fakes for repositories and external services. | Not SQL. Not HTTP. Not the shape of stored rows. |
| **Infrastructure** | I/O contracts: "`SQLUserRepository` round-trips an entity correctly", "the facade re-raises SDK rate-limit errors as `ApplicationException`". `@pytest.mark.integration` when real DB/network is involved. | Not the business rule (already covered in domain) — only that the boundary works. |
| **Presentation** | HTTP contracts: "POST `/users` with bad email returns 400", "endpoint converts schema to command and returns 200", "auth dependency raises 401 on missing bearer". Use `TestClient` with `dependency_overrides`. | Not the business rule. Not the storage path. |

If a test is asserting "the repository's `add_user` was called once" and nothing else, it's testing wiring, not behavior — and that wiring should be obvious from reading the handler. Delete the test. The behavior worth testing is "after handling, a user with this email exists in the repository" — which is exactly what a fake (real in-memory class, not a mock) lets you assert against.

### 11.3 Layer containment — don't think outside the layer you're in

When working on the domain, **think only about the domain**. Don't ask "how will this be stored?" or "what will the JSON response look like?" — those are not domain concerns. If you find yourself reaching for a SQLAlchemy import or a FastAPI status code while writing a value object, stop. You've leaked.

The same rule applies at every layer:

- In **domain**: forget about persistence, HTTP, configuration, external services. The world is dataclasses, value objects, and exceptions.
- In **application**: the repository is a `Protocol`. You don't know if it's Postgres, SQLite, or an in-memory dict. The external service is `IExternalService`. You don't know if it's HTTP, gRPC, or a stub.
- In **infrastructure**: forget about HTTP status codes — that's presentation's job (via the central exception map). Translate library errors to `ApplicationException`/`DomainException` and stop.
- In **presentation**: forget about transactions, business rules, and storage. Build the command, hand it to the handler, return the response.

This is the layer-import rule (§4), but for your **thinking**. Code leaks happen because thought leaks first. Catch it at the thinking layer.

### 11.4 A worked example — adding "users can change their email"

A concrete walkthrough of the inside-out cycle:

1. **Domain (red → green)**
   - Add `User.change_email(new_email: Email) -> None` and decide invariants: "cannot be the same as current", "marks user as unverified again".
   - Write `tests/core/domain/entities/test_user.py` with cases: changes email, raises on same email, resets `is_verified`. Tests fail — method doesn't exist.
   - Implement `User.change_email`. Tests pass.
   - **You haven't touched DB, HTTP, or Pydantic.**

2. **Application (red → green)**
   - Add `ChangeEmailCommand` and `ChangeEmailCommandHandler`. Decide flow: load user, call `change_email`, persist, commit.
   - Write `tests/core/application/handlers/commands/test_user.py` with cases: changes email and commits once, raises `UserNotFound` for missing user, propagates domain exceptions. Use `FakeUserRepository` and `FakeDBSession`.
   - Implement the handler. Tests pass.
   - **You still haven't touched SQL or HTTP.**

3. **Infrastructure (red → green)**
   - The existing `SQLUserRepository.update()` already handles entity persistence — no new code needed. If a new query were required, write an `@pytest.mark.integration` test for the round-trip first.

4. **Presentation (red → green)**
   - Add `PATCH /api/v1/users/me/email` endpoint, schema, provider.
   - Write `tests/presentation/http/api/users/test_endpoints.py` with cases: 200 on success, 400 on bad email, 401 without auth.
   - Implement endpoint + schema + provider. Tests pass.
   - Add the new exception (if any) to `_EXCEPTION_STATUS_MAP`.

At no point during steps 1–2 did you have to think about JSON, HTTP, or SQL. That's the point.

### 11.5 When a change is single-layer

Not every change crosses all four layers. A typo in a response schema is presentation-only. A new private domain rule (e.g. tightening a value object's regex) is domain-only. The inside-out rule still applies: the layer with the change is the layer you test first; outer layers come along only when they're affected.

What's forbidden is the **reverse** direction — modifying an endpoint to encode a new business rule because "it's faster than going through the handler and domain." If the rule lives in the endpoint, it can't be tested without a `TestClient`, can't be reused from a script or a background job, and will quietly diverge from any other path that touches the same entity.

---

## 12. Testing

### 12.1 Test layout — mirror the project structure 1:1

`tests/` mirrors `src/` exactly. Every test file lives next to where its target would live in `src/`, prefixed with `test_`:

| Target in `src/` | Test in `tests/` |
|---|---|
| `src/core/domain/entities/user.py` | `tests/core/domain/entities/test_user.py` |
| `src/core/domain/value_objects.py` (one VO per file) | `tests/core/domain/value_objects/test_email.py` |
| `src/core/application/handlers/commands/user.py` | `tests/core/application/handlers/commands/test_user.py` |
| `src/infrastructure/database/repositories/user.py` | `tests/infrastructure/database/repositories/test_user.py` |
| `src/presentation/http/api/users/endpoints.py` | `tests/presentation/http/api/users/test_endpoints.py` |

Every intermediate test directory needs an `__init__.py`. Don't flatten tests into a single `tests/` directory — the parallel structure is what lets you find a test from its source file (and vice versa) without grep.

### 12.2 Fakes live in `tests/mocks/`, mirroring the project

In-memory fakes go under `tests/mocks/`, and **the path inside `tests/mocks/` matches the path of the Protocol they implement**:

| Protocol in `src/` | Fake in `tests/mocks/` |
|---|---|
| `core/domain/repositories/user.py::IUserRepository` | `tests/mocks/core/domain/repositories/user.py::FakeUserRepository` |
| `core/application/interfaces.py::IDBSession` | `tests/mocks/core/application/interfaces.py::FakeDBSession` |
| `infrastructure/services/email.py::EmailFacade` (impl of `IEmailService`) | `tests/mocks/core/application/interfaces.py::FakeEmailService` |

Rule of thumb: the fake's file path is determined by **where the Protocol is defined**, not by where the concrete implementation lives. Fakes implement Protocols, not concrete classes.

Don't dump everything into one giant `tests/fakes.py`. One file per Protocol (or per closely-related Protocol cluster, e.g. all the small JWT/DB fakes can share `tests/mocks/core/application/interfaces.py`).

### 12.3 In-memory fakes, not mocks

Each fake is a real class implementing the Protocol with a dict-based store. Instrument with observable hooks (`.calls`, `.commits`, `.added`) so tests assert against them directly. No `unittest.mock`.

```python
class FakeDBSession:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    async def commit(self) -> None: self.commits += 1
    async def flush(self) -> None: ...
    async def rollback(self) -> None: self.rollbacks += 1


class FakeUserRepository(IUserRepository):
    def __init__(self, seed: list[User] | None = None) -> None:
        self._by_uuid: dict[str, User] = {str(u.uuid): u for u in (seed or [])}
        self._by_email: dict[str, User] = {str(u.email): u for u in (seed or [])}

    async def add_user(self, user: User) -> None:
        self._by_uuid[str(user.uuid)] = user
        self._by_email[str(user.email)] = user

    async def get_user_by_email(self, email: Email) -> User | None:
        return self._by_email.get(str(email))

    async def get_user_by_uuid(self, user_uuid: UserUUID) -> User | None:
        return self._by_uuid.get(str(user_uuid))

    async def list_all(self) -> list[User]:
        return list(self._by_uuid.values())

    async def update(self, user: User) -> None:
        self._by_uuid[str(user.uuid)] = user
        self._by_email[str(user.email)] = user
```

### 12.4 Handler tests — builder, configure, assert

Assemble the handler with explicitly listed fakes, run it, assert side effects (persisted state, commit count, recorded calls):

```python
# tests/core/application/handlers/commands/test_user.py
from tests.mocks.core.application.interfaces import FakeDBSession
from tests.mocks.core.domain.repositories.user import FakeUserRepository

async def test_signup_creates_user_and_commits_once():
    repo = FakeUserRepository()
    session = FakeDBSession()
    handler = CreateUserCommandHandler(
        db_session=session,
        repository=repo,
        password_hasher=_Hasher(),
    )

    new_uuid = await handler.handle(CreateUserCommand(
        email="alice@example.com",
        fullname="Alice",
        password="hunter2",
    ))

    user = await repo.get_user_by_uuid(new_uuid)
    assert user is not None
    assert user.email == Email("alice@example.com")
    assert session.commits == 1
```

### 12.5 API tests

Use a real FastAPI `TestClient` (don't mock the framework). Override boundary dependencies — the repository, the JWT service, the external facade — never the handler itself. Tests live under `tests/presentation/http/api/<feature>/test_endpoints.py`:

```python
from fastapi.testclient import TestClient

from presentation.http.api.users import providers
from presentation.http.main import app
from tests.mocks.core.domain.repositories.user import FakeUserRepository

def test_create_user_endpoint():
    fake = FakeUserRepository()
    app.dependency_overrides[providers.get_user_repository] = lambda: fake
    try:
        client = TestClient(app)
        r = client.post("/api/v1/users", json={...})
        assert r.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

### 12.6 Pytest config

`pyproject.toml`:

```toml
[tool.pytest.ini_options]
python_files = "test*.py"
pythonpath = "src"
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
addopts = "-m 'not integration'"
markers = [
    "integration: real-service tests (hit external APIs or the real DB); opt in with `-m integration`",
]
```

### 12.7 Integration tests

Tests that hit a real database, real external API, or any real I/O are marked `@pytest.mark.integration` and excluded by default. They live in the same mirrored structure (e.g. `tests/infrastructure/database/repositories/test_user.py`). Opt in with `uv run pytest -m integration`.

---

## 13. Naming conventions

| Element | Convention | Example |
|---|---|---|
| Entity | noun, singular | `User`, `Order`, `Invoice` |
| Value object | semantic name | `Email`, `Money`, `Score` |
| Entity UUID VO | `<Entity>UUID` | `UserUUID`, `OrderUUID` |
| Protocol (interface) | `I<Service>` | `IUserRepository`, `IJWTService` |
| SQL repository | `SQL<Entity>Repository` | `SQLUserRepository` |
| Command | `<Verb><Noun>Command` | `CreateUserCommand`, `ShipOrderCommand` |
| Query | `<Get\|List>...Query` | `GetMeQuery`, `ListOrdersPagedQuery` |
| Command handler | `<Command>Handler` | `CreateUserCommandHandler` |
| Facade | `<Domain>Facade` | `EmailFacade`, `AIFacade` |
| API client | `<Domain>HTTPClient` or `<Domain>APIClient` | `StripeHTTPClient` |
| Exception | descriptive noun phrase | `EmailIsAlreadyInUse`, `OrderNotFound` |
| Enum | `StrEnum`, lowercase values | `OrderStatus.shipped = "shipped"` |
| Module-private file | `_<name>.py` | `_sample_data.py`, `_xml_reader.py` |

---

## 14. Type discipline

- **100% type annotations.** Every parameter, return, and class attribute. No untyped `def`. No implicit `Any`.
- **`X | None`**, not `Optional[X]`. **`list[T]`/`dict[K, V]`**, not `List[T]`/`Dict[K, V]`.
- **Generics on handlers**: `CommandHandler[CreateUserCommand, UserUUID]`.
- **`Protocol` for interfaces** — structural typing. Don't use ABCs unless you need real inheritance.
- **`if TYPE_CHECKING:`** for forward refs. **Imports at the top of the file** — never bottom-of-file or in-function.
- **No `# type: ignore`** to escape typing problems. Tighten the type or wrap in a DTO.
- **No `object`/`Any`** as escape hatches. If a function returns "anything," it returns a typed DTO.

---

## 15. Non-negotiable rules

Pasted at the top of `CLAUDE.md` so AI assistants see them on every turn:

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
15. **TDD, inside-out.** For every feature: domain → application → infrastructure → presentation. At each layer, write tests first, watch them fail, then implement. Test **business behavior**, not mock-call wiring. Don't think about outer-layer concerns while working on an inner layer — code leaks because thought leaks first.
16. **Don't reinvent the wheel.** Before hand-rolling a non-trivial utility, check PyPI and the project's existing dependencies for a maintained library that already solves the problem. Prefer `uv add <pkg>` over a from-scratch implementation. The stdlib is the right default for trivial helpers, not a hard ceiling — reach for `httpx`, `tenacity`, `structlog`, `python-slugify`, `pendulum`, `email-validator`, etc., when they fit. Note the library choice (or the conscious decision to avoid one) in the PR description.

---

## 16. Copy-paste starter scaffold

A minimal working slice: a `User` entity with `Email` value object, `POST /api/v1/users` that creates a user, and a handler test. Every layer is exercised. Copy these files verbatim into the new project to bootstrap it.

### `pyproject.toml`

```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.13.0"
dependencies = [
    "alembic>=1.14.0",
    "asyncpg>=0.30.0",
    "bcrypt>=4.2.0",
    "fastapi>=0.115.0",
    "httpx>=0.28.0",
    "pydantic[email]>=2.9.0",
    "pydantic-settings>=2.6.0",
    "pyjwt>=2.10.0",
    "sqlalchemy[asyncio]>=2.0.36",
    "uvicorn>=0.32.0",
    "gunicorn>=23.0.0",
]

[dependency-groups]
dev = [
    "aiosqlite>=0.20.0",
    "pre-commit>=4.0.1",
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.7.3",
]

[tool.pytest.ini_options]
python_files = "test*.py"
pythonpath = "src"
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
addopts = "-m 'not integration'"
markers = [
    "integration: real-service tests; opt in with `-m integration`",
]

[tool.ruff]
exclude = [".venv/"]
```

### `.env.example`

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/myapp
JWT_SECRET_KEY=replace-me
JWT_ACCESS_TOKEN_LIFETIME=600
JWT_REFRESH_TOKEN_LIFETIME=86400
LOG_LEVEL=INFO
FRONTEND_ORIGINS=http://localhost:3000
```

### `.gitignore`

```
.env
.venv/
__pycache__/
*.pyc
dist/
build/
*.egg-info/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
node_modules/
```

### `Makefile`

```makefile
dev:
	rm -rf .venv && uv venv --python 3.13 && uv sync

prod:
	rm -rf .venv && uv venv --python 3.13 && uv sync --no-dev

ruff:
	uv run ruff check --fix .
	uv run ruff format .
```

### `alembic.ini` (minimal)

```ini
[alembic]
script_location = src/infrastructure/database/alembic
prepend_sys_path = src
sqlalchemy.url =

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

### Domain layer

```python
# src/core/domain/exceptions.py
class DomainException(Exception):
    """Base domain exception."""

class InvalidEmailFormat(DomainException): pass
class EmailIsAlreadyInUse(DomainException): pass
class UserNotFound(DomainException): pass
```

```python
# src/core/domain/value_objects.py
import re
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from core.domain.exceptions import InvalidEmailFormat


@dataclass(frozen=True, slots=True)
class UserUUID:
    value: UUID = field(default_factory=uuid4)

    def __str__(self) -> str:
        return str(self.value)


_EMAIL_RE: re.Pattern[str] = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise InvalidEmailFormat(f"Invalid email: {self.value!r}")

    def __str__(self) -> str:
        return self.value
```

```python
# src/core/domain/entities/__init__.py
from core.domain.entities.user import User

__all__ = ["User"]
```

```python
# src/core/domain/entities/user.py
from dataclasses import dataclass

from core.domain.value_objects import Email, UserUUID


@dataclass(slots=True)
class User:
    uuid: UserUUID
    email: Email
    fullname: str
    hashed_password: str
    is_verified: bool = False
```

```python
# src/core/domain/repositories/__init__.py
from core.domain.repositories.user import IUserRepository

__all__ = ["IUserRepository"]
```

```python
# src/core/domain/repositories/user.py
from typing import Protocol

from core.domain.entities import User
from core.domain.value_objects import Email, UserUUID


class IUserRepository(Protocol):
    async def add_user(self, user: User) -> None: ...
    async def get_user_by_email(self, email: Email) -> User | None: ...
    async def get_user_by_uuid(self, user_uuid: UserUUID) -> User | None: ...
```

```python
# src/core/domain/interfaces.py
from typing import Protocol


class IPasswordHasher(Protocol):
    def hash_password(self, password: str) -> str: ...
    def verify_password(self, password: str, hashed: str) -> bool: ...
```

### Application layer

```python
# src/core/application/commands/base.py
from pydantic import BaseModel
class Command(BaseModel): pass
```

```python
# src/core/application/queries/base.py
from pydantic import BaseModel, ConfigDict
class Query(BaseModel): pass
class BaseResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

```python
# src/core/application/handlers/base.py
from typing import Generic, TypeVar

from core.application.commands.base import Command
from core.application.queries.base import BaseResultDTO, Query

CmdT = TypeVar("CmdT", bound=Command)
CmdResultT = TypeVar("CmdResultT")
QueryT = TypeVar("QueryT", bound=Query)
QueryResultT = TypeVar("QueryResultT", bound=BaseResultDTO)


class CommandHandler(Generic[CmdT, CmdResultT]):
    async def handle(self, command: CmdT) -> CmdResultT:
        raise NotImplementedError


class QueryHandler(Generic[QueryT, QueryResultT]):
    async def handle(self, query: QueryT) -> QueryResultT:
        raise NotImplementedError
```

```python
# src/core/application/interfaces.py
from typing import Protocol


class IDBSession(Protocol):
    async def commit(self) -> None: ...
    async def flush(self) -> None: ...
    async def rollback(self) -> None: ...
```

```python
# src/core/application/exceptions.py
class ApplicationException(Exception):
    """Base application exception."""

class AuthenticationFailed(ApplicationException): pass
```

```python
# src/core/application/commands/user.py
from pydantic import EmailStr

from core.application.commands.base import Command


class CreateUserCommand(Command):
    email: EmailStr
    fullname: str
    password: str
```

```python
# src/core/application/handlers/commands/user.py
from core.application.commands.user import CreateUserCommand
from core.application.handlers.base import CommandHandler
from core.application.interfaces import IDBSession
from core.domain.entities import User
from core.domain.exceptions import EmailIsAlreadyInUse
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from core.domain.value_objects import Email, UserUUID


class CreateUserCommandHandler(CommandHandler[CreateUserCommand, UserUUID]):
    def __init__(
        self,
        db_session: IDBSession,
        repository: IUserRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        self._db_session = db_session
        self._repository = repository
        self._password_hasher = password_hasher

    async def handle(self, command: CreateUserCommand) -> UserUUID:
        email = Email(str(command.email))
        existing = await self._repository.get_user_by_email(email)
        if existing is not None:
            raise EmailIsAlreadyInUse()

        user = User(
            uuid=UserUUID(),
            fullname=command.fullname,
            email=email,
            hashed_password=self._password_hasher.hash_password(command.password),
        )

        await self._repository.add_user(user)
        await self._db_session.commit()
        return user.uuid
```

### Infrastructure layer

```python
# src/infrastructure/config.py
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    frontend_origins: list[str] = Field(default_factory=list, alias="FRONTEND_ORIGINS")

    @field_validator("frontend_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value
```

```python
# src/infrastructure/database/db_session.py
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from infrastructure.config import Config


def new_session_maker(config: Config) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(
        config.database_url,
        pool_size=15,
        max_overflow=15,
        connect_args={"timeout": 5},
    )
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
```

```python
# src/infrastructure/database/models/__init__.py
from infrastructure.database.models.base import Base
from infrastructure.database.models.user import User

__all__ = ["Base", "User"]
```

```python
# src/infrastructure/database/models/base.py
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    uuid: Mapped[UUID] = mapped_column(sa.Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
```

```python
# src/infrastructure/database/models/user.py
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.base import Base


class User(Base):
    __tablename__ = "users"

    fullname: Mapped[str] = mapped_column(sa.String(255))
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(255))
    is_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False)
```

```python
# src/infrastructure/database/repositories/__init__.py
from infrastructure.database.repositories.user import SQLUserRepository

__all__ = ["SQLUserRepository"]
```

```python
# src/infrastructure/database/repositories/user.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.entities import User as UserEntity
from core.domain.repositories import IUserRepository
from core.domain.value_objects import Email, UserUUID
from infrastructure.database.models import User as UserModel


class SQLUserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def add_user(self, user: UserEntity) -> None:
        self._db_session.add(UserModel(
            uuid=user.uuid.value,
            fullname=user.fullname,
            email=str(user.email),
            hashed_password=user.hashed_password,
            is_verified=user.is_verified,
        ))

    async def get_user_by_email(self, email: Email) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.email == str(email))
        row = (await self._db_session.execute(stmt)).scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def get_user_by_uuid(self, user_uuid: UserUUID) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.uuid == user_uuid.value)
        row = (await self._db_session.execute(stmt)).scalar_one_or_none()
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            uuid=UserUUID(UUID(str(model.uuid))),
            fullname=model.fullname,
            email=Email(model.email),
            hashed_password=model.hashed_password,
            is_verified=model.is_verified,
        )
```

```python
# src/infrastructure/services/password_hasher.py
import bcrypt

from core.domain.interfaces import IPasswordHasher


class PasswordHasher(IPasswordHasher):
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
```

### Presentation layer

```python
# src/presentation/http/main.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config import Config
from presentation.http import exception_handlers
from presentation.http.api.router import api_router


def create_app() -> FastAPI:
    config = Config()
    app = FastAPI(title="myapp", description="Clean-architecture FastAPI starter.")
    exception_handlers.register(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.frontend_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(api_router)
    return app


app = create_app()
```

```python
# src/presentation/http/wiring.py
from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.application.interfaces import IDBSession
from infrastructure.config import Config
from infrastructure.database.db_session import new_session_maker


@lru_cache
def get_config() -> Config:
    return Config()


def get_session_maker(
    config: Annotated[Config, Depends(get_config)],
) -> async_sessionmaker[AsyncSession]:
    return new_session_maker(config)


async def get_db_session(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_maker)
    ],
) -> AsyncIterator[IDBSession]:
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


SessionDep = Annotated[IDBSession, Depends(get_db_session)]
```

```python
# src/presentation/http/exception_handlers.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.application.exceptions import (
    ApplicationException,
    AuthenticationFailed,
)
from core.domain.exceptions import (
    DomainException,
    EmailIsAlreadyInUse,
    InvalidEmailFormat,
    UserNotFound,
)


_EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    InvalidEmailFormat: status.HTTP_400_BAD_REQUEST,
    EmailIsAlreadyInUse: status.HTTP_400_BAD_REQUEST,
    UserNotFound: status.HTTP_404_NOT_FOUND,
    AuthenticationFailed: status.HTTP_401_UNAUTHORIZED,
}


def _lookup_status(exc_type: type[Exception]) -> int:
    for klass in exc_type.mro():
        if klass in _EXCEPTION_STATUS_MAP:
            return _EXCEPTION_STATUS_MAP[klass]
    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def _domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    return JSONResponse(
        status_code=_lookup_status(type(exc)),
        content={"detail": str(exc) or exc.__class__.__name__},
    )


async def _application_exception_handler(
    request: Request, exc: ApplicationException
) -> JSONResponse:
    return JSONResponse(
        status_code=_lookup_status(type(exc)),
        content={"detail": str(exc) or exc.__class__.__name__},
    )


def register(app: FastAPI) -> None:
    app.add_exception_handler(DomainException, _domain_exception_handler)
    app.add_exception_handler(ApplicationException, _application_exception_handler)
```

```python
# src/presentation/http/api/router.py
from fastapi import APIRouter

from presentation.http.api.users.endpoints import router as users_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users_router)
```

```python
# src/presentation/http/api/users/schemas.py
from pydantic import BaseModel, ConfigDict, EmailStr


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    fullname: str
    password: str


class CreateUserResponse(BaseModel):
    uuid: str
```

```python
# src/presentation/http/api/users/providers.py
from typing import Annotated

from fastapi import Depends

from core.application.handlers.commands.user import CreateUserCommandHandler
from core.domain.interfaces import IPasswordHasher
from core.domain.repositories import IUserRepository
from infrastructure.database.repositories import SQLUserRepository
from infrastructure.services.password_hasher import PasswordHasher
from presentation.http.wiring import SessionDep


def get_user_repository(session: SessionDep) -> IUserRepository:
    return SQLUserRepository(session)


def get_password_hasher() -> IPasswordHasher:
    return PasswordHasher()


def create_user_handler(
    session: SessionDep,
    repository: Annotated[IUserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[IPasswordHasher, Depends(get_password_hasher)],
) -> CreateUserCommandHandler:
    return CreateUserCommandHandler(
        db_session=session,
        repository=repository,
        password_hasher=password_hasher,
    )
```

```python
# src/presentation/http/api/users/endpoints.py
from typing import Annotated

from fastapi import APIRouter, Depends

from core.application.commands.user import CreateUserCommand
from core.application.handlers.commands.user import CreateUserCommandHandler
from presentation.http.api.users import providers, schemas


router = APIRouter(prefix="/users", tags=["users"])


@router.post("")
async def create_user(
    data: schemas.CreateUserRequest,
    handler: Annotated[CreateUserCommandHandler, Depends(providers.create_user_handler)],
) -> schemas.CreateUserResponse:
    command = CreateUserCommand(
        email=data.email,
        fullname=data.fullname,
        password=data.password,
    )
    new_uuid = await handler.handle(command)
    return schemas.CreateUserResponse(uuid=str(new_uuid))
```

### Tests

The test tree mirrors `src/`. Mocks live under `tests/mocks/` along the same path as the Protocol they implement. Every directory below needs an `__init__.py` so imports work.

```python
# tests/mocks/core/application/interfaces.py
from core.application.interfaces import IDBSession


class FakeDBSession(IDBSession):
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    async def commit(self) -> None:
        self.commits += 1

    async def flush(self) -> None: ...

    async def rollback(self) -> None:
        self.rollbacks += 1
```

```python
# tests/mocks/core/domain/repositories/user.py
from core.domain.entities import User
from core.domain.repositories import IUserRepository
from core.domain.value_objects import Email, UserUUID


class FakeUserRepository(IUserRepository):
    def __init__(self, seed: list[User] | None = None) -> None:
        self._by_uuid: dict[str, User] = {}
        self._by_email: dict[str, User] = {}
        for user in seed or []:
            self._by_uuid[str(user.uuid)] = user
            self._by_email[str(user.email)] = user

    async def add_user(self, user: User) -> None:
        self._by_uuid[str(user.uuid)] = user
        self._by_email[str(user.email)] = user

    async def get_user_by_email(self, email: Email) -> User | None:
        return self._by_email.get(str(email))

    async def get_user_by_uuid(self, user_uuid: UserUUID) -> User | None:
        return self._by_uuid.get(str(user_uuid))
```

```python
# tests/mocks/core/domain/interfaces.py
from core.domain.interfaces import IPasswordHasher


class FakePasswordHasher(IPasswordHasher):
    def hash_password(self, password: str) -> str:
        return f"hashed:{password}"

    def verify_password(self, password: str, hashed: str) -> bool:
        return hashed == f"hashed:{password}"
```

```python
# tests/core/application/handlers/commands/test_user.py
import pytest

from core.application.commands.user import CreateUserCommand
from core.application.handlers.commands.user import CreateUserCommandHandler
from core.domain.entities import User
from core.domain.exceptions import EmailIsAlreadyInUse
from core.domain.value_objects import Email, UserUUID
from tests.mocks.core.application.interfaces import FakeDBSession
from tests.mocks.core.domain.interfaces import FakePasswordHasher
from tests.mocks.core.domain.repositories.user import FakeUserRepository


async def test_create_user_persists_and_commits_once():
    repo = FakeUserRepository()
    session = FakeDBSession()
    handler = CreateUserCommandHandler(
        db_session=session,
        repository=repo,
        password_hasher=FakePasswordHasher(),
    )

    new_uuid = await handler.handle(CreateUserCommand(
        email="alice@example.com",
        fullname="Alice",
        password="hunter2",
    ))

    user = await repo.get_user_by_uuid(new_uuid)
    assert user is not None
    assert user.email == Email("alice@example.com")
    assert user.hashed_password == "hashed:hunter2"
    assert session.commits == 1


async def test_create_user_rejects_duplicate_email():
    existing = User(
        uuid=UserUUID(),
        fullname="Bob",
        email=Email("alice@example.com"),
        hashed_password="hashed:other",
    )
    handler = CreateUserCommandHandler(
        db_session=FakeDBSession(),
        repository=FakeUserRepository([existing]),
        password_hasher=FakePasswordHasher(),
    )

    with pytest.raises(EmailIsAlreadyInUse):
        await handler.handle(CreateUserCommand(
            email="alice@example.com",
            fullname="Alice",
            password="hunter2",
        ))
```

---

## 17. Verification

After scaffolding the new project, verify the slice end-to-end:

```bash
# 1. Provision env + deps
make dev

# 2. Run migrations against a local Postgres (create initial migration first via `uv run alembic revision -m "create users"`)
uv run alembic upgrade head

# 3. Start the server
uv run uvicorn --app-dir src presentation.http.main:app --reload

# 4. Hit the endpoint
curl -X POST http://localhost:8000/api/v1/users \
    -H 'Content-Type: application/json' \
    -d '{"email":"a@b.com","fullname":"A","password":"hunter2"}'
# → {"uuid": "..."}

# 5. Run tests
uv run pytest

# 6. Lint + format
uv run ruff check .
uv run ruff format --check .
```

All six steps should pass before the scaffold is considered done. If any fail, fix the project before committing.
