from typing import Any, List, Mapping, Optional, Union, Self
from fsspec import AbstractFileSystem
from pathlib import Path
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict
from llama_index import StorageContext, ServiceContext, load_indices_from_storage
from llama_index.readers.base import BaseReader
from llama_index.llms.llm import LLM
from llama_index.embeddings.base import BaseEmbedding
from llama_index.response_synthesizers.base import BaseSynthesizer
from llama_index.core import BaseRetriever, BaseQueryEngine
from llama_index.schema import TransformComponent
from llama_index.indices.base import BaseIndex
from llama_index.data_structs.data_structs import IndexStruct
from llama_index.chat_engine.types import BaseChatEngine
from llama_index.schema import Document


class Indexer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    index: BaseIndex[IndexStruct]
    retriever_kwargs: Mapping[str, Any]
    description: str


class BaseSystem(ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data_loader: BaseReader
    llm: LLM
    embed_model: BaseEmbedding
    transformations: List[TransformComponent]
    indices: List[BaseIndex[IndexStruct]] = None
    storage: StorageContext
    response_composer: BaseSynthesizer
    context_retriever: BaseRetriever
    service_context: ServiceContext = None
    engine: Union[BaseQueryEngine, BaseChatEngine] = None
    documents: List[Document] = None

    def __init__(
        self,
        data_loader: BaseReader,
        llm: LLM,
        embed_model: BaseEmbedding,
        transformations: List[TransformComponent],
        service_context: Optional[ServiceContext] = None,
        response_composer: Optional[BaseSynthesizer] = None,
        # retriever: BaseRetriever
    ) -> "BaseSystem":
        self.data_loader = data_loader
        self.llm = llm
        self.embed_model = embed_model
        self.transformations = transformations
        self.response_composer = response_composer
        self.service_context = service_context

        # self.retriever = retriever

    @abstractmethod
    def load_data(self):
        raise NotImplementedError("load_data not implemented")

    @abstractmethod
    def delete_indices(self):
        raise NotImplementedError("delete_indices not implemented")

    @abstractmethod
    def build_retrievers(self):
        raise NotImplementedError("build_retrievers not implemented")

    def add_indice(self, index: BaseIndex[IndexStruct], namespace: str) -> Self:
        index.set_index_id(
            f"{namespace}.{index.index_struct.get_type().value}")
        if not self.indices:
            self.indices = []
        self.indices.append(index)
        return self

    def load_indices(self, storage_context: StorageContext) -> Self:
        # If there are already indices, just return it.
        if not self.indices:
            self.indices = load_indices_from_storage(
                storage_context=storage_context)
        return self

    # TODO: implement method to print tree structure of the system.
    def __str__(self) -> str:
        return f"LLM={self.llm.__module__}, Encoder={self.embed_model.model_name}"

    def docs_to_index(self, documents: List[Document]) -> Self:
        for index in self.indices:
            for document in documents:
                index.insert(document)
        return self

    def save_indices(self, save_dir: Union[Path, str], fs: Optional[AbstractFileSystem] = None) -> Self:
        for indexer in self.indices:
            indexer.storage_context.persist(persist_dir=save_dir, fs=fs)
        return self

    def chat(self):
        """Chat using chat engine"""
