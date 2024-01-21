from fastapi import APIRouter

from app.api.endpoints import chat

api_router = APIRouter()

api_router.include_router(chat.chat_router, prefix="/chat")
# api_router.include_router(users.user_router, prefix="/users")
