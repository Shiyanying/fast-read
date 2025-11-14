from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def verify_token(token: str = Depends(oauth2_scheme)):
    """验证token，不再需要用户信息"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # 只要token有效即可，不需要用户信息
    return True

# 为了兼容现有代码，保留get_current_user但返回None
async def get_current_user(verified: bool = Depends(verify_token)):
    """获取当前用户（简化版，返回None）"""
    # 返回一个简单的对象，包含默认用户ID
    class SimpleUser:
        id = 1  # 使用固定的用户ID
    
    return SimpleUser()
