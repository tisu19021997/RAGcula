from pathlib import Path
from typing import Dict, List, Optional, Self, Sequence, Union

from app.upload.crud import get_all_documents
from app.upload.models import Document as Upload
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    load_indices_from_storage,
    set_global_service_context,
)
from llama_index.core.agent import ReActAgent
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.data_structs.data_structs import IndexStruct
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.indices import SummaryIndex, VectorStoreIndex
from llama_index.core.indices.base import BaseIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.llms import LLM
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import TransformComponent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from llama_index.readers.file import PyMuPDFReader
from llama_index.vector_stores.postgres import PGVectorStore
from rag.default import Default
from rag.prompt import SIMPLE_CHAT_SYSTEM_PROMPT
from rag.systems.base import BaseSystem, DocumentIndices
from rag.transform.cleaner import UnstructuredIOCleaner
from rag.utils import (
    custom_react_chat_formatter,
    get_tool_description_from_upload,
    index_to_query_engine_tool_mapping,
)


class ReactSystem(BaseSystem):
    indices: Dict[str, DocumentIndices]

    def __init__(
        self,
        data_loader: BaseReader,
        llm: LLM,
        embed_model: BaseEmbedding,
        transformations: List[TransformComponent],
        vector_store: PGVectorStore,
        storage_context: StorageContext,
    ) -> None:
        self.indices = {}
        super().__init__(
            data_loader=data_loader,
            llm=llm,
            embed_model=embed_model,
            transformations=transformations,
            vector_store=vector_store,
            storage_context=storage_context,
        )

    @classmethod
    def from_vector_store(
        cls,
        vector_store: PGVectorStore,
        data_loader: Optional[BaseReader] = None,
        llm: Optional[LLM] = None,
        embed_model: Optional[BaseEmbedding] = None,
        transformations: Optional[List[TransformComponent]] = None,
        storage_context: Optional[StorageContext] = None,
    ) -> "ReactSystem":
        data_loader = data_loader or PyMuPDFReader()
        llm = llm or Default.llm()
        embed_model = embed_model or Default.embedding_model()
        transformations = transformations or [
            TokenTextSplitter(
                separator=" ",
                chunk_size=embed_model.max_length,
                chunk_overlap=24,
                tokenizer=embed_model._tokenizer,
            ),
            UnstructuredIOCleaner(),
            embed_model,
        ]
        storage_context = storage_context or StorageContext.from_defaults(
            vector_store=vector_store
        )
        return cls(
            data_loader=data_loader,
            llm=llm,
            embed_model=embed_model,
            transformations=transformations,
            vector_store=vector_store,
            storage_context=storage_context,
        )

    def load_data(
        self, file_path: Union[Path, str], upload_id: str
    ) -> Sequence[Document]:
        documents = self.data_loader.load_data(file_path, metadata=True)
        for document in documents:
            document.metadata["doc_uuid"] = upload_id
            document.excluded_llm_metadata_keys = ["doc_uuid"]
            document.excluded_embed_metadata_keys = ["doc_uuid"]
        return documents

    def build_indices(
        self,
        documents: Sequence[Document],
        upload_id: str,
    ) -> Self:
        self.ingestion_pipeline = IngestionPipeline(
            transformations=Settings.transformations,
            vector_store=self.vector_store,
            docstore=self.storage_context.docstore,
        )
        nodes = self.ingestion_pipeline.run(documents=documents, num_workers=2)

        # Build indices.
        indices: List[BaseIndex[IndexStruct]] = [
            VectorStoreIndex(nodes=nodes, storage_context=self.storage_context),
            SummaryIndex(nodes=nodes, storage_context=self.storage_context),
        ]
        for index in indices:
            index.set_index_id(f"{index.index_struct.get_type().value}.{upload_id}")
        self.indices[upload_id] = DocumentIndices(indices=indices)

        return Self

    def save_upload_index(self, upload_id: str, persist_dir: Union[Path, str]):
        for index in self.indices[upload_id].indices:
            index.storage_context.persist(persist_dir=persist_dir)
            print(f"Persisting {index.index_id} to {persist_dir}")

    # deprecated.
    def add_indices(
        self, indices: List[BaseIndex[IndexStruct]], namespace: str, upload_id: str
    ) -> Self:
        if not self.indices:
            self.indices = {}
        # Set unique id for each index.
        for index in indices:
            index.set_index_id(
                f"{namespace}.{index.index_struct.get_type().value}.{upload_id}"
            )
        self.indices[upload_id] = DocumentIndices(indices=indices)
        return self

    def load_indices(self, uploads: Sequence[Upload]) -> Self:
        """Load indices for the given uploads."""
        # Load indices from storage.
        self.indices = {}
        for upload in uploads:
            # Load non-vector-store indices.
            indices = load_indices_from_storage(
                storage_context=self.storage_context,
                index_ids=upload.llama_index_metadata["index_ids"],
            )
            # Vector store index.
            vector_index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store
            )
            indices.append(vector_index)
            self.indices[str(upload.id)] = DocumentIndices(indices=indices)

        return self

    def delete_upload_index(
        self,
        upload_id: str,
        llamaindex_ref_doc_ids: Sequence[str],
    ) -> Self:
        # Delete an index from storage.
        for key, indices in self.indices.items():
            if key != upload_id:
                continue

            for ref_doc_id in llamaindex_ref_doc_ids:
                for index in indices.indices:
                    ref_doc_info = index.docstore.get_ref_doc_info(ref_doc_id)
                    node_ids = ref_doc_info.node_ids
                    for node_id in node_ids:
                        index.docstore.delete_document(node_id, raise_error=True)

                    index.delete_ref_doc(
                        ref_doc_id=ref_doc_id, delete_from_docstore=True
                    )
                    print(
                        f"Deleteing {ref_doc_id} from {index.index_struct.get_type()}"
                    )
        del self.indices[upload_id]

        return self

    def build_engine(self, uploads: Sequence[Upload]) -> Self:
        if len(self.indices) == 0:
            print("No index found. Use simple chat interface.")
            self.engine = SimpleChatEngine.from_defaults(
                memory=ChatMemoryBuffer.from_defaults(),
                system_prompt=SIMPLE_CHAT_SYSTEM_PROMPT,
            )
            return self

        # Create an document-level agent for each upload.
        upload_agents = {}
        for upload_id, indices in self.indices.items():
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="doc_uuid", operator=FilterOperator.EQ, value=upload_id
                    )
                ]
            )
            query_engine_tools = [
                # Filter the vector index search space to only the current upload.
                index_to_query_engine_tool_mapping(
                    indices.vector, tool_name=f"vector_store_index", filters=filters
                ),
                index_to_query_engine_tool_mapping(
                    indices.summary, tool_name=f"summary_index"
                ),
            ]
            upload_agents[upload_id] = RouterQueryEngine.from_defaults(
                query_engine_tools=query_engine_tools, select_multi=False
            )
        # Create thread-level tools, each tool is a document.
        tools = [
            QueryEngineTool(
                query_engine=upload_agents[str(upload.id)],
                metadata=ToolMetadata(
                    description=get_tool_description_from_upload(upload),
                    name=f"document_{idx}",
                ),
            )
            for idx, upload in enumerate(uploads)
        ]
        self.engine = ReActAgent.from_tools(
            tools=tools,
            react_chat_formatter=custom_react_chat_formatter(uploads),
            memory=ChatMemoryBuffer.from_defaults(token_limit=1000),
            max_iterations=10,
            verbose=True,
        )

        return self
