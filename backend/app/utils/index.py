import logging
from pathlib import Path
from typing import Annotated
from fastapi import Depends
from llama_index import (
    StorageContext,
    load_index_from_storage,
)

from app.db.pg_vector import get_vector_store_singleton
from app.utils.fs import get_s3_fs
from app.utils.auth import decode_access_token
from app.db.crud import is_user_existed

DATA_DIR = Path("./data")  # directory containing the documents to index
logger = logging.getLogger("uvicorn")


async def get_index(
    token_payload: Annotated[dict, Depends(decode_access_token)]
):
    vector_store = await get_vector_store_singleton()
    user_id = token_payload["user_id"]
    s3 = get_s3_fs()

    if await is_user_existed(user_id):
        logger.info(
            f"{user_id} already in storage. Loading it into storage context.")
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=f"talking-resume/{user_id}",
            fs=s3)
        index = load_index_from_storage(storage_context, index_id=user_id)
        return index

# Provides an overview of my professional qualifications, relevant work experience, skills, education and notable accomplishments.

# What is your educational background?
# What work experience does you have?
# What skills do you possess?
# In your previous job, did you receive any notable awards?
