from fastapi import FastAPI
from backend.db.connection import register_startup_event, register_shutdown_event
from fastapi.responses import UJSONResponse
from importlib import metadata
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import HTMLResponse


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    origins = [
        "http://localhost:5173",  # React dev server
    ]

    app = FastAPI(
        title="backend",
        version=metadata.version("backend"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )
    app.mount("/static", StaticFiles(directory="dist", html=True), name="static")
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # or ["*"] to allow all (not recommended for prod)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key="super-secret-key",  # Replace with a strong key in prod!
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        with open(os.path.join("dist", "index.html")) as f:
            return f.read()
        
    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_spa(full_path: str):
        index_path = os.path.join("dist", "index.html")
        with open(index_path) as f:
            return f.read()

    register_startup_event(app=app)
    register_shutdown_event(app=app)
    return app
