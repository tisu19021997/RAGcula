from pathlib import Path
from typing import Annotated
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.core.llms import MessageRole, ChatMessage

from app.database import get_vector_store_singleton
from rag.systems.router_system import RouterSystem
from rag.utils import get_storage_context
from .utils import json_to_model
from .schemas import ChatData

chat_router = r = APIRouter()

DEFAULT_STORAGE_DIR = Path.cwd() / "storage"


@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    data: Annotated[ChatData, Depends(json_to_model(ChatData))],
):
    thread_uuid = "123"  # uuid4()
    thread_dir = DEFAULT_STORAGE_DIR / thread_uuid
    vector_store = await get_vector_store_singleton()

    rag_system: RouterSystem = request.state.rag_system
    storage_context = get_storage_context(
        vector_store=vector_store,
        persist_dir=thread_dir,
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

    rag_system.build_retrievers(storage_context=storage_context)

    response = rag_system.engine.stream_chat(lastMessage.content, messages)

    # stream response
    async def event_generator():
        for token in response.response_gen:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
