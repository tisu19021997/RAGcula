from typing import List
from pydantic import BaseModel
from llama_index.core.llms import MessageRole


class Message(BaseModel):
    role: MessageRole
    content: str


class ChatData(BaseModel):
    messages: List[Message]
