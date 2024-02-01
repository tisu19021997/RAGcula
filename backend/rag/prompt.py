from typing import Sequence
from llama_index.llms.types import (
    ChatMessage,
    MessageRole,
)

# Default system message for LLM.
LLM_SYSTEM_MESSAGE = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, just say that you don't know. Keep the answer concise."
)

#####

# Selector prompts for RouterQueryEngine.
SINGLE_SELECTOR_PROMPT_TEMPLATE = (
    "### System:\n"
    "You are a helpful assistant. "
    "Using only the choices above and not prior knowledge, return "
    "the choice that is most relevant to the question: '{query_str}'\n"
    "### User:\n"
    "Some choices are given below. It is provided in a numbered list "
    "(1 to {num_choices}), "
    "where each item in the list corresponds to a summary.\n"
    "---------------------\n"
    "{context_list}"
    "\n---------------------\n"
)

MULTI_SELECT_PROMPT_TEMPLATE = (
    "### System:\n"
    "You are a helpful assistant. "
    "Using only the choices above and not prior knowledge, return the top choices "
    "(no more than {max_outputs}, but only select what is needed) that "
    "are most relevant to the question: '{query_str}'\n"

    "### User:\n"
    "Some choices are given below. It is provided in a numbered "
    "list (1 to {num_choices}), "
    "where each item in the list corresponds to a summary.\n"
    "---------------------\n"
    "{context_list}"
    "\n---------------------\n"
)


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
