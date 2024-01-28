import os
import logging
import sqlalchemy
from dotenv import find_dotenv, load_dotenv
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel

# from app.orm_models import Base
from app.db.session import (
    AsyncSessionLocal as AppAsyncSessionLocal,
    async_engine as app_async_engine,
    SessionLocal as AppSessionLocal,
    engine as app_engine
)


logger = logging.getLogger("uvicorn")

load_dotenv(find_dotenv())

singleton_instance = None
did_run_setup = False


class CustomPGVectorStore(PGVectorStore):
    """
    Custom PGVectorStore that uses the same connection pool as the FastAPI app.
    """

    def _connect(self) -> None:
        # Use our existing app engine and session so we can use the same connection pool
        self._engine = app_engine
        self._session = AppSessionLocal
        self._async_engine = app_async_engine
        self._async_session = AppAsyncSessionLocal

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
    url = make_url(os.environ["POSTGRE_CONNECTION_STRING"])
    singleton_instance = CustomPGVectorStore.from_params(
        url.host,
        url.port or 5432,
        url.database,
        url.username,
        url.password,
        os.environ["VECTOR_STORE_TABLE_NAME"],
        embed_dim=1024,
        # hybrid_search=True,
        # text_search_config="english"
    )
    return singleton_instance
