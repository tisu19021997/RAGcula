from typing import Sequence

from llama_index.core.llms import ChatMessage, MessageRole

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

SIMPLE_CHAT_SYSTEM_PROMPT = "You are a helpful assistant."


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

    string_messages.append(f"### {MessageRole.ASSISTANT.value.capitalize()}:\n")
    return "\n".join(string_messages)


def completion_to_prompt_alpaca(prompt: str) -> str:
    prompt = "### User:\n" f"{prompt}" "### Assistant:\n"
    return prompt


def messages_to_prompt_openchat(messages: Sequence[ChatMessage]) -> str:
    _roles = dict(
        system="",
        user="GPT4 Correct User: ",
        assistant="<|end_of_turn|>GPT4 Correct Assistant: ",
    )
    string_messages = []
    for message in messages:
        role = message.role
        content = message.content

        if role == MessageRole.SYSTEM:
            string_message = f"{content}<|end_of_turn|>"
        else:
            string_message = f"{_roles[role.value]}\n{content}\n"

        addtional_kwargs = message.additional_kwargs
        if addtional_kwargs:
            string_message += f"\n{addtional_kwargs}"
        string_messages.append(string_message)

    string_messages.append(f"{MessageRole.ASSISTANT.value.capitalize()}:\n")
    return "\n".join(string_messages)


def completion_to_prompt_openchat(prompt: str) -> str:
    prompt = f"GPT4 Correct User: {prompt}<|end_of_turn|>GPT4 Correct Assistant:"
    return prompt
