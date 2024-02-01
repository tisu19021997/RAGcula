from llama_index.llms import LlamaCPP
from llama_index.embeddings import HuggingFaceEmbedding

from .prompt import messages_to_prompt_alpaca

DEFAULT_LLM_MODEL = "https://huggingface.co/TheBloke/SOLAR-10.7B-Instruct-v1.0-GGUF/resolve/main/solar-10.7b-instruct-v1.0.Q5_K_M.gguf"
DEFAULT_EMB_MODEL = "BAAI/bge-large-en-v1.5"


class Default:
    @staticmethod
    def embedding_model() -> HuggingFaceEmbedding:
        embedding_model = HuggingFaceEmbedding(
            model_name=DEFAULT_EMB_MODEL, embed_batch_size=4)
        return embedding_model

    @staticmethod
    def llm() -> LlamaCPP:
        llm = LlamaCPP(
            model_url=DEFAULT_LLM_MODEL,
            max_new_tokens=1024,
            context_window=4096,
            temperature=0.1,
            model_kwargs={"n_gpu_layers": -1, "chat_format": "llama-2"},
            verbose=False,
            messages_to_prompt=messages_to_prompt_alpaca,
        )
        return llm
