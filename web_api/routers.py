from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


templates = Jinja2Templates(directory="web_api/templates")
front_router = APIRouter(tags=["Frontend"])

@front_router.get("/", response_class=HTMLResponse,)
async def main(request: Request) -> HTMLResponse:
    """Frontend of that project"""
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )
