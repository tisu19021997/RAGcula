from llama_index import ServiceContext, set_global_service_context
from app.utils.model import get_llm, get_embedding_model


def initialize_llamaindex_service_context():
    llm = get_llm()
    embed_model = get_embedding_model()

    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
        chunk_size=512,
        chunk_overlap=32,
    )
    set_global_service_context(service_context)
