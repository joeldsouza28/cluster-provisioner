from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

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


