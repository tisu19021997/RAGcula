from pathlib import Path
from typing import Annotated

from app.database import get_vector_store_singleton
from app.deps import get_rag_system_from_state
from app.upload.crud import get_all_documents
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from llama_index.core.llms import ChatMessage, MessageRole
from rag.systems.base import BaseSystem
from rag.systems.react_system import ReactSystem
from rag.utils import get_storage_context

from .schemas import ChatData
from .utils import json_to_model

chat_router = r = APIRouter()

DEFAULT_STORAGE_DIR = Path.cwd() / "storage"


@r.post("")
async def chat(
    request: Request,
    data: Annotated[ChatData, Depends(json_to_model(ChatData))],
    rag_system: Annotated[ReactSystem, Depends(get_rag_system_from_state)],
):
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

    # uploads = get_all_documents()
    # rag_system.build_engine(uploads=uploads)
    rag_system.engine.reset()
    response = rag_system.engine.stream_chat(
        lastMessage.content,
        # messages
    )

    # stream response
    async def event_generator():
        for token in response.response_gen:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
