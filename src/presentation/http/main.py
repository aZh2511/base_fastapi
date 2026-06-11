import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from infrastructure.config import Config
from presentation.http import exception_handlers
from presentation.http.api.router import api_router
from presentation.http.web.router import web_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield


def create_app() -> FastAPI:
    config = Config()
    logging.basicConfig(level=config.log_level)

    app = FastAPI(
        title="base_fastapi",
        description="Lightweight fullstack FastAPI app (clean architecture + CQRS).",
        lifespan=lifespan,
    )

    exception_handlers.register(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.frontend_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    static_dir = Path(__file__).parent / "web" / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.include_router(api_router)
    app.include_router(web_router)

    return app


app = create_app()
