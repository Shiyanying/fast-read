# ReadSmart 快速开始指南

## 5分钟快速启动

### 前置要求
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

### 步骤 1: 克隆/下载项目

```bash
# 如果使用 Git
git clone <repository-url>
cd readsmart
```

### 步骤 2: 设置数据库

```bash
# 登录 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE readsmart;
\q
```

### 步骤 3: 配置后端

```bash
cd backend

# Windows 用户
start.bat

# Linux/Mac 用户
chmod +x start.sh
./start.sh
```

或者手动执行：

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# 复制并编辑 .env 文件
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# 编辑 .env，设置数据库连接
# DATABASE_URL=postgresql://user:password@localhost/readsmart

# 运行迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 步骤 4: 启动前端

打开新的终端窗口：

```bash
cd frontend

# Windows 用户
start.bat

# 或手动执行
npm install
npm run dev
```

### 步骤 5: 访问应用

打开浏览器访问：http://localhost:5173

## 首次使用

1. **注册账号**
   - 访问登录页面
   - 点击"立即注册"
   - 填写用户名、邮箱、密码

2. **上传文档**
   - 登录后进入仪表盘
   - 拖拽或点击上传 .txt 文件（MVP 阶段）
   - 等待文档解析完成

3. **开始阅读**
   - 点击文档卡片进入阅读器
   - 点击任意单词查看释义
   - 使用翻页按钮浏览文档

4. **查看生词本**
   - 点击右上角用户头像
   - 选择"我的生词本"
   - 查看所有点击过的单词
   - 点击单词查看出现上下文

## 测试账号

首次使用需要注册，系统暂不提供测试账号。

## 常见问题

### Q: 后端启动失败，提示数据库连接错误
A: 检查 `.env` 文件中的 `DATABASE_URL` 是否正确，确保 PostgreSQL 服务正在运行。

### Q: 前端无法连接到后端
A: 确保后端服务运行在 http://localhost:8000，检查 `vite.config.js` 中的代理配置。

### Q: 上传文件失败
A: 确保 `backend/uploads` 目录存在且有写权限。

### Q: 单词查询无结果
A: 系统使用免费的词典 API，可能偶尔不稳定。可以查看浏览器控制台错误信息。

## 下一步

- 阅读 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) 了解项目结构
- 阅读 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解生产环境部署
- 查看 [README.md](./README.md) 了解完整功能

## 开发建议

1. **使用虚拟环境**：避免依赖冲突
2. **定期备份数据库**：开发过程中数据可能丢失
3. **查看日志**：后端日志在终端，前端日志在浏览器控制台
4. **API 文档**：访问 http://localhost:8000/docs 查看 Swagger 文档

