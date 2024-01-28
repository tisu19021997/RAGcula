from urllib import response
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
from llama_index import StorageContext, VectorStoreIndex, SummaryIndex
from llama_index.selectors.llm_selectors import LLMSingleSelector
from llama_index.llms.types import MessageRole, ChatMessage
from llama_index.retrievers import VectorIndexRetriever, SummaryIndexEmbeddingRetriever, RouterRetriever
from llama_index.tools import RetrieverTool
from llama_index.chat_engine import ContextChatEngine
from llama_index.memory import ChatMemoryBuffer
from llama_index.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator
)

from llama_index.callbacks import CallbackManager, LlamaDebugHandler

from app.utils.json_to import json_to_model
from app.utils.index import get_index
from app.utils.auth import decode_access_token
from app.utils.fs import get_s3_fs, get_s3_boto_client
from app.db.pg_vector import get_vector_store_singleton
from app.db.crud import get_documents, create_documents, delete_document, is_user_existed
from app.pydantic_models.chat import ChatData
from app.orm_models import Document
from app.core.ingest import ingest_user_documents
from app.prompts.system import LLM_SYSTEM_MESSAGE
from app.prompts.selector import MULTI_SELECT_PROMPT_TEMPLATE, SINGLE_SELECTOR_PROMPT_TEMPLATE

chat_router = r = APIRouter()


@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    data: Annotated[ChatData, Depends(json_to_model(ChatData))],
    index: Annotated[dict, Depends(get_index)],
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
    # system_message = (
    #     "You are a professional job candidate who will answer the recruiter question using the context information."
    #     "If the question is out of scope, kindly apologize and refuse to answer."
    # )

    # Callbacks for observability.
    # TODO: this is not working.
    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])

    vs_retriever = VectorIndexRetriever(
        index=index["vector"],
        similarity_top_k=3,
        filters=filters,
    )
    summary_retriever = SummaryIndexEmbeddingRetriever(
        index=index["summary"],
        similarity_top_k=3,
    )

    vs_tool = RetrieverTool.from_defaults(
        retriever=vs_retriever,
        description="Useful for retrieving specific context from uploaded documents."
    )
    summary_tool = RetrieverTool.from_defaults(
        retriever=summary_retriever,
        description="Useful to retrieve all context from uploaded documents and summary tasks. Don't use if the question only requires more specific context."
    )

    # TODO: correct the prompt used by LLM to use router retriever.
    retriever = RouterRetriever(
        selector=LLMSingleSelector.from_defaults(
            # prompt_template_str=SINGLE_SELECTOR_PROMPT_TEMPLATE
        ),
        retriever_tools=[vs_tool, summary_tool]
    )

    chat_engine = ContextChatEngine(
        retriever=vs_retriever,
        llm=llama_index.global_service_context.llm,
        memory=ChatMemoryBuffer.from_defaults(token_limit=4096),
        prefix_messages=[ChatMessage(
            role="system", content=LLM_SYSTEM_MESSAGE)],
        callback_manager=callback_manager,
    )
    print(chat_engine._retriever.get_prompts())

    response = chat_engine.stream_chat(lastMessage.content, messages)

    # stream response
    async def event_generator():
        for token in response.response_gen:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")


@r.post("/upload/single")
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


@r.get("/upload")
def get_upload(
    user_id: str,
    token_payload: Annotated[dict, Depends(decode_access_token)]
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


@r.delete("/upload")
async def delete_upload(
    document_id: str,
    user_id: str,
) -> None:
    await delete_document(document_id, user_id)


@r.post("/upload/multiple")
async def upload(
    descriptions: Annotated[List[str], Form()],
    questions: Annotated[List[str], Form()],
    files: Annotated[List[UploadFile], File()],
    token_payload: Annotated[dict, Depends(decode_access_token)]
) -> List[Document]:
    vector_store = await get_vector_store_singleton()
    user_id = token_payload["user_id"]
    user_s3_folder = Path(f"talking-resume/{user_id}")

    # TODO: smartly remove or inactivate documents instead of full deletion.
    # if await is_user_existed(user_id):
    #     await delete_all_documents_from_user(user_id)

    # Have to use boto because I don't know how to write temporary file to s3 using f3fs.
    s3 = get_s3_boto_client()
    nodes = []
    docs = []
    for user_document, description, question in zip(files, descriptions, questions):
        doc = Document(
            s3_path=f"{user_id}/{user_document.filename}",
            is_active=True,
            description=description,
            question=question,
            user_id=user_id,
        )

        # Save the document to S3.
        s3.upload_fileobj(
            user_document.file,
            "talking-resume",
            doc.s3_path,
        )
        nodes.extend(ingest_user_documents(
            f"talking-resume/{doc.s3_path}", doc.description, doc.question, doc.user_id))
        docs.append(doc)

    # Save documents indices and embeddings.
    s3 = get_s3_fs()
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, fs=s3)

    # Vector store index.
    vector_index = VectorStoreIndex.from_documents(
        documents=nodes, storage_context=storage_context)
    vector_index.set_index_id(user_id)
    vector_index.storage_context.persist(persist_dir=user_s3_folder, fs=s3)

    # Create new record in db.
    docs = create_documents(docs)
    return docs
