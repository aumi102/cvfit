from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.core.config import resolve_path, settings

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory=resolve_path(settings.FRONTEND_TEMPLATES_DIR))

@router.get("/")
def ui_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
