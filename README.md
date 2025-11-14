# ReadSmart - 个性化英语外刊阅读平台

## 项目简介

ReadSmart 是一个极简、高效、个性化的英语外刊阅读工具，通过技术手段降低阅读障碍，帮助用户科学地积累词汇。

### 核心价值

- **无缝阅读体验**：点击查词，无需打断阅读流
- **数据驱动学习**：自动生成基于真实阅读行为的生词本
- **个性化内容库**：上传自己感兴趣的外刊材料
- **简单安全**：密码保护，无需复杂注册流程

## 技术栈

### 前端
- **框架**：Vue.js 3 + Vite
- **UI组件库**：Element Plus
- **状态管理**：Pinia
- **路由**：Vue Router
- **HTTP客户端**：Axios

### 后端
- **框架**：FastAPI
- **数据库**：PostgreSQL
- **ORM**：SQLAlchemy
- **认证**：JWT
- **文件处理**：PyPDF2, ebooklib

## 快速开始（Docker 部署）

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+

### 一键部署

```bash
# 克隆项目（如果还没有）
git clone <repository-url>
cd fast-read

# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 访问应用

- **前端**：http://localhost
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

### 常用命令

```bash
# 停止服务
docker-compose down

# 停止并删除数据（谨慎！会删除数据库）
docker-compose down -v

# 重新构建
docker-compose up -d --build

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# 查看服务状态
docker-compose ps

# 重启服务
docker-compose restart backend
```

## 配置说明

### 修改配置

编辑 `docker-compose.yml` 文件：

1. **数据库密码**：修改 `POSTGRES_PASSWORD`（默认：readsmart123）
2. **访问密码**：修改 `ACCESS_PASSWORD`（**必须更改！**，默认：readsmart123）
3. **JWT 密钥**：修改 `SECRET_KEY`（**生产环境必须更改！**）
4. **CORS 配置**：修改 `CORS_ORIGINS` 为你的前端域名
5. **端口配置**：根据需要修改端口映射

修改后运行：
```bash
docker-compose up -d --build
```

### 环境变量

后端服务支持以下环境变量（在 `docker-compose.yml` 中配置）：

- `DATABASE_URL` - 数据库连接字符串（自动配置）
- `SECRET_KEY` - JWT 密钥（**必须更改**）
- `ACCESS_PASSWORD` - 访问密码（**必须更改**，默认：readsmart123）
- `CORS_ORIGINS` - 允许的跨域来源
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token 过期时间（默认：30分钟）

## 生产环境部署

### 重要安全配置

1. ✅ **更改访问密码**：修改 `ACCESS_PASSWORD`（**必须更改！**）
2. ✅ **更改数据库密码**：修改 `POSTGRES_PASSWORD` 和 `SECRET_KEY`
3. ✅ **配置域名**：修改 `CORS_ORIGINS` 为你的实际域名
4. ✅ **配置 HTTPS**：使用 Nginx 反向代理 + SSL 证书
5. ✅ **定期备份**：备份数据库卷 `postgres_data`

### 数据持久化

数据库数据存储在 Docker 卷 `postgres_data` 中，即使删除容器也不会丢失数据。

备份数据库：
```bash
docker-compose exec db pg_dump -U readsmart_user readsmart > backup.sql
```

恢复数据库：
```bash
docker-compose exec -T db psql -U readsmart_user readsmart < backup.sql
```

## 故障排查

```bash
# 查看所有容器状态
docker-compose ps

# 查看错误日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 进入容器调试
docker-compose exec backend bash
docker-compose exec db psql -U readsmart_user -d readsmart

# 重启单个服务
docker-compose restart backend
```

## 项目结构

```
fast-read/
├── backend/              # 后端服务
│   ├── app/             # 应用代码
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic模型
│   │   └── services/    # 业务逻辑
│   ├── alembic/         # 数据库迁移
│   ├── Dockerfile       # 后端镜像构建
│   └── requirements.txt # Python依赖
├── frontend/            # 前端应用
│   ├── src/            # 源代码
│   ├── Dockerfile      # 前端镜像构建
│   ├── nginx.conf      # Nginx配置
│   └── package.json    # Node依赖
├── docker-compose.yml  # Docker Compose配置
└── README.md           # 项目说明
```

## 功能模块

### 已实现
- [x] 用户注册/登录
- [x] 文档上传（纯文本）
- [x] 阅读器界面
- [x] 点击查词
- [x] 生词本基础功能
- [x] 移动端适配

### 计划中
- [ ] PDF/EPUB解析
- [ ] 生词本反链接功能
- [ ] 单词测验
- [ ] 导出生词

## 许可证

MIT License
