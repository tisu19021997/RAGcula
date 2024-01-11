from typing import List
from pydantic import BaseModel
from llama_index.llms.types import MessageRole


class Message(BaseModel):
    role: MessageRole
    content: str


class ChatData(BaseModel):
    messages: List[Message]
