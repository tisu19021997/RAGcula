import logging
from app.utils.fs import get_s3_fs
from app.utils.reader import PDFReader

logger = logging.getLogger("uvicorn")


def ingest_user_documents(
    # user_document: BinaryIO,
    user_document_path: str,
    description: str,
    question: str,
    user_id: str,
):
    # PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(user_document_path, fs=get_s3_fs())

    # Add extra metadata on each node.
    for doc in documents:
        doc.metadata["user_id"] = user_id
        doc.metadata["description"] = description
        doc.metadata["question"] = question
        doc.metadata["is_active"] = True
        # Don't let the LLM see the file_name.
        doc.excluded_llm_metadata_keys = ["file_name", "user_id", "is_active"]
    return documents
