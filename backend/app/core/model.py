from llama_index.llms import LlamaCPP
from llama_index.embeddings import HuggingFaceEmbedding
from app.utils.prompt import messages_to_prompt_alpaca

MODEL_URL = "https://huggingface.co/TheBloke/SOLAR-10.7B-Instruct-v1.0-GGUF/resolve/main/solar-10.7b-instruct-v1.0.Q5_K_M.gguf"
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"


def get_llm(model_url=MODEL_URL):
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


def get_embedding_model(model_name=EMBEDDING_MODEL_NAME):
    embed_model = HuggingFaceEmbedding(
        model_name=model_name, embed_batch_size=4)
    return embed_model
