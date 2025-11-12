# ReadSmart 测试指南

## 快速测试步骤

由于路径中包含中文字符可能导致 PowerShell 命令执行问题，请按照以下步骤手动测试：

### 步骤 1: 检查环境

打开 PowerShell 或 CMD，检查环境：

```powershell
python --version  # 应该显示 Python 3.9+
node --version     # 应该显示 v16+
```

### 步骤 2: 设置后端

1. **打开新的 PowerShell 窗口**，导航到项目目录：
   ```powershell
   cd "D:\Mizuka备份\设想\backend"
   ```

2. **创建虚拟环境**（如果还没有）：
   ```powershell
   python -m venv venv
   ```

3. **激活虚拟环境**：
   ```powershell
   .\venv\Scripts\activate
   ```

4. **安装依赖**：
   ```powershell
   pip install -r requirements.txt
   ```

5. **创建 .env 文件**：
   - 复制 `.env.example` 为 `.env`
   - 编辑 `.env` 文件，设置数据库连接：
     ```
     DATABASE_URL=postgresql://postgres:your_password@localhost/readsmart
     ```
   - 注意：将 `your_password` 替换为你的 PostgreSQL 密码

6. **创建数据库**（如果还没有）：
   ```powershell
   # 登录 PostgreSQL
   psql -U postgres
   
   # 在 psql 中执行：
   CREATE DATABASE readsmart;
   \q
   ```

7. **运行数据库迁移**：
   ```powershell
   alembic upgrade head
   ```

8. **创建上传目录**：
   ```powershell
   mkdir uploads
   ```

9. **启动后端服务**：
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```

   后端应该运行在 http://localhost:8000

### 步骤 3: 设置前端

1. **打开另一个 PowerShell 窗口**，导航到前端目录：
   ```powershell
   cd "D:\Mizuka备份\设想\frontend"
   ```

2. **安装依赖**：
   ```powershell
   npm install
   ```

3. **启动开发服务器**：
   ```powershell
   npm run dev
   ```

   前端应该运行在 http://localhost:5173

### 步骤 4: 测试功能

1. **访问应用**：
   - 打开浏览器访问 http://localhost:5173

2. **注册账号**：
   - 点击"立即注册"
   - 填写用户名、邮箱、密码
   - 提交注册

3. **登录**：
   - 使用刚注册的账号登录

4. **上传文档**：
   - 创建一个测试用的 .txt 文件（英文内容）
   - 在仪表盘中拖拽或点击上传
   - 等待上传完成

5. **测试阅读器**：
   - 点击文档卡片进入阅读器
   - 点击文档中的单词，查看是否弹出释义
   - 测试翻页功能

6. **测试生词本**：
   - 点击右上角用户头像
   - 选择"我的生词本"
   - 查看已点击的单词列表
   - 点击单词查看详情和上下文

### 步骤 5: 检查 API 文档

访问 http://localhost:8000/docs 查看 Swagger API 文档，可以在这里测试所有 API 端点。

## 常见问题排查

### 问题 1: 数据库连接失败

**错误信息**：`sqlalchemy.exc.OperationalError`

**解决方案**：
1. 确认 PostgreSQL 服务正在运行
2. 检查 `.env` 文件中的 `DATABASE_URL` 是否正确
3. 确认数据库 `readsmart` 已创建
4. 确认用户名和密码正确

### 问题 2: 前端无法连接后端

**错误信息**：`Network Error` 或 `CORS error`

**解决方案**：
1. 确认后端服务运行在 http://localhost:8000
2. 检查浏览器控制台的错误信息
3. 确认 `vite.config.js` 中的代理配置正确

### 问题 3: 上传文件失败

**错误信息**：`413 Request Entity Too Large` 或文件上传失败

**解决方案**：
1. 确认文件大小不超过 10MB
2. 确认 `backend/uploads` 目录存在且有写权限
3. 检查后端日志查看详细错误

### 问题 4: 单词查询无结果

**错误信息**：单词释义为空或 API 调用失败

**解决方案**：
1. 检查网络连接
2. 查看浏览器控制台和后端日志
3. 词典 API 可能偶尔不稳定，这是正常的

## 测试检查清单

- [ ] 后端服务成功启动（http://localhost:8000）
- [ ] 前端服务成功启动（http://localhost:5173）
- [ ] 可以访问登录页面
- [ ] 可以成功注册账号
- [ ] 可以成功登录
- [ ] 可以上传 .txt 文件
- [ ] 可以进入阅读器查看文档
- [ ] 可以点击单词查看释义
- [ ] 可以翻页浏览文档
- [ ] 可以在生词本中看到点击过的单词
- [ ] 可以查看单词的上下文
- [ ] 可以更新单词的掌握状态

## 下一步

完成基本测试后，可以：
1. 测试 PDF/EPUB 文件上传（需要确保相关库已安装）
2. 测试更多功能边界情况
3. 查看性能表现
4. 准备部署到生产环境

