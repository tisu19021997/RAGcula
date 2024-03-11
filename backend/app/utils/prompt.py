from llama_index.core import PromptTemplate
from typing import Sequence
from llama_index.core.llms import ChatMessage, MessageRole

QA_PROMPTS = {
    "neural-chat-7b": (
        "### System:\n"
        "You are a helpful assistant. Using the context information and not prior knowledge, "
        "answer the query correctly. "
        "If you don't know the answer, just say it.\n"
        "### User:\n"
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Query: {query_str}\n"
        "### Assistant: "
    )
}

REFINE_PROMPTS = {
    "neural-chat-7b": (
        "### System:\n"
        "You are a helpful assistant. Given an original query, an existing answer and a new context, refine the original answer to better answer the query. "
        "If the context isn't useful, return the original answer.\n"
        "### User:\n"
        "The original query is as follows: {query_str}\n"
        "We have provided an existing answer: {existing_answer}\n"
        "We have the opportunity to refine the existing answer (only if needed) with some more context below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "### Assistant: "
    )
}


def get_text_qa_template(model="neural-chat-7b"):
    assert model in QA_PROMPTS, f'{model} not in {list(QA_PROMPTS.keys())}'
    return PromptTemplate(QA_PROMPTS[model])


def get_refine_template(model="neural-chat-7b"):
    assert model in REFINE_PROMPTS, f'{model} not in {list(REFINE_PROMPTS.keys())}'
    return PromptTemplate(REFINE_PROMPTS[model])


def messages_to_prompt_alpaca(messages: Sequence[ChatMessage]) -> str:
    """Convert messages to a prompt string."""
    string_messages = []
    for message in messages:
        role = message.role
        content = message.content
        string_message = f"### {role.value.capitalize()}:\n{content}\n"

        addtional_kwargs = message.additional_kwargs
        if addtional_kwargs:
            string_message += f"\n{addtional_kwargs}"
        string_messages.append(string_message)

    string_messages.append(
        f"### {MessageRole.ASSISTANT.value.capitalize()}:\n")
    return "\n".join(string_messages)
