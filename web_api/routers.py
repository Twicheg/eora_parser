from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

tags_metadata = [
    {
        "name": "parser",
        "description":
            "Parse with llm",
    },
]

templates = Jinja2Templates(directory="web_api/templates")
front_router = APIRouter(tags=tags_metadata)


@front_router.get("/", response_class=HTMLResponse, tags=["web"])
async def main(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )
