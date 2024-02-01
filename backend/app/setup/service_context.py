from llama_index import ServiceContext, set_global_service_context
from llama_index.text_splitter import TokenTextSplitter

from app.core.model import get_llm, get_embedding_model


def initialize_llamaindex_service_context():
    llm = get_llm()
    embed_model = get_embedding_model()

    # Transformations.
    text_splitter = TokenTextSplitter(
        separator=" ",
        chunk_size=embed_model.max_length,
        chunk_overlap=24,
        tokenizer=embed_model._tokenizer
    )

    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
        chunk_size=embed_model.max_length,
        chunk_overlap=24,
        transformations=[text_splitter]
    )
    set_global_service_context(service_context)
