import uvicorn
import os
import logging
from typing import cast
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from llama_index.core import set_global_handler

from app.utils.reader import PyMuPDFReader
from app.database import CustomPGVectorStore, get_vector_store_singleton, check_database_connection
from app.chat.router import chat_router
from app.upload.router import upload_router
from rag.systems.router_system import RouterSystem

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

    rag_system = RouterSystem(data_loader=PyMuPDFReader())

    yield {"rag_system": rag_system}

    # This section is run on app shutdown.
    del rag_system
    await vector_store.close()

app = FastAPI(lifespan=lifespan)

if environment == "dev":
    # LLM debug.
    set_global_handler("simple")

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

app.include_router(chat_router, prefix="/api/chat")
app.include_router(upload_router, prefix="/api/upload")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
