from fastapi import APIRouter

from app.upload.router import upload_router
from app.chat.router import chat_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat")
api_router.include_router(upload_router, prefix="/upload")
