from enum import Enum
from pathlib import Path
from typing import List, Optional, Sequence, Union, Self
from fsspec import AbstractFileSystem
from llama_index import StorageContext, ServiceContext, load_indices_from_storage, set_global_service_context
from llama_index.readers.base import BaseReader
from llama_index.llms.llm import LLM
from llama_index.embeddings.base import BaseEmbedding
from llama_index.schema import TransformComponent
from llama_index.llms.types import ChatMessage
from llama_index.retrievers import RouterRetriever
from llama_index.tools import RetrieverTool
from llama_index.selectors.llm_selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.chat_engine import ContextChatEngine
from llama_index.memory import ChatMemoryBuffer
from llama_index.indices.base import BaseIndex
from llama_index.data_structs.data_structs import IndexStruct
from llama_index.schema import Document
from llama_index.tools.types import AsyncBaseTool
from llama_index.chat_engine.types import AgentChatResponse, StreamingAgentChatResponse
from llama_index.text_splitter import TokenTextSplitter

from rag.systems.base import BaseSystem
from rag.prompt import LLM_SYSTEM_MESSAGE


class RouterMode(Enum):
    SINGLE = "single"
    MULTI = "multi"

    def __init__(self, mode: str):
        self.mode = mode

    @property
    def selector(self) -> Union[LLMMultiSelector, LLMSingleSelector]:
        if self.mode == "single":
            return LLMSingleSelector
        elif self.mode == "multi":
            return LLMMultiSelector
        raise ValueError(
            f"mode must be either single or multi, found {self.mode}")


class RouterSystem(BaseSystem):
    retriever_tools: List[AsyncBaseTool] = None

    def __init__(
        self,
        data_loader: BaseReader,
        llm: LLM,
        embed_model: BaseEmbedding,
        transformations: Optional[List[TransformComponent]] = None,
    ) -> None:
        transformations = transformations or [
            TokenTextSplitter(
                separator=" ",
                chunk_size=embed_model.max_length,
                chunk_overlap=24,
                tokenizer=embed_model._tokenizer
            )
        ]
        super().__init__(
            data_loader=data_loader,
            llm=llm,
            embed_model=embed_model,
            transformations=transformations,
        )
        self.service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model=self.embed_model,
            chunk_size=embed_model.max_length,
        )
        set_global_service_context(self.service_context)

    @classmethod
    def from_defaults(
        cls,

    ):
        pass

    def load_data(
            self,
            file_path: Union[Path, str],
            include_metadata: bool = True,
            fs: Optional[AbstractFileSystem] = None
    ) -> List[Document]:
        """_summary_

        Args:
            file_path (Union[Path, str]): _description_
            document_id (str): Document ID for PostgreSQL.
            include_metadata (bool, optional): _description_. Defaults to True.
            fs (Optional[AbstractFileSystem], optional): _description_. Defaults to None.

        Returns:
            List[Document]: _description_
        """
        self.documents = self.data_loader.load_data(
            file_path, metadata=include_metadata, fs=fs)
        return self.documents

    def delete_indices(self, storage_context: StorageContext, doc_ids: Sequence[str]) -> Self:
        self.load_indices(storage_context)
        for index in self.indices:
            for doc_id in doc_ids:
                index.delete_ref_doc(
                    ref_doc_id=doc_id, delete_from_docstore=True)
                print(
                    f'Deleteing {doc_id} from {index.index_struct.get_type()}')
        return self

    def build_retrievers(
            self,
            mode: RouterMode = RouterMode.SINGLE,
            selector_template_str: Optional[str] = None,
            system_prompt: Optional[str] = None
    ) -> Self:
        # TODO: how to set description for RetrieverTool?
        self.retreiver_tools = [
            RetrieverTool.from_defaults(
                retriever=indice.as_retriever(),
                # description=indice.description
            )
            for indice in self.indices
        ]
        selector = RouterMode(mode).selector.from_defaults(
            prompt_template_str=selector_template_str)
        self.context_retriever = RouterRetriever(
            selector=selector,
            retriever_tools=self.retreiver_tools,
            service_context=self.service_context
        )
        self.engine = ContextChatEngine.from_defaults(
            retriever=self.context_retriever,
            service_context=self.service_context,
            memory=ChatMemoryBuffer.from_defaults(llm=self.llm),
            system_prompt=system_prompt or LLM_SYSTEM_MESSAGE
        )
        return self

    def chat(self, message: str, chat_history: List[ChatMessage] | None = None) -> Union[AgentChatResponse, StreamingAgentChatResponse]:
        return self.engine.chat(message, chat_history)

    def stream_chat(self, message: str, chat_history: List[ChatMessage] | None = None) -> StreamingAgentChatResponse:
        return self.engine.stream_chat(message, chat_history)
