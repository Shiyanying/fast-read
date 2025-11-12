# ReadSmart 生产环境部署指南

## 目录
1. [服务器环境准备](#服务器环境准备)
2. [后端部署](#后端部署)
3. [前端部署](#前端部署)
4. [使用 Nginx 反向代理](#使用-nginx-反向代理)
5. [使用 Docker 部署（推荐）](#使用-docker-部署推荐)
6. [使用 Systemd 管理服务](#使用-systemd-管理服务)
7. [SSL/HTTPS 配置](#sslhttps-配置)

---

## 服务器环境准备

### 系统要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **Python**: 3.9+
- **Node.js**: 16+
- **PostgreSQL**: 12+
- **Nginx**: 1.18+ (可选，用于反向代理)

### 安装基础软件

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx git
```

**CentOS/RHEL:**
```bash
sudo yum install -y python3 python3-pip postgresql postgresql-server nodejs npm nginx git
```

---

## 后端部署

### 1. 上传代码到服务器

```bash
# 使用 Git
git clone <your-repository-url> /opt/readsmart
cd /opt/readsmart

# 或使用 SCP 上传
scp -r /path/to/fast-read user@your-server:/opt/readsmart
```

### 2. 设置后端环境

```bash
cd /opt/readsmart/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置文件
```

### 3. 配置 .env 文件

```env
# 数据库连接（生产环境）
DATABASE_URL=postgresql://readsmart_user:your_strong_password@localhost:5432/readsmart

# JWT 密钥（必须更改！）
SECRET_KEY=your-very-long-and-random-secret-key-here-change-this-in-production

# 其他配置
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置（生产环境域名）
CORS_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]

# 文件上传
UPLOAD_DIR=/opt/readsmart/backend/uploads
MAX_FILE_SIZE=10485760

# 词典 API
DICTIONARY_API_URL=https://api.dictionaryapi.dev/api/v2/entries/en
DICTIONARY_API_KEY=
```

### 4. 设置数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE readsmart;
CREATE USER readsmart_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE readsmart TO readsmart_user;

# 授予 Schema 权限
\c readsmart
GRANT ALL ON SCHEMA public TO readsmart_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO readsmart_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO readsmart_user;

\q
```

### 5. 运行数据库迁移

```bash
cd /opt/readsmart/backend
source venv/bin/activate
alembic upgrade head
```

### 6. 创建上传目录

```bash
mkdir -p /opt/readsmart/backend/uploads
chmod 755 /opt/readsmart/backend/uploads
```

### 7. 测试后端服务

```bash
cd /opt/readsmart/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 `http://your-server-ip:8000/health` 应该返回 `{"status":"healthy"}`

---

## 前端部署

### 1. 构建前端

```bash
cd /opt/readsmart/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

构建完成后，静态文件会在 `frontend/dist` 目录中。

### 2. 配置 API 地址

编辑 `frontend/src/api/index.js`，确保生产环境使用正确的 API 地址：

```javascript
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'https://your-domain.com/api/v1'  // 生产环境
    : '/api/v1',  // 开发环境
  headers: {
    'Content-Type': 'application/json'
  }
})
```

或者使用环境变量：

创建 `frontend/.env.production`:
```env
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

修改 `frontend/src/api/index.js`:
```javascript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  // ...
})
```

然后重新构建：
```bash
npm run build
```

---

## 使用 Nginx 反向代理

### 1. 安装 Nginx

```bash
sudo apt install nginx  # Ubuntu/Debian
# 或
sudo yum install nginx  # CentOS
```

### 2. 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/readsmart`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 前端静态文件
    location / {
        root /opt/readsmart/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 文件上传大小限制
    client_max_body_size 10M;

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        root /opt/readsmart/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. 启用配置

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/readsmart /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 使用 Docker 部署（推荐）

### 1. 创建后端 Dockerfile

创建 `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads && chmod 755 uploads

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 创建前端 Dockerfile

创建 `frontend/Dockerfile`:

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

创建 `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    client_max_body_size 10M;
}
```

### 3. 创建 docker-compose.yml

在项目根目录创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: readsmart-db
    environment:
      POSTGRES_DB: readsmart
      POSTGRES_USER: readsmart_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-change_this_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U readsmart_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: readsmart-backend
    environment:
      DATABASE_URL: postgresql://readsmart_user:${DB_PASSWORD:-change_this_password}@db:5432/readsmart
      SECRET_KEY: ${SECRET_KEY:-change_this_secret_key}
      CORS_ORIGINS: '["http://localhost","https://your-domain.com"]'
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/.env:/app/.env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000"

  frontend:
    build: ./frontend
    container_name: readsmart-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

### 4. 使用 Docker Compose 部署

```bash
# 创建 .env 文件（用于 Docker Compose）
cat > .env << EOF
DB_PASSWORD=your_strong_database_password
SECRET_KEY=your_very_long_random_secret_key
EOF

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据卷（谨慎使用！）
docker-compose down -v
```

---

## 使用 Systemd 管理服务

### 1. 创建后端服务文件

创建 `/etc/systemd/system/readsmart-backend.service`:

```ini
[Unit]
Description=ReadSmart Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/readsmart/backend
Environment="PATH=/opt/readsmart/backend/venv/bin"
ExecStart=/opt/readsmart/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. 启用并启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable readsmart-backend

# 启动服务
sudo systemctl start readsmart-backend

# 查看状态
sudo systemctl status readsmart-backend

# 查看日志
sudo journalctl -u readsmart-backend -f
```

---

## SSL/HTTPS 配置

### 使用 Let's Encrypt (免费 SSL 证书)

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu/Debian
# 或
sudo yum install certbot python3-certbot-nginx  # CentOS

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

Certbot 会自动修改 Nginx 配置，添加 SSL 支持。

### 手动配置 SSL

在 Nginx 配置中添加：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... 其他配置
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 部署检查清单

- [ ] 服务器已安装所有必需软件
- [ ] 数据库已创建并配置用户权限
- [ ] 后端 `.env` 文件已配置（特别是 `SECRET_KEY`）
- [ ] 数据库迁移已运行
- [ ] 上传目录已创建并有写权限
- [ ] 前端已构建并配置正确的 API 地址
- [ ] Nginx 配置已正确设置
- [ ] 防火墙已开放必要端口（80, 443, 8000）
- [ ] SSL 证书已配置（生产环境）
- [ ] 服务已设置为开机自启
- [ ] 已测试所有功能（注册、登录、上传、阅读）

---

## 性能优化建议

1. **使用 Gunicorn + Uvicorn Workers**（生产环境）:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **启用数据库连接池**: 已在 SQLAlchemy 中配置

3. **使用 Redis 缓存**: 缓存单词释义查询结果

4. **CDN 加速**: 将前端静态资源部署到 CDN

5. **文件存储**: 使用对象存储服务（AWS S3、阿里云 OSS）替代本地存储

---

## 备份策略

### 数据库备份

```bash
# 创建备份脚本
cat > /opt/readsmart/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/readsmart/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -U readsmart_user readsmart > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/readsmart/backend/uploads

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/readsmart/scripts/backup.sh

# 添加到 crontab（每天凌晨 2 点备份）
crontab -e
# 添加: 0 2 * * * /opt/readsmart/scripts/backup.sh
```

---

## 故障排查

### 后端无法启动
```bash
# 检查日志
sudo journalctl -u readsmart-backend -n 50

# 检查端口占用
sudo netstat -tlnp | grep 8000

# 检查数据库连接
psql -U readsmart_user -d readsmart -h localhost
```

### 前端无法访问
```bash
# 检查 Nginx 状态
sudo systemctl status nginx

# 检查 Nginx 日志
sudo tail -f /var/log/nginx/error.log

# 检查文件权限
ls -la /opt/readsmart/frontend/dist
```

### 数据库连接失败
```bash
# 检查 PostgreSQL 服务
sudo systemctl status postgresql

# 检查连接配置
cat /opt/readsmart/backend/.env | grep DATABASE_URL
```

---

## 安全建议

1. **更改默认密码**: 所有默认密码必须更改
2. **使用强 SECRET_KEY**: 至少 32 个随机字符
3. **限制数据库访问**: 只允许本地连接
4. **配置防火墙**: 只开放必要端口
5. **定期更新**: 保持系统和依赖包更新
6. **使用 HTTPS**: 生产环境必须使用 HTTPS
7. **文件权限**: 确保敏感文件权限正确（`.env` 应为 600）

