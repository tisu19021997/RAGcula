import llama_index

from typing import Annotated
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.core.indices import EmptyIndex
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.llms import MessageRole, ChatMessage
from llama_index.core.retrievers import VectorIndexRetriever, SummaryIndexEmbeddingRetriever, RouterRetriever
from llama_index.core.tools import RetrieverTool
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler

from app.utils.json_to import json_to_model
from app.utils.index import get_index
from app.pydantic_models.chat import ChatData
from app.prompts.system import LLM_SYSTEM_MESSAGE
from rag.schemas import RagIndex

chat_router = r = APIRouter()


@r.post("")
async def chat(
    request: Request,
    # Note: To support clients sending a JSON object using content-type "text/plain",
    # we need to use Depends(json_to_model(_ChatData)) here
    data: Annotated[ChatData, Depends(json_to_model(ChatData))],
    index: Annotated[RagIndex, Depends(get_index)],
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
        index=index.vector,
        similarity_top_k=3,
    )
    summary_retriever = SummaryIndexEmbeddingRetriever(
        index=index.summary,
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
    empty_retriever = EmptyIndex().as_retriever()
    empty_tool = RetrieverTool.from_defaults(
        empty_retriever,
        description="Useful for questions not related to uploaded documents."
    )

    retriever = RouterRetriever(
        selector=LLMSingleSelector.from_defaults(
            # prompt_template_str=SINGLE_SELECTOR_PROMPT_TEMPLATE
        ),
        retriever_tools=[vs_tool, summary_tool, empty_tool]
    )

    chat_engine = ContextChatEngine(
        retriever=retriever,
        llm=llama_index.global_service_context.llm,
        memory=ChatMemoryBuffer.from_defaults(token_limit=4096),
        prefix_messages=[ChatMessage(
            role="system", content=LLM_SYSTEM_MESSAGE)],
        callback_manager=callback_manager,
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
