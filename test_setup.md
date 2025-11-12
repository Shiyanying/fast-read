# ReadSmart 测试设置指南

由于项目路径包含中文字符，PowerShell 可能无法正确识别路径。请按照以下步骤手动设置和测试：

## 准备工作

### 1. 检查环境

在 PowerShell 中运行：

```powershell
python --version  # 需要 Python 3.9+
node --version    # 需要 Node.js 16+
```

### 2. 检查 PostgreSQL

确保 PostgreSQL 已安装并运行：

```powershell
# 检查 PostgreSQL 服务状态
Get-Service postgresql*

# 如果未运行，启动服务
Start-Service postgresql-x64-13  # 版本号可能不同
```

## 后端设置步骤

### 步骤 1: 打开后端目录

在 PowerShell 中：

```powershell
# 方法1: 使用引号包裹路径
cd "D:\Mizuka备份\设想\backend"

# 方法2: 如果方法1不行，使用短路径名
# 先获取短路径名
cmd /c for %I in ("D:\Mizuka备份\设想\backend") do @echo %~sI
# 然后使用返回的短路径
```

### 步骤 2: 创建虚拟环境

```powershell
python -m venv venv
```

### 步骤 3: 激活虚拟环境

```powershell
.\venv\Scripts\activate
```

激活成功后，命令提示符前会显示 `(venv)`。

### 步骤 4: 安装依赖

```powershell
pip install -r requirements.txt
```

### 步骤 5: 配置环境变量

1. 复制 `.env.example` 为 `.env`：
   ```powershell
   Copy-Item .env.example .env
   ```

2. 编辑 `.env` 文件，设置数据库连接：
   ```
   DATABASE_URL=postgresql://postgres:你的密码@localhost/readsmart
   SECRET_KEY=your-secret-key-change-in-production
   ```

### 步骤 6: 创建数据库

```powershell
# 登录 PostgreSQL
psql -U postgres

# 在 psql 中执行：
CREATE DATABASE readsmart;
\q
```

### 步骤 7: 运行数据库迁移

```powershell
alembic upgrade head
```

### 步骤 8: 创建上传目录

```powershell
New-Item -ItemType Directory -Force -Path uploads
```

### 步骤 9: 启动后端

```powershell
uvicorn app.main:app --reload --port 8000
```

看到类似以下输出表示启动成功：
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 前端设置步骤

### 打开新的 PowerShell 窗口

### 步骤 1: 进入前端目录

```powershell
cd "D:\Mizuka备份\设想\frontend"
```

### 步骤 2: 安装依赖

```powershell
npm install
```

### 步骤 3: 启动开发服务器

```powershell
npm run dev
```

看到类似以下输出表示启动成功：
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 测试流程

### 1. 访问应用

打开浏览器访问：http://localhost:5173

### 2. 注册账号

- 点击"立即注册"
- 填写信息：
  - 用户名：testuser
  - 邮箱：test@example.com
  - 密码：test123456
- 点击注册

### 3. 登录

- 使用刚注册的账号登录

### 4. 上传测试文档

创建一个测试文件 `test.txt`，内容如下：

```
This is a test document for ReadSmart.
The quick brown fox jumps over the lazy dog.
Learning English is fun and rewarding.
Technology helps us learn more efficiently.
```

在仪表盘中上传这个文件。

### 5. 测试阅读器

- 点击文档卡片进入阅读器
- 点击单词 "test"、"document"、"learning" 等
- 查看是否弹出释义侧边栏
- 测试翻页功能

### 6. 测试生词本

- 点击右上角用户头像
- 选择"我的生词本"
- 查看已点击的单词
- 点击单词查看详情和上下文
- 尝试更改单词的掌握状态

## 验证 API

访问 http://localhost:8000/docs 查看 Swagger API 文档，可以在这里直接测试 API。

## 常见问题

### 问题：无法进入目录

**解决方案**：
1. 使用文件资源管理器导航到目录
2. 在目录中右键选择"在此处打开 PowerShell"
3. 或者使用短路径名

### 问题：数据库连接失败

**解决方案**：
1. 确认 PostgreSQL 服务正在运行
2. 检查 `.env` 文件中的数据库连接字符串
3. 确认数据库 `readsmart` 已创建
4. 测试连接：
   ```powershell
   psql -U postgres -d readsmart
   ```

### 问题：端口被占用

**解决方案**：
1. 后端端口 8000 被占用：
   ```powershell
   # 查找占用端口的进程
   netstat -ano | findstr :8000
   # 结束进程（替换 PID）
   taskkill /PID <PID> /F
   ```

2. 前端端口 5173 被占用：
   - 修改 `vite.config.js` 中的端口号

## 成功标志

如果一切正常，你应该能够：
- ✅ 访问 http://localhost:5173 看到登录页面
- ✅ 成功注册和登录
- ✅ 上传文档并看到文档列表
- ✅ 进入阅读器并点击单词查看释义
- ✅ 在生词本中看到点击过的单词
- ✅ 查看单词的上下文信息

## 下一步

完成基本测试后，可以：
1. 测试更多功能
2. 查看代码结构
3. 准备部署

