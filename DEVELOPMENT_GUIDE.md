# ReadSmart 开发指南

## 项目结构

```
fast-read/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API 路由
│   │   │   └── v1/
│   │   │       └── endpoints/  # API 端点
│   │   ├── core/        # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── database.py   # 数据库连接
│   │   │   └── security.py    # JWT 和密码加密
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic 数据验证
│   │   └── services/    # 业务逻辑
│   ├── alembic/         # 数据库迁移
│   └── requirements.txt
│
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── api/         # API 调用
│   │   ├── components/  # 组件
│   │   ├── router/      # 路由配置
│   │   ├── stores/      # Pinia 状态管理
│   │   └── views/        # 页面视图
│   └── package.json
│
└── README.md
```

---

## 开发环境设置

### 1. 启动开发服务器

**后端：**
```bash
cd backend
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload --port 8000
```

**前端：**
```bash
cd frontend
npm run dev
```

### 2. 热重载

- 后端：使用 `--reload` 参数，代码修改后自动重启
- 前端：Vite 自动热更新，无需手动刷新

---

## 添加新功能

### 添加新的 API 端点

1. **创建端点文件**：`backend/app/api/v1/endpoints/your_feature.py`
```python
from fastapi import APIRouter, Depends
from app.api.v1.dependencies import get_current_user

router = APIRouter()

@router.get("/your-endpoint")
async def your_function(current_user = Depends(get_current_user)):
    return {"message": "Hello"}
```

2. **注册路由**：在 `backend/app/api/v1/__init__.py` 中导入
```python
from app.api.v1.endpoints import your_feature
api_router.include_router(your_feature.router, prefix="/your-prefix", tags=["your-tag"])
```

### 添加新的数据库模型

1. **创建模型**：`backend/app/models/your_model.py`
```python
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class YourModel(Base):
    __tablename__ = "your_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

2. **创建迁移**：
```bash
cd backend
alembic revision --autogenerate -m "add your_model table"
alembic upgrade head
```

### 添加新的前端页面

1. **创建页面组件**：`frontend/src/views/YourPage.vue`
```vue
<template>
  <div>Your Page</div>
</template>

<script setup>
// 你的逻辑
</script>
```

2. **添加路由**：在 `frontend/src/router/index.js` 中
```javascript
{
  path: 'your-page',
  name: 'YourPage',
  component: () => import('@/views/YourPage.vue')
}
```

---

## 数据库操作

### 创建迁移

```bash
cd backend
alembic revision --autogenerate -m "描述你的更改"
```

### 应用迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
alembic downgrade -1  # 回滚一个版本
alembic downgrade base  # 回滚到初始状态
```

---

## 代码规范

### Python (后端)

- 使用类型提示
- 遵循 PEP 8 规范
- 使用 Pydantic 进行数据验证

### JavaScript/Vue (前端)

- 使用 Composition API
- 组件使用 `<script setup>`
- 使用 ESLint 检查代码

---

## 测试

### 后端测试

```bash
cd backend
pytest  # 如果配置了测试
```

### 前端测试

```bash
cd frontend
npm test  # 如果配置了测试
```

---

## 调试技巧

### 后端调试

1. **查看 API 文档**：http://localhost:8000/docs
2. **查看日志**：后端控制台输出
3. **使用断点**：在 IDE 中设置断点

### 前端调试

1. **浏览器开发者工具**：F12
2. **Vue DevTools**：安装 Vue 开发者工具扩展
3. **Console 日志**：使用 `console.log()` 调试

---

## 常见开发任务

### 修改数据库结构

1. 修改模型文件（`backend/app/models/`）
2. 生成迁移：`alembic revision --autogenerate -m "描述"`
3. 应用迁移：`alembic upgrade head`

### 添加新的 API

1. 在 `backend/app/api/v1/endpoints/` 创建端点
2. 在 `backend/app/api/v1/__init__.py` 注册路由
3. 创建对应的 Schema（`backend/app/schemas/`）

### 修改前端页面

1. 编辑对应的 Vue 文件（`frontend/src/views/`）
2. 保存后自动热更新
3. 在浏览器中查看效果

---

## Git 工作流

### 提交代码

```bash
# 查看更改
git status

# 添加文件
git add .

# 提交
git commit -m "描述你的更改"

# 推送到远程
git push
```

### 分支管理

```bash
# 创建新分支
git checkout -b feature/your-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/your-feature
```

---

## 性能优化

### 后端

- 使用数据库索引
- 实现查询缓存
- 优化数据库查询（避免 N+1 问题）

### 前端

- 使用懒加载路由
- 图片优化
- 代码分割

---

## 继续开发建议

1. **阅读现有代码**：了解项目结构和编码风格
2. **从简单功能开始**：先实现小的功能点
3. **保持代码整洁**：遵循项目规范
4. **及时提交代码**：使用 Git 管理版本
5. **编写注释**：复杂逻辑添加注释说明

---

## 获取帮助

- 查看 API 文档：http://localhost:8000/docs
- 查看项目文档：README.md, DEPLOYMENT.md
- 检查代码注释和类型提示

