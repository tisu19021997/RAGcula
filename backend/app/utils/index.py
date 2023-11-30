import logging
import os
from glob import glob
from pathlib import Path
from app.utils.model import get_llm, get_embedding_model
from llama_index import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    ServiceContext,
    download_loader
)

STORAGE_DIR = Path("./storage")  # directory to cache the generated index
DATA_DIR = Path("./data")  # directory containing the documents to index

# TODO: currently only use the default models.
llm = get_llm()
embed_model = get_embedding_model()

service_context = ServiceContext.from_defaults(
    llm=llm,
    embed_model=embed_model,
    chunk_size=128,
    chunk_overlap=32,
)
# PDF loader.
PDFReader = download_loader("PDFReader")
loader = PDFReader()


def get_index():
    logger = logging.getLogger("uvicorn")
    index_set = {}
    # check if storage already exists
    if not os.path.exists(STORAGE_DIR):
        logger.info("Creating new index")
        # load the documents and create the index
        for file in glob(str(DATA_DIR / '*.pdf')):
            file = Path(file)
            # Load the documents.
            documents = loader.load_data(file)
            # Create index and persist to storage.
            index = VectorStoreIndex.from_documents(
                documents,
                service_context=service_context,
            )
            index_set[file.stem] = index
            index.storage_context.persist(STORAGE_DIR / file.stem)
            logger.info(
                f"Finished creating new index. Stored in {STORAGE_DIR / file.stem}")
    else:
        for dir in glob(str(STORAGE_DIR / '*')):
            dir = Path(dir)
            logger.info(f"Loading index from {dir}...")
            storage_context = StorageContext.from_defaults(persist_dir=dir)
            index = load_index_from_storage(
                storage_context, service_context=service_context)
            index_set[dir.stem] = index
            logger.info(f"Finished loading index from {STORAGE_DIR}")
    return index_set
