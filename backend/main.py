import uvicorn
import os
import logging
import llama_index
from typing import cast
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from firebase_admin import credentials, initialize_app

from app.db.pg_vector import CustomPGVectorStore, get_vector_store_singleton
from app.db.wait_for_db import check_database_connection
from app.api.api import api_router
from app.setup.service_context import initialize_llamaindex_service_context
from app.setup.tracing import initialize_tracing_service

load_dotenv()

cwd = Path.cwd()

# Default to 'development' if not set
environment = os.getenv("ENVIRONMENT", "dev")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # First wait for DB to be connectable.
    await check_database_connection()

    # Initialize pg vector store singleton.
    vector_store = await get_vector_store_singleton()
    vector_store = cast(CustomPGVectorStore, vector_store)
    await vector_store.run_setup()

    # Initialize firebase admin for authentication.
    cred = credentials.Certificate(cwd / 'firebase_creds.json')
    initialize_app(cred)

    # if environment == "dev":
    #     # Initialize observability service.
    #     initialize_tracing_service("wandb", "talking-resume")

    # Set global ServiceContext for LlamaIndex.
    initialize_llamaindex_service_context(environment)

    yield

    # This section is run on app shutdown.
    await vector_store.close()

app = FastAPI(lifespan=lifespan)

if environment == "dev":
    # LLM debug.
    llama_index.set_global_handler("simple")

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
