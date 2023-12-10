from llama_index import VectorStoreIndex
from llama_index.retrievers import VectorIndexRetriever
from llama_index.tools import ToolMetadata, RetrieverTool
from llama_index.agent import ReActAgent
from llama_index.vector_stores.types import MetadataFilters, ExactMatchFilter


def get_agent_for_index(index: VectorStoreIndex):
    filters = None
    retriever = VectorIndexRetriever(index=index, similarity_top_k=2, )
    doc_tool = RetrieverTool(
        retriever=retriever,
        metadata=ToolMetadata(
            description=""
        )
    )

    chat_engine = index.as_chat_engine()
