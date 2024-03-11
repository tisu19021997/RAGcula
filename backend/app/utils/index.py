import logging
from pathlib import Path
from typing import Annotated
from fastapi import Depends
from llama_index.core import StorageContext, load_index_from_storage

from app.db.pg_vector import get_vector_store_singleton
from app.utils.fs import get_s3_fs
from app.utils.auth import decode_access_token
from app.db.crud import is_user_existed
from rag.schemas import RagIndex

DATA_DIR = Path("./data")  # directory containing the documents to index
logger = logging.getLogger("uvicorn")


async def get_index(
    token_payload: Annotated[dict, Depends(decode_access_token)]
) -> RagIndex:
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
        indices = {}
        for prefix in ["summary", "vector"]:
            indices[prefix] = load_index_from_storage(
                storage_context, index_id=f'{prefix}_{user_id}')
        return RagIndex(**indices)
