from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


_TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

web_router = APIRouter()


@web_router.get("/", response_class=HTMLResponse, name="home")
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")
