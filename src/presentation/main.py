from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from presentation import exception_handlers
from presentation.api.router import api_router
from presentation.web.router import web_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="base_fastapi",
        description="Lightweight fullstack FastAPI app (clean architecture + CQRS).",
    )

    exception_handlers.register(app)

    static_dir = Path(__file__).parent / "web" / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.include_router(api_router)
    app.include_router(web_router)

    return app


app = create_app()
