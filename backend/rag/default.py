from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.llama_cpp import LlamaCPP

from .prompt import completion_to_prompt_openchat, messages_to_prompt_openchat

DEFAULT_LLM_MODEL = "https://huggingface.co/TheBloke/Starling-LM-7B-alpha-GGUF/resolve/main/starling-lm-7b-alpha.Q5_K_M.gguf"
DEFAULT_EMB_MODEL = "BAAI/bge-large-en-v1.5"


class Default:
    @staticmethod
    def embedding_model() -> HuggingFaceEmbedding:
        embedding_model = HuggingFaceEmbedding(
            model_name=DEFAULT_EMB_MODEL, embed_batch_size=4, max_length=512
        )
        return embedding_model

    @staticmethod
    def llm() -> LlamaCPP:
        llm = LlamaCPP(
            model_url=DEFAULT_LLM_MODEL,
            max_new_tokens=1024,
            # context_window=8192,
            temperature=0.1,
            model_kwargs={"n_gpu_layers": -1, "chat_format": "openchat"},
            verbose=False,
            messages_to_prompt=messages_to_prompt_openchat,
            completion_to_prompt=completion_to_prompt_openchat,
        )
        return llm
