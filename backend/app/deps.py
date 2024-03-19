from fastapi import Request
from rag.systems.base import BaseSystem


async def get_rag_system_from_state(request: Request) -> BaseSystem:
    return request.state.rag_system
