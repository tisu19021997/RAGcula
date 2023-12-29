import logging
from typing import Annotated, List
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index import VectorStoreIndex
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
from app.utils.index import get_index, llm
from app.utils.auth import decode_access_token

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    data: Annotated[_ChatData, Depends(json_to_model(_ChatData))],
    index: Annotated[VectorStoreIndex, Depends(get_index)],
    payload: Annotated[dict, Depends(decode_access_token)]
):
    # logger = logging.getLogger("uvicorn")
    user_id = payload["user_id"]
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
        llm=llm,
        memory=ChatMemoryBuffer.from_defaults(token_limit=512),
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
