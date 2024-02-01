from app.config import POSTGRE_ASYNC_ENGINE, POSTGRE_ENGINE
from sqlmodel import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(
    POSTGRE_ASYNC_ENGINE,
    pool_pre_ping=True,
    pool_size=4,  # Number of connections to keep open in the pool
    max_overflow=4,  # Number of connections that can be opened beyond the pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
    # Raise an exception after 2 minutes if no connection is available from the pool
    pool_timeout=120,
)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine)

engine = create_engine(
    POSTGRE_ENGINE,
    pool_pre_ping=True,
    pool_size=4,
    max_overflow=4,
    pool_recycle=3600,
    pool_timeout=120,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)
