from fastapi import FastAPI
from backend.db.connection import register_startup_event, register_shutdown_event
from fastapi.responses import UJSONResponse
from importlib import metadata
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router

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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # or ["*"] to allow all (not recommended for prod)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    register_startup_event(app=app)
    register_shutdown_event(app=app)
    return app