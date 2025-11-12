# ReadSmart 部署指南

## 环境准备

### 1. 后端环境

```bash
# 安装 Python 3.9+
python --version

# 创建虚拟环境
cd backend
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库设置

#### 安装 PostgreSQL

**Windows:**
- 下载并安装 PostgreSQL: https://www.postgresql.org/download/windows/
- 记住设置的 postgres 用户密码

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

#### 创建数据库

```bash
# 登录 PostgreSQL
psql -U postgres

# 创建数据库和用户
CREATE DATABASE readsmart;
CREATE USER readsmart_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE readsmart TO readsmart_user;
\q
```

### 3. 配置环境变量

在 `backend` 目录下创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置正确的数据库连接：

```env
DATABASE_URL=postgresql://readsmart_user:your_password@localhost/readsmart
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
DICTIONARY_API_URL=https://api.dictionaryapi.dev/api/v2/entries/en
```

### 4. 运行数据库迁移

```bash
cd backend
alembic upgrade head
```

### 5. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

后端服务将在 http://localhost:8000 启动

### 6. 前端环境

```bash
# 安装 Node.js 16+
node --version

# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 生产环境部署

### 使用 Docker (推荐)

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: readsmart
      POSTGRES_USER: readsmart_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://readsmart_user:your_password@db/readsmart
      SECRET_KEY: your-secret-key
    depends_on:
      - db
    volumes:
      - ./backend/uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 常见问题

### 1. 数据库连接失败

- 检查 PostgreSQL 服务是否运行
- 验证 `.env` 文件中的数据库连接字符串
- 确认数据库用户权限

### 2. 文件上传失败

- 确保 `uploads` 目录存在且有写权限
- 检查文件大小是否超过限制

### 3. CORS 错误

- 检查后端 `CORS_ORIGINS` 配置
- 确保前端 URL 在允许列表中

## 性能优化建议

1. **数据库索引**: 已为常用查询字段创建索引
2. **文件存储**: 生产环境建议使用对象存储（如 AWS S3, 阿里云 OSS）
3. **缓存**: 考虑使用 Redis 缓存单词释义
4. **CDN**: 前端静态资源使用 CDN 加速

