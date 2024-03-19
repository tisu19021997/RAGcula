import uuid as uuid_pkg
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Self, Sequence, Union

from fsspec import AbstractFileSystem
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    load_indices_from_storage,
)
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.data_structs.data_structs import IndexStruct
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.indices import SummaryIndex, VectorStoreIndex
from llama_index.core.indices.base import BaseIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.llms import LLM
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.readers.base import BaseReader
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import TransformComponent
from llama_index.vector_stores.postgres import PGVectorStore
from pydantic import BaseModel, ConfigDict
from rag.default import Default


class DocumentIndices(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    indices: List[Union[VectorStoreIndex, SummaryIndex]]

    @property
    def vector(self) -> VectorStoreIndex:
        for index in self.indices:
            if isinstance(index, VectorStoreIndex):
                return index
        raise AttributeError("No VectorStoreIndex found for the given document")

    @property
    def summary(self) -> SummaryIndex:
        for index in self.indices:
            if isinstance(index, SummaryIndex):
                return index
        raise AttributeError("No SummaryIndex found for the given document")


class BaseSystem(ABC):
    data_loader: BaseReader
    llm: LLM
    embed_model: BaseEmbedding
    indices: Dict[str, DocumentIndices] = None
    storage_context: StorageContext
    response_composer: BaseSynthesizer
    context_retriever: BaseRetriever
    engine: Union[BaseQueryEngine, BaseChatEngine] = None
    documents: List[Document] = None
    vector_store: PGVectorStore = None
    ingestion_pipeline: IngestionPipeline = None

    def __init__(
        self,
        data_loader: BaseReader,
        transformations: List[TransformComponent],
        llm: Optional[LLM] = None,
        embed_model: Optional[BaseEmbedding] = None,
        response_composer: Optional[BaseSynthesizer] = None,
        vector_store: Optional[PGVectorStore] = None,
        storage_context: Optional[StorageContext] = None,
        # retriever: BaseRetriever
    ) -> "BaseSystem":
        self.data_loader = data_loader
        self.response_composer = response_composer
        self.vector_store = vector_store
        self.storage_context = storage_context

        Settings.llm = llm or Default.llm()
        Settings.embed_model = embed_model or Default.embedding_model()
        Settings.chunk_size = Settings.embed_model.max_length
        Settings.transformations = transformations

        # self.retriever = retriever

    @abstractmethod
    def load_data(self):
        raise NotImplementedError("load_data not implemented")

    @abstractmethod
    def build_indices(self):
        raise NotImplementedError("build_indices not implemented")

    @abstractmethod
    def delete_upload_index(self):
        raise NotImplementedError("delete_upload_index not implemented")

    @abstractmethod
    def build_engine(self):
        raise NotImplementedError("build_engine not implemented")

    @abstractmethod
    def add_indices(self):
        raise NotImplementedError("add_indices not implemented")

    def load_indices(
        self, storage_context: StorageContext, force_reload: bool = False
    ) -> Self:
        # If there are already indices, just return it.
        if not self.indices or force_reload:
            self.indices = load_indices_from_storage(storage_context=storage_context)
        return self

    # TODO: implement method to print tree structure of the system.
    # just like Haystack pipeline.draw().
    def __str__(self) -> str:
        # pygraphviz
        return f"Engine={self.engine}"

    def docs_to_index(self, documents: List[Document]) -> Self:
        for doc_id, indices in self.indices.items():
            for document in documents:
                document.metadata["doc_uuid"] = doc_id
                document.excluded_llm_metadata_keys = ["doc_uuid"]
                for index in indices.indices:
                    index.insert(document)
        return self

    def save_indices(
        self, save_dir: Union[Path, str], fs: Optional[AbstractFileSystem] = None
    ) -> Self:
        self.storage_context.persist(persist_dir=save_dir, fs=fs)
        return self

    def chat(self):
        """Chat using chat engine"""
