from llama_index.llms import LlamaCPP
from llama_index.embeddings import HuggingFaceEmbedding

MODEL_URL = "https://huggingface.co/TheBloke/neural-chat-7B-v3-1-GGUF/resolve/main/neural-chat-7b-v3-1.Q5_K_M.gguf"
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"


def get_llm(model_url=MODEL_URL):
    llm = LlamaCPP(
        model_url=model_url,
        max_new_tokens=1024,
        context_window=4096,
        temperature=0.1,
        model_kwargs={"n_gpu_layers": -1},
        verbose=False,
    )
    return llm


def get_embedding_model(model_name=EMBEDDING_MODEL_NAME):
    embed_model = HuggingFaceEmbedding(model_name=model_name)
    return embed_model
