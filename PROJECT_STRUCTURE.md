# ReadSmart 项目结构说明

## 目录结构

```
readsmart/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   └── v1/
│   │   │       ├── endpoints/ # API 端点
│   │   │       │   ├── auth.py      # 认证相关
│   │   │       │   ├── documents.py # 文档管理
│   │   │       │   └── words.py     # 单词查询
│   │   │       ├── dependencies.py  # 依赖注入
│   │   │       └── __init__.py
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── security.py    # 安全相关（JWT、密码加密）
│   │   ├── models/            # 数据库模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── document.py    # 文档模型
│   │   │   └── word.py        # 单词点击记录模型
│   │   ├── schemas/           # Pydantic 模型（数据验证）
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   └── word.py
│   │   ├── services/          # 业务逻辑服务
│   │   │   ├── dictionary.py  # 词典 API 调用
│   │   │   └── document_parser.py # 文档解析
│   │   └── main.py            # FastAPI 应用入口
│   ├── alembic/               # 数据库迁移
│   │   ├── versions/          # 迁移版本
│   │   └── env.py
│   ├── uploads/               # 上传文件存储目录
│   ├── requirements.txt       # Python 依赖
│   ├── .env.example           # 环境变量示例
│   └── start.bat / start.sh   # 启动脚本
│
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── api/               # API 调用封装
│   │   │   └── index.js
│   │   ├── components/        # 可复用组件（如有）
│   │   ├── layouts/           # 布局组件
│   │   │   └── MainLayout.vue # 主布局
│   │   ├── router/            # 路由配置
│   │   │   └── index.js
│   │   ├── stores/            # Pinia 状态管理
│   │   │   └── auth.js        # 认证状态
│   │   ├── views/             # 页面组件
│   │   │   ├── Login.vue      # 登录页
│   │   │   ├── Register.vue   # 注册页
│   │   │   ├── Dashboard.vue  # 仪表盘（文档列表）
│   │   │   ├── Reader.vue     # 阅读器
│   │   │   └── Words.vue      # 生词本
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 应用入口
│   ├── package.json           # 前端依赖
│   ├── vite.config.js         # Vite 配置
│   └── index.html             # HTML 模板
│
├── README.md                   # 项目说明
├── DEPLOYMENT.md               # 部署指南
├── PROJECT_STRUCTURE.md        # 本文件
└── .gitignore                 # Git 忽略文件
```

## 核心模块说明

### 后端模块

#### 1. 用户认证模块 (`app/api/v1/endpoints/auth.py`)
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

#### 2. 文档管理模块 (`app/api/v1/endpoints/documents.py`)
- `POST /api/v1/documents/upload` - 上传文档
- `GET /api/v1/documents/` - 获取文档列表
- `GET /api/v1/documents/{id}` - 获取文档详情
- `GET /api/v1/documents/{id}/pages/{page_number}` - 获取文档页面
- `DELETE /api/v1/documents/{id}` - 删除文档

#### 3. 单词查询模块 (`app/api/v1/endpoints/words.py`)
- `GET /api/v1/words/lookup` - 查询单词释义（并记录点击）
- `GET /api/v1/words/` - 获取生词列表
- `GET /api/v1/words/{word}` - 获取单词详情（含上下文）
- `PATCH /api/v1/words/{word}/status` - 更新单词掌握状态

### 前端页面

#### 1. 登录/注册页
- 用户认证入口
- 表单验证
- 错误提示

#### 2. 仪表盘 (`Dashboard.vue`)
- 文档上传（拖拽上传）
- 文档列表展示（卡片网格）
- 文档搜索
- 文档删除

#### 3. 阅读器 (`Reader.vue`)
- 文档内容展示
- 翻页功能
- 单词点击查词
- 单词释义侧边栏
- 已点击单词高亮

#### 4. 生词本 (`Words.vue`)
- 生词列表展示
- 排序功能（按时间、点击次数、字母）
- 筛选功能（按掌握状态）
- 单词详情查看（含上下文）
- 掌握状态更新

## 数据库表结构

### users 表
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- hashed_password: 加密密码
- is_active: 是否激活
- created_at, updated_at: 时间戳

### documents 表
- id: 主键
- user_id: 用户ID（外键）
- title: 文档标题
- filename: 文件名
- file_path: 文件路径
- content: 文档完整内容
- total_pages: 总页数
- created_at, updated_at: 时间戳

### pages 表
- id: 主键
- document_id: 文档ID（外键）
- page_number: 页码
- content: 页面内容
- created_at: 创建时间

### word_clicks 表
- id: 主键
- user_id: 用户ID（外键）
- document_id: 文档ID（外键）
- word: 单词（索引）
- click_count: 点击次数
- first_clicked_at: 首次点击时间
- last_clicked_at: 最后点击时间
- mastery_status: 掌握状态（生词/熟悉/已掌握）

## 技术栈

### 后端
- **FastAPI**: 现代、快速的 Web 框架
- **SQLAlchemy**: ORM 框架
- **Alembic**: 数据库迁移工具
- **PyPDF2**: PDF 解析
- **ebooklib**: EPUB 解析
- **JWT**: 身份认证

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 快速构建工具
- **Vue Router**: 路由管理
- **Pinia**: 状态管理
- **Element Plus**: UI 组件库
- **Axios**: HTTP 客户端

## 开发流程

1. **环境设置**: 安装 Python、Node.js、PostgreSQL
2. **数据库初始化**: 运行 Alembic 迁移
3. **后端启动**: 运行 `uvicorn app.main:app --reload`
4. **前端启动**: 运行 `npm run dev`
5. **开发调试**: 使用浏览器访问 http://localhost:5173

## 下一步开发建议

### 第二阶段功能
- [ ] 完善 PDF/EPUB 解析（支持图片、格式）
- [ ] 优化单词点击识别（处理复合词、连字符）
- [ ] 添加单词收藏功能
- [ ] 实现单词复习提醒

### 第三阶段功能
- [ ] 移动端适配
- [ ] 单词测验功能
- [ ] 导出生词本（CSV/PDF）
- [ ] 学习统计图表
- [ ] 社交功能（分享、讨论）

