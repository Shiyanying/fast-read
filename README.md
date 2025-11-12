# ReadSmart - 个性化英语外刊阅读平台

## 项目简介

ReadSmart 是一个极简、高效、个性化的英语外刊阅读工具，通过技术手段降低阅读障碍，帮助用户科学地积累词汇。

### 核心价值

- **无缝阅读体验**：点击查词，无需打断阅读流
- **数据驱动学习**：自动生成基于真实阅读行为的生词本
- **个性化内容库**：完全由用户主导，上传自己感兴趣的外刊材料
- **多用户支持**：为小组学习或商业化提供基础

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

## 项目结构

```
readsmart/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic模型
│   │   └── services/    # 业务逻辑
│   ├── requirements.txt
│   └── main.py
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── views/       # 页面
│   │   ├── router/     # 路由
│   │   ├── stores/      # 状态管理
│   │   └── api/         # API调用
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

### 后端设置

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置数据库连接
# 1. 在 backend 目录下创建 .env 文件
# 2. 编辑 .env 文件，设置数据库连接字符串：
#
# DATABASE_URL 格式：postgresql://用户名:密码@主机:端口/数据库名
#
# 示例配置：
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/readsmart
#
# 各部分说明：
# - postgresql://     - 数据库类型（PostgreSQL）
# - postgres          - 数据库用户名（默认 postgres，或你创建的用户名）
# - your_password     - 数据库密码（替换为你的实际密码）
# - localhost         - 数据库主机地址（本地为 localhost，远程需填写 IP）
# - 5432              - 数据库端口（PostgreSQL 默认 5432，可省略）
# - readsmart         - 数据库名称（需要先创建此数据库）
#
# 创建数据库步骤：
# 1. 登录 PostgreSQL：psql -U postgres
# 2. 创建数据库：CREATE DATABASE readsmart;
# 3. （可选）创建专用用户：
#    CREATE USER readsmart_user WITH PASSWORD 'your_password';
#    GRANT ALL PRIVILEGES ON DATABASE readsmart TO readsmart_user;
# 4. 退出：\q

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 前端设置

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 功能模块

### 第一阶段（MVP）
- [x] 用户注册/登录
- [x] 文档上传（纯文本）
- [x] 阅读器界面
- [x] 点击查词
- [x] 生词本基础功能

### 第二阶段
- [ ] 多用户系统完善
- [ ] PDF/EPUB解析
- [ ] 生词本反链接功能
- [ ] UI优化

### 第三阶段
- [ ] 移动端适配
- [ ] 单词测验
- [ ] 导出生词
- [ ] 性能优化

## 开发路线图

详见项目文档中的实施路线图部分。

## 许可证

MIT License

