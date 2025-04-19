from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Awaitable, Callable
from fastapi import FastAPI


DATABASE_URL = os.environ.get("DB_URL")


# DATABASE_URL = "sqlite:///./test.db"  # Change for PostgreSQL or MySQL

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# This Base is needed for Alembic
Base = declarative_base()


# def initialize_gcp_backend():


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    db_engine = create_async_engine(DATABASE_URL)
    db_session_factory = async_sessionmaker(
        db_engine,
        expire_on_commit=False,
    )
    app.state.db_engine = db_engine
    app.state.db_session_factory = db_session_factory


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        app.middleware_stack = None
        _setup_db(app)
        app.middleware_stack = app.build_middleware_stack()
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_engine.dispose()
        pass  # noqa: WPS420

    return _shutdown
