from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import List
import urllib.parse

class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "postgresql://user:password@localhost/readsmart"
    
    # 访问密码（简单密码验证）
    ACCESS_PASSWORD: str = "readsmart123"
    
    # JWT（用于token生成）
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # 词典API
    DICTIONARY_API_URL: str = "https://api.dictionaryapi.dev/api/v2/entries/en"
    DICTIONARY_API_KEY: str = ""
    
    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def validate_database_url(cls, v):
        """确保数据库 URL 使用正确的编码"""
        if isinstance(v, str):
            # 如果 URL 中包含非 ASCII 字符，进行 URL 编码
            try:
                # 尝试解析 URL
                parsed = urllib.parse.urlparse(v)
                # 如果密码包含特殊字符，进行编码
                if parsed.password:
                    # 重新构建 URL，确保密码部分正确编码
                    encoded_password = urllib.parse.quote(parsed.password, safe='')
                    netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"
                    if parsed.port:
                        netloc += f":{parsed.port}"
                    return urllib.parse.urlunparse((
                        parsed.scheme,
                        netloc,
                        parsed.path,
                        parsed.params,
                        parsed.query,
                        parsed.fragment
                    ))
            except Exception:
                # 如果解析失败，返回原值
                pass
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # 明确指定 UTF-8 编码
        case_sensitive=True,
        extra="ignore"  # 忽略 .env 文件中的额外字段
    )

settings = Settings()

