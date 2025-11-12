# ReadSmart Docker 部署指南

## 一键部署

所有 Docker 文件已创建，直接运行即可！

### 部署命令

```bash
# 进入项目目录
cd D:\fast-read

# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 访问应用

- **前端**：http://localhost
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

---

## 常用命令

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

# 查看服务状态
docker-compose ps

# 重启服务
docker-compose restart backend
```

---

## 修改配置

编辑 `docker-compose.yml`：

1. **修改数据库密码**：`POSTGRES_PASSWORD`
2. **修改 JWT 密钥**：`SECRET_KEY`（**生产环境必须更改！**）
3. **修改端口**：修改 `ports` 配置

修改后运行：
```bash
docker-compose up -d --build
```

---

## 生产环境注意事项

1. ✅ **更改默认密码**：修改 `POSTGRES_PASSWORD` 和 `SECRET_KEY`
2. ✅ **配置域名**：修改 `CORS_ORIGINS` 为你的域名
3. ✅ **配置 HTTPS**：使用 Nginx 反向代理 + SSL 证书
4. ✅ **定期备份**：备份数据库卷 `postgres_data`

---

## 故障排查

```bash
# 查看所有容器状态
docker-compose ps

# 查看错误日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 重启单个服务
docker-compose restart backend
```

---

## 文件说明

已创建的文件：
- `docker-compose.yml` - Docker Compose 配置
- `backend/Dockerfile` - 后端镜像构建文件
- `frontend/Dockerfile` - 前端镜像构建文件
- `frontend/nginx.conf` - Nginx 配置

完成！访问 http://localhost 即可使用。
