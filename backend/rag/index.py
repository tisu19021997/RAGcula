import logging
from pathlib import Path
from llama_index import StorageContext, load_index_from_storage, load_indices_from_storage

from app.database import get_vector_store_singleton
from .schemas import RagIndex
from .fs import get_s3_fs

DATA_DIR = Path("./data")  # directory containing the documents to index
logger = logging.getLogger("uvicorn")


async def load_indices(
    user_id: str
) -> RagIndex:
    vector_store = await get_vector_store_singleton()
    s3 = get_s3_fs()

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
