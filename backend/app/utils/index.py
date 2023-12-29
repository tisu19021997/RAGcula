import logging
from glob import glob
from pathlib import Path
from typing import Annotated
from fastapi import Depends
from llama_index import (
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    ServiceContext,
    download_loader
)

from app.utils.model import get_llm, get_embedding_model
from app.db.pg_vector import get_vector_store_singleton
from app.chat.engine import get_s3_fs
from app.utils.auth import decode_access_token

DATA_DIR = Path("./data")  # directory containing the documents to index
logger = logging.getLogger("uvicorn")

# TODO: allow user to config the model?
llm = get_llm()
embed_model = get_embedding_model()
embed_dim = embed_model._model.config.hidden_size

service_context = ServiceContext.from_defaults(
    llm=llm,
    embed_model=embed_model,
    chunk_size=128,
    chunk_overlap=32,
)
# PDF loader.
PDFReader = download_loader("PDFReader")
loader = PDFReader()
s3 = get_s3_fs()


async def get_index(
    payload: Annotated[dict, Depends(decode_access_token)]
):
    vector_store = await get_vector_store_singleton(embed_dim=embed_dim)
    user_id = payload["user_id"]
    user_s3_folder = f"talking-resume/{user_id}"
    nodes = []

    if s3.exists(user_s3_folder):
        logger.info(
            f"{user_id} already in storage. Loading it into storage context.")
        storage_context = StorageContext.from_defaults(
            persist_dir=user_s3_folder,
            vector_store=vector_store,
            fs=s3
        )
        index = load_index_from_storage(
            storage_context,
            index_id=user_id,
            service_context=service_context,
        )
    else:
        # TODO: let user upload their own files and save these to S3.
        for file in glob(str(DATA_DIR / '*.pdf')):
            file = Path(file)
            file_name = file.stem
            if "Portfolio" in file_name:
                descr = (
                    "Useful for questions related to projects that I has done."
                )
            elif "Resume" in file_name:
                descr = (
                    "Useful for questions related to my background, skills, education, and accomplishments."
                )
            documents = loader.load_data(file)

            # Add extra metadata on each node.
            for doc in documents:
                doc.metadata["description"] = descr
                doc.metadata["user_id"] = user_id
                # Don't let the LLM see the file_name.
                doc.excluded_llm_metadata_keys = ["file_name"]
            nodes.extend(documents)

        logger.info(f"New user {user_id}. Creating new storage context on S3.")
        # Create index and persist to s3 storage.
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, fs=s3)
        index = VectorStoreIndex.from_documents(
            nodes,
            storage_context=storage_context,
            service_context=service_context,
        )
        index.set_index_id(user_id)

        # Persist index to s3.
        index.storage_context.persist(persist_dir=user_s3_folder, fs=s3)

    return index
