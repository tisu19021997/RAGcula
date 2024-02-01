from pathlib import Path
from typing import Annotated, List
from fastapi import APIRouter, File, UploadFile, Form, Depends
from llama_index import StorageContext, VectorStoreIndex, SummaryIndex

from app.utils.auth import decode_access_token
from app.utils.fs import get_s3_fs, get_s3_boto_client
from app.db.pg_vector import get_vector_store_singleton
from app.db.crud import get_documents, create_documents, delete_document, is_user_existed
from app.orm_models import Document
from app.core.ingest import ingest_user_documents

upload_router = r = APIRouter()


@r.post("/single")
async def upload(
    description: Annotated[str, Form()],
    question: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    token_payload: Annotated[dict, Depends(decode_access_token)]
) -> Document:
    vector_store = await get_vector_store_singleton()
    user_id = token_payload["user_id"]
    user_s3_folder = Path(f"talking-resume/{user_id}")
    nodes = []

    # Have to use boto because I don't know how to write temporary file to s3 using f3fs.
    s3 = get_s3_boto_client()
    doc = Document(
        s3_path=f"{user_id}/{file.filename}",
        is_active=True,
        description=description,
        question=question,
        user_id=user_id,
    )
    # Create new record in db.
    doc_in_db = create_documents([doc])[0]
    doc_uuid = str(doc_in_db.id)

    # Save the document to S3.
    s3.upload_fileobj(
        file.file,
        "talking-resume",
        doc.s3_path,
    )
    nodes = ingest_user_documents(
        doc_uuid,
        f"talking-resume/{doc.s3_path}",
        doc.description,
        doc.question,
        doc.user_id
    )

    # Save documents indices and embeddings.
    s3 = get_s3_fs()
    persist_dir = None
    if await is_user_existed(user_id):
        persist_dir = f"talking-resume/{user_id}"

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=persist_dir,
        fs=s3)
    # Vector store index.
    vector_index = VectorStoreIndex.from_documents(
        documents=nodes, storage_context=storage_context, show_progress=True)
    vector_index.set_index_id(f'vector_{user_id}')
    vector_index.storage_context.persist(persist_dir=user_s3_folder, fs=s3)

    # Summary index.
    summary_index = SummaryIndex.from_documents(
        documents=nodes, storage_context=storage_context, show_progress=True)
    summary_index.set_index_id(f'summary_{user_id}')
    summary_index.storage_context.persist(persist_dir=user_s3_folder, fs=s3)

    return doc_in_db


@r.get("")
def get_upload(
    user_id: str,
) -> List[Document]:
    documents = get_documents(user_id)
    for document in documents:
        s3 = get_s3_boto_client()
        s3_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": "talking-resume",
                "Key": document.s3_path,
                "ResponseContentDisposition": "inline",
                "ResponseContentType": "application/pdf"})
        document.s3_url = s3_url
    return documents


@r.delete("")
async def delete_upload(
    document_id: str,
    user_id: str,
) -> None:
    await delete_document(document_id, user_id)
