import uvicorn
import os
import logging
from typing import cast
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from app.db.pg_vector import CustomPGVectorStore, get_vector_store_singleton
from app.db.wait_for_db import check_database_connection
from app.api.api import api_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # first wait for DB to be connectable
    await check_database_connection()

    # initialize pg vector store singleton
    vector_store = await get_vector_store_singleton()
    vector_store = cast(CustomPGVectorStore, vector_store)
    await vector_store.run_setup()

    yield
    # This section is run on app shutdown
    await vector_store.close()

app = FastAPI(lifespan=lifespan)

# Default to 'development' if not set
environment = os.getenv("ENVIRONMENT", "dev")


if environment == "dev":
    logger = logging.getLogger("uvicorn")
    logger.warning(
        "Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
