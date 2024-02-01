import aiofiles
import fsspec
import uuid
from pathlib import Path
from typing import Annotated, List
from fastapi import APIRouter, File, Request, UploadFile, Form, Depends
from llama_index import StorageContext, VectorStoreIndex, SummaryIndex

from rag.fs import get_s3_fs, get_s3_boto_client
from rag.systems.router_system import RouterSystem
from app.auth import decode_access_token
from app.database import get_vector_store_singleton
from .crud import get_documents_by_user_id, create_documents, delete_document_by_id, get_document_by_id
from .models import Document


upload_router = r = APIRouter()

DEFAULT_STORAGE_DIR = Path.cwd() / "storage"


@r.post("/single")
async def upload(
    request: Request,
    description: Annotated[str, Form()],
    question: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    token_payload: Annotated[dict, Depends(decode_access_token)],
) -> Document:
    vector_store = await get_vector_store_singleton()
    rag_system: RouterSystem = request.state.rag_system
    user_id = token_payload["user_id"]

    # TODO: build a Thread object.
    thread_uuid = "123"  # uuid4()
    thread_dir = DEFAULT_STORAGE_DIR / thread_uuid
    thread_dir.mkdir(parents=True, exist_ok=True)
    new_file_name = f"{str(uuid.uuid4())}.pdf"
    file_path = str(thread_dir/new_file_name)

    # Write uploaded file content to disk.
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Load and preprocess data to documents.
    fs = fsspec.filesystem("local")
    documents = rag_system.load_data(file_path, fs=fs)

    # Save document ids for later delete/update.
    doc_ids = [document.doc_id for document in documents]
    doc = Document(
        display_name=file.filename,
        path=file_path,
        is_active=True,
        description=description,
        question=question,
        user_id=user_id,
        llamaindex_ref_doc_ids=doc_ids
    )
    # Insert to database.
    doc_in_db = create_documents([doc])[0]

    had_storage = (thread_dir / "docstore.json").exists()
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=thread_dir if had_storage else None,
    )

    # If storage has been created, just load persisted indices.
    # Else, initialize new indices.
    if had_storage:
        rag_system.load_indices(storage_context).docs_to_index(documents)
    else:
        rag_system.add_indice(VectorStoreIndex(
            [], storage_context=storage_context), namespace=thread_uuid)
        rag_system.add_indice(SummaryIndex(
            [], storage_context=storage_context), namespace=thread_uuid)
        rag_system.docs_to_index(documents)

    # Persist indices to storage.
    rag_system.save_indices(save_dir=thread_dir, fs=fs)

    return doc_in_db


@r.get("")
def get_upload(
    user_id: str,
) -> List[Document]:
    documents = get_documents_by_user_id(user_id)
    return documents


@r.delete("")
async def delete_upload(
    request: Request,
    document_id: str,
    user_id: str,
) -> None:
    # TODO: for each index, use delete_ref_doc to delete indices.
    thread_uuid = "123"  # uuid4()
    thread_dir = DEFAULT_STORAGE_DIR / thread_uuid
    vector_store = await get_vector_store_singleton()

    rag_system: RouterSystem = request.state.rag_system
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=thread_dir,
    )

    # Load the document to get its ref_doc_ids for index/docstore deletion.
    document = get_document_by_id(document_id=document_id)
    await delete_document_by_id(document_id, user_id)

    # Delete the file in storage.
    fs = fsspec.filesystem("local")
    fs.rm_file(document.path)

    # Delete the indices then persist again to reflect the changes.
    rag_system.delete_indices(
        storage_context, document.llamaindex_ref_doc_ids).save_indices(save_dir=thread_dir, fs=fs)
