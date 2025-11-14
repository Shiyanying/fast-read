from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from pydantic import BaseModel

router = APIRouter()

class PasswordLogin(BaseModel):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=Token)
async def login(password_data: PasswordLogin):
    """密码验证登录"""
    # 简单的密码验证
    if password_data.password != settings.ACCESS_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌（使用固定标识）
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": "user"},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
