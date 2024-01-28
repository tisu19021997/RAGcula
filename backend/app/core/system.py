from abc import ABC, abstractmethod
from typing import Any

# A system:
# 1. ingestion and indexing pipeline
# 2. querying: retriever,


class BaseSystem(ABC):
    @abstractmethod
    def ingest(self, *args: Any, **kwargs: Any):
        """Ingest documents"""

    @abstractmethod
    def index(self, *args: Any, **kwargs: Any):
        """Index documents"""

    @abstractmethod
    def query(self, *args: Any, **kwargs: Any):
        """Query from documents"""

    @abstractmethod
    def chat(self, *args: Any, **kwargs: Any):
        """Chat with documents"""


class ResumeAISystem(BaseSystem):
    pass


my_system = ResumeAISystem()
