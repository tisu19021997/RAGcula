import logging
from glob import glob
from pathlib import Path
from torch import preserve_format
from app.utils.model import get_llm, get_embedding_model
from app.db.pg_vector import get_vector_store_singleton
from app.chat.engine import get_s3_fs
from llama_index import (
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    ServiceContext,
    download_loader
)

DATA_DIR = Path("./data")  # directory containing the documents to index

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

# TODO: get user from the current session.
user = "Truc_Quynh"

# async def get_index():
#     logger = logging.getLogger("uvicorn")
#     # check if storage already exists
#     for file in glob(str(DATA_DIR / '*.pdf')):
#         file = Path(file)
#         s3_bucket_path = f"stoarge/{file_id}"
#         # TODO: get the embedding size automatically.
#         vector_store = await get_vector_store_singleton(embed_dim=1024)

#         # If the vectors already existed on S3, load it.
#         if os.path.exists(s3_bucket_path):
#             logger.info(
#                 f"{file_id} existed in S3. Loading it into storage context.")
#             storage_context = StorageContext.from_defaults(
#                 persist_dir=s3_bucket_path,
#                 vector_store=vector_store,
#                 # fs=s3
#             )
#             index = load_index_from_storage(
#                 storage_context,
#                 index_id=file_id,
#                 service_context=service_context,
#             )
#             return index

#         # Else, create new storage context.
#         # Load the documents.
#         logger.info("Creating new storage context on S3.")
#         documents = loader.load_data(file)
#         # Create index and persist to storage.
#         storage_context = StorageContext.from_defaults(
#             vector_store=vector_store,
#             # fs=s3
#         )
#         index = VectorStoreIndex.from_documents(
#             documents,
#             storage_context=storage_context,
#             service_context=service_context,
#         )
#         index.set_index_id(file_id)
#         # Persist index to s3.
#         index.storage_context.persist(persist_dir=s3_bucket_path)

#     return index


async def get_index():
    logger = logging.getLogger("uvicorn")
    # logger.info(f"Current user: {user}")
    indices = {}
    for file in glob(str(DATA_DIR / '*.pdf')):
        file = Path(file)
        file_id = file.stem

        # TODO: each document requires a description
        # we need that information from the user when they upload the file.
        # first, let's just hardcode it for now.
        if "Portfolio" in file.stem:
            descr = (
                "Useful for questions related to projects that I has done."
            )
        elif "Resume" in file.stem:
            descr = (
                "Useful for questions related to my background, skills, education, and accomplishments."
            )
        s3_bucket_path = f"talking-resume/{file_id}"
        vector_store = await get_vector_store_singleton(embed_dim=embed_dim)

        # If the vectors already existed on S3, load it.
        if s3.exists(s3_bucket_path):
            logger.info(
                f"{file_id} exists in storage. Loading it into storage context.")
            storage_context = StorageContext.from_defaults(
                persist_dir=s3_bucket_path,
                vector_store=vector_store,
                fs=s3
            )
            index = load_index_from_storage(
                storage_context,
                index_id=file_id,
                service_context=service_context,
            )
        else:
            # Else, create new storage context.
            # Load the documents.
            logger.info("Creating new storage context on S3.")
            documents = loader.load_data(file)
            for doc in documents:
                doc.metadata["description"] = descr
                # Don't let the LLM see the file_name.
                doc.excluded_llm_metadata_keys = ["file_name"]

            # Create index and persist to storage.
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, fs=s3)
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                service_context=service_context,
            )
            index.set_index_id(file_id)
            # Persist index to s3.
            index.storage_context.persist(persist_dir=s3_bucket_path, fs=s3)
        indices[file_id] = index
    return indices
