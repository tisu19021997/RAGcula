from typing import List

from fastapi.responses import StreamingResponse

from app.utils.json import json_to_model
from app.utils.index import get_index, llm
from app.utils.prompt import get_refine_template, get_text_qa_template
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index import VectorStoreIndex
from llama_index.llms.base import MessageRole, ChatMessage
from llama_index.retrievers import VectorIndexRetriever
from llama_index.chat_engine import ContextChatEngine
from llama_index.memory import ChatMemoryBuffer
from pydantic import BaseModel

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]
    user: str


@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    data: _ChatData = Depends(json_to_model(_ChatData)),
    index: VectorStoreIndex = Depends(get_index),
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
    # TODO: change this to an user input/selection.
    print(data.user)
    index = index['Truc_Quynh_Resume']

    # query chat engine
    system_message = (
        "You are a professional job candidate who will answer the recruiter question using the context information."
        "If the question is out of scope, kindly apologize and refuse to answer."
    )
    prefix_messages = [ChatMessage(
        role="system", content=system_message)]
    retriever = VectorIndexRetriever(index=index, similarity_top_k=3)
    memory = ChatMemoryBuffer.from_defaults(token_limit=512)
    chat_engine = ContextChatEngine(
        retriever=retriever,
        llm=llm,
        memory=memory,
        prefix_messages=prefix_messages
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
