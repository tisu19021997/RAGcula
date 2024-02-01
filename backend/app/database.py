import asyncio
import sqlalchemy
from sqlmodel import create_engine, SQLModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy.engine import make_url

from app.config import POSTGRE_ASYNC_ENGINE, POSTGRE_ENGINE, POSTGRE_CONNECTION_STRING, VECTOR_STORE_TABLE_NAME

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

###

singleton_instance = None
did_run_setup = False


class CustomPGVectorStore(PGVectorStore):
    """
    Custom PGVectorStore that uses the same connection pool as the FastAPI app.
    """

    def _connect(self) -> None:
        # Use our existing app engine and session so we can use the same connection pool
        self._engine = engine
        self._session = SessionLocal
        self._async_engine = async_engine
        self._async_session = AsyncSessionLocal

    async def close(self) -> None:
        self._session.close_all()
        self._engine.dispose()

        await self._async_engine.dispose()

    def _create_tables_if_not_exists(self) -> None:
        pass

    def _create_extension(self) -> None:
        pass

    async def run_setup(self) -> None:
        global did_run_setup
        if did_run_setup:
            return
        self._initialize()

        async with self._async_session() as session:
            async with session.begin():
                statement = sqlalchemy.text(
                    "CREATE EXTENSION IF NOT EXISTS vector")
                await session.execute(statement)
                await session.commit()

        async with self._async_session() as session:
            async with session.begin():
                conn = await session.connection()
                # Create vector tables.
                await conn.run_sync(self._base.metadata.create_all)
                # Create all non-vector tables.
                await conn.run_sync(SQLModel.metadata.create_all)

        did_run_setup = True


async def get_vector_store_singleton() -> PGVectorStore:
    global singleton_instance
    if singleton_instance is not None:
        return singleton_instance
    url = make_url(POSTGRE_CONNECTION_STRING)
    singleton_instance = CustomPGVectorStore.from_params(
        url.host,
        url.port or 5432,
        url.database,
        url.username,
        url.password,
        VECTOR_STORE_TABLE_NAME,
        embed_dim=1024,
        # hybrid_search=True,
        # text_search_config="english"
    )
    return singleton_instance


async def check_database_connection(max_attempts: int = 30, sleep_interval: int = 1) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
                print(f"Connected to the database on attempt {attempt}.")
                return
        except Exception as e:
            print(
                f"Attempt {attempt}: Database is not yet available. Error: {e}")
            if attempt == max_attempts:
                raise ValueError(
                    f"Couldn't connect to database after {max_attempts} attempts."
                ) from e
            await asyncio.sleep(sleep_interval)
