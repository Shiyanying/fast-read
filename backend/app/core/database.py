from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import urllib.parse

# 确保数据库 URL 使用正确的编码
def get_database_url():
    """获取正确编码的数据库 URL"""
    url = settings.DATABASE_URL
    try:
        # 确保 URL 是字符串类型
        if isinstance(url, bytes):
            url = url.decode('utf-8', errors='replace')
        
        # 解析 URL
        parsed = urllib.parse.urlparse(url)
        
        # 如果密码包含特殊字符，进行 URL 编码
        username = parsed.username or ''
        password = parsed.password or ''
        
        # 对密码进行 URL 编码（如果包含特殊字符）
        if password:
            # 先解码（如果已经编码），然后重新编码
            try:
                decoded_password = urllib.parse.unquote(password)
                # 如果解码后的密码包含非 ASCII 字符，进行编码
                if any(ord(c) > 127 for c in decoded_password):
                    password = urllib.parse.quote(decoded_password, safe='')
            except Exception:
                # 如果解码失败，直接编码
                password = urllib.parse.quote(password, safe='')
        
        # 重新构建 URL
        if username and password:
            netloc = f"{username}:{password}@{parsed.hostname or ''}"
        elif username:
            netloc = f"{username}@{parsed.hostname or ''}"
        else:
            netloc = parsed.hostname or ''
            
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
    except Exception as e:
        # 如果处理失败，返回原 URL（确保是字符串）
        print(f"警告: 数据库 URL 处理失败: {e}")
        return url if isinstance(url, str) else url.decode('utf-8', errors='replace')

engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,  # 连接前检查连接是否有效
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """数据库依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

