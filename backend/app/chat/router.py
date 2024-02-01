import llama_index

from typing import Annotated
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.indices.empty import EmptyIndex
from llama_index.selectors.llm_selectors import LLMSingleSelector
from llama_index.llms.types import MessageRole, ChatMessage
from llama_index.retrievers import VectorIndexRetriever, SummaryIndexEmbeddingRetriever, RouterRetriever
from llama_index.tools import RetrieverTool
from llama_index.chat_engine import ContextChatEngine
from llama_index.memory import ChatMemoryBuffer
from llama_index.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.callbacks import CallbackManager, LlamaDebugHandler

from app.auth import decode_access_token
from rag.systems.router_system import RouterSystem
from rag.index import load_indices
from rag.prompt import LLM_SYSTEM_MESSAGE
from .utils import json_to_model
from .schemas import ChatData

chat_router = r = APIRouter()


@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    token_payload: Annotated[dict, Depends(decode_access_token)],
    data: Annotated[ChatData, Depends(json_to_model(ChatData))],
):
    # logger = logging.getLogger("uvicorn")
    user_id = token_payload["user_id"]
    # indices = await load_indices(user_id)
    rag_system: RouterSystem = request.state.rag_system
    # indices = rag_system.load_indices()

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

    rag_system.build_retrievers()

    response = rag_system.engine.stream_chat(lastMessage.content, messages)

    # stream response
    async def event_generator():
        for token in response.response_gen:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
