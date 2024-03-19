import uuid as uuid_pkg
from pathlib import Path
from typing import Annotated, List

import aiofiles
import fsspec
from app.deps import get_rag_system_from_state
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from rag.systems.react_system import ReactSystem
from rag.utils import summarize_documents

from .crud import (
    create_documents,
    delete_document_by_id,
    get_all_documents,
    get_document_by_id,
)
from .models import Document

upload_router = r = APIRouter()

DEFAULT_STORAGE_DIR = Path.cwd() / "storage"


@r.post("/single")
async def upload(
    file: Annotated[UploadFile, File()],
    rag_system: Annotated[ReactSystem, Depends(get_rag_system_from_state)],
) -> Document:
    # TODO: build a Thread object.
    import time

    start = time.time()

    thread_uuid = "123"  # uuid4()
    thread_dir = DEFAULT_STORAGE_DIR / thread_uuid
    thread_dir.mkdir(parents=True, exist_ok=True)
    had_storage = (thread_dir / "docstore.json").exists()
    new_file_name = f"{str(uuid_pkg.uuid4())}.pdf"
    doc_id = uuid_pkg.uuid4()
    file_path = str(thread_dir / new_file_name)

    # Write uploaded file content to disk.
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Load and preprocess data to documents.
    fs = fsspec.filesystem("local")
    documents = rag_system.load_data(file_path, str(doc_id))
    # Build indices and also persist to disk.
    rag_system.build_indices(documents, str(doc_id))
    rag_system.save_upload_index(upload_id=str(doc_id), persist_dir=thread_dir)

    # Insert upload document to relational database.
    ref_doc_ids = [document.doc_id for document in documents]
    doc = Document(
        id=doc_id,
        display_name=file.filename,
        path=file_path,
        is_active=True,
        summary=summarize_documents(
            documents,
            rag_system.storage_context,
            index=rag_system.indices[str(doc_id)].summary,
        ),
        llama_index_metadata={
            "ref_doc_ids": ref_doc_ids,
            "index_ids": [
                indice.summary._index_struct.index_id
                for _, indice in rag_system.indices.items()
            ],
        },
    )
    doc_in_db = create_documents([doc])[0]

    # Build engine based on uploaded documents.
    rag_system.build_engine(uploads=get_all_documents())
    print(f"ETA: {(time.time() - start)%60}")
    return doc_in_db


@r.get("")
def get_upload(
    rag_system: Annotated[ReactSystem, Depends(get_rag_system_from_state)]
) -> List[Document]:
    uploads = get_all_documents()
    return uploads


@r.delete("")
async def delete_upload(
    document_id: str,
    rag_system: Annotated[ReactSystem, Depends(get_rag_system_from_state)],
) -> None:
    thread_uuid = "123"  # uuid4()
    thread_dir = DEFAULT_STORAGE_DIR / thread_uuid

    # Load the document to get its ref_doc_ids for index/docstore deletion.
    fs = fsspec.filesystem("local")
    document = get_document_by_id(document_id=document_id)
    fs.rm_file(document.path)

    # Delete from database.
    delete_document_by_id(document_id)

    # Delete the indices then persist again to reflect the changes.
    rag_system.delete_upload_index(
        str(document.id), document.llama_index_metadata["ref_doc_ids"]
    )

    uploads = get_all_documents()
    rag_system.save_indices(save_dir=thread_dir, fs=fs)
    rag_system.build_engine(uploads=uploads)
