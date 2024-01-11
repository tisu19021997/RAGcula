import llama_index

from pathlib import Path
from typing import Annotated, List
from fastapi.responses import StreamingResponse
from fastapi import (
    File,
    Form,
    UploadFile,
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)
from llama_index import StorageContext, VectorStoreIndex
from llama_index.llms.types import MessageRole, ChatMessage
from llama_index.retrievers import VectorIndexRetriever
from llama_index.chat_engine import ContextChatEngine
from llama_index.memory import ChatMemoryBuffer
from llama_index.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator
)

from app.utils.json_to import json_to_model
from app.utils.index import get_index
from app.utils.auth import decode_access_token
from app.pydantic_models.chat import ChatData
from app.db.crud import delete_all_documents_from_user, is_user_existed
from app.core.ingest import ingest_user_documents
from app.db.pg_vector import get_vector_store_singleton
from app.utils.fs import get_s3_fs, get_s3_boto_client

chat_router = r = APIRouter()


@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    data: Annotated[ChatData, Depends(json_to_model(ChatData))],
    index: Annotated[VectorStoreIndex, Depends(get_index)],
    token_payload: Annotated[dict, Depends(decode_access_token)]
):
    # logger = logging.getLogger("uvicorn")
    user_id = token_payload["user_id"]
    # Only need to retrieve indices from the current user.
    filters = MetadataFilters(
        filters=[
            MetadataFilter(
                key="user_id",
                operator=FilterOperator.EQ,
                value=user_id),
        ]
    )

    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]

    # query chat engine
    system_message = (
        "You are a professional job candidate who will answer the recruiter question using the context information."
        "If the question is out of scope, kindly apologize and refuse to answer."
    )
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=3,
        filters=filters,
    )
    chat_engine = ContextChatEngine(
        retriever=retriever,
        llm=llama_index.global_service_context.llm,
        memory=ChatMemoryBuffer.from_defaults(token_limit=2000),
        prefix_messages=[ChatMessage(role="system", content=system_message)]
    )
    response = chat_engine.stream_chat(lastMessage.content, messages)

    # stream response
    async def event_generator():
        for token in response.response_gen:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")


@r.post("/upload")
async def upload(
    descriptions: Annotated[List[str], Form()],
    questions: Annotated[List[str], Form()],
    files: Annotated[List[UploadFile], File()],
    token_payload: Annotated[dict, Depends(decode_access_token)]
):
    vector_store = await get_vector_store_singleton()
    user_id = token_payload["user_id"]
    user_s3_folder = Path(f"talking-resume/{user_id}")

    # TODO: smartly remove or inactivate documents instead of full deletion.
    if await is_user_existed(user_id):
        await delete_all_documents_from_user(user_id)

    nodes = []
    for user_document, description, question in zip(files, descriptions, questions):
        # Save the document to S3.
        # Have to use boto because I don't know how to write temporary file to s3 using f3fs.
        s3 = get_s3_boto_client()
        s3.upload_fileobj(
            user_document.file,
            "talking-resume",
            f"{user_id}/{user_document.filename}",
        )

        # Read the documents directly from S3 bucket since the temporary file is closed.
        # Ingest them to LlamaIndex Documents.
        nodes.extend(ingest_user_documents(
            user_s3_folder/user_document.filename, description, question, user_id))
        # await user_document.seek(0)

    s3 = get_s3_fs()
    # Save documents indices and embeddings.
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, fs=s3)
    index = VectorStoreIndex.from_documents(
        documents=nodes, storage_context=storage_context)
    index.set_index_id(user_id)
    index.storage_context.persist(persist_dir=user_s3_folder, fs=s3)
