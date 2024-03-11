from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from .default import DEFAULT_LLM_MODEL, DEFAULT_EMB_MODEL
from .prompt import messages_to_prompt_alpaca


def get_llm(model_url: str = DEFAULT_LLM_MODEL) -> LlamaCPP:
    # TODO: create a class to dynamically select correct prompt for model.
    llm = LlamaCPP(
        model_url=model_url,
        max_new_tokens=1024,
        context_window=4096,
        temperature=0.1,
        model_kwargs={"n_gpu_layers": -1, "chat_format": "llama-2"},
        verbose=False,
        messages_to_prompt=messages_to_prompt_alpaca,
    )
    return llm


def get_embedding_model(model_name: str = DEFAULT_EMB_MODEL) -> HuggingFaceEmbedding:
    embed_model = HuggingFaceEmbedding(
        model_name=model_name, embed_batch_size=4)
    return embed_model
