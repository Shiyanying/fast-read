from fastapi import APIRouter
from app.api.v1.endpoints import auth, documents, words

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(documents.router, prefix="/documents", tags=["文档"])
api_router.include_router(words.router, prefix="/words", tags=["单词"])

