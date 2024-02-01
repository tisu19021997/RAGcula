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

from llama_index import VectorStoreIndex, SummaryIndex
from llama_index.llms import LlamaCPP
from llama_index.embeddings import HuggingFaceEmbedding

from app.utils.reader import PyMuPDFReader
from app.database import CustomPGVectorStore, get_vector_store_singleton, check_database_connection
from app.chat.router import chat_router
from app.upload.router import upload_router
from rag.systems.router_system import RouterSystem
from rag.default import Default

# TODO: restructure these
from app.setup.service_context import initialize_llamaindex_service_context

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

    # Set global ServiceContext for LlamaIndex.
    # initialize_llamaindex_service_context()

    rag_system = RouterSystem(
        data_loader=PyMuPDFReader(),
        llm=Default.llm(),
        embed_model=Default.embedding_model(),
    )

    yield {"rag_system": rag_system}

    # This section is run on app shutdown.
    del rag_system
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

app.include_router(chat_router, prefix="/api/chat")
app.include_router(upload_router, prefix="/api/upload")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
