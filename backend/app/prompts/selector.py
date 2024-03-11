from llama_index.core import PromptTemplate
from llama_index.core.prompts import PromptType

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

SELECTOR_PROMPT = PromptTemplate(
    template=SINGLE_SELECTOR_PROMPT_TEMPLATE, prompt_type=PromptType.SINGLE_SELECT
)
