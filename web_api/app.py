from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import DEBUG, CORS_ORIGINS
from web_api.routers import front_router
from fastapi.middleware.cors import CORSMiddleware
from web_api.middlewares import UuidCookies
from web_api.websockets_router import dialog_with_llm

app = FastAPI(debug=DEBUG)
app.include_router(front_router)
app.mount("/web_api/static", StaticFiles(directory="web_api/static"), name='static')
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.add_middleware(UuidCookies)
app.add_websocket_route("/ws/{client_id}", dialog_with_llm)
