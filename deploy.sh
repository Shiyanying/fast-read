#!/bin/bash

# ReadSmart 一键部署脚本 (Linux/Mac)
# 用于重建数据库和重新部署应用

echo "========================================"
echo "  ReadSmart 重建与部署"
echo "========================================"
echo ""

# 1. 停止并删除所有容器和卷
echo "[1/5] 停止现有容器并删除数据..."
docker compose down -v
echo ""

# 2. 重新构建镜像
echo "[2/5] 重新构建Docker镜像..."
docker compose build
if [ $? -ne 0 ]; then
    echo "错误: 构建失败"
    exit 1
fi
echo ""

# 3. 启动容器
echo "[3/5] 启动容器..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "错误: 启动失败"
    exit 1
fi
echo ""

# 4. 等待数据库就绪
echo "[4/5] 等待数据库启动..."
sleep 10

# 5. 运行数据库迁移
echo "[5/5] 运行数据库迁移..."
docker compose exec -T backend alembic upgrade head
if [ $? -ne 0 ]; then
    echo "警告: 迁移可能失败，请检查日志"
    echo "尝试手动运行: docker compose exec backend alembic upgrade head"
else
    echo "✓ 迁移成功!"
fi
echo ""

echo "========================================"
echo "  部署完成!"
echo "========================================"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:3000"
echo "  后端API文档: http://localhost:8000/docs"
echo ""
echo "查看日志:"
echo "  docker compose logs -f"
echo ""
echo "创建测试账号 (可选):"
echo '  docker compose exec backend python -c "from app.db.session import SessionLocal; from app.models.user import User; from app.core.security import get_password_hash; db = SessionLocal(); user = User(username=\"test\", email=\"test@example.com\", hashed_password=get_password_hash(\"test123\")); db.add(user); db.commit(); print(\"Created: test/test123\")"'
echo ""
