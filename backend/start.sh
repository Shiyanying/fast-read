#!/bin/bash

# ReadSmart 后端启动脚本

echo "启动 ReadSmart 后端服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，请从 .env.example 复制并配置"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "已创建 .env 文件，请编辑配置"
    fi
fi

# 运行数据库迁移
echo "运行数据库迁移..."
alembic upgrade head

# 创建上传目录
mkdir -p uploads

# 启动服务
echo "启动服务..."
uvicorn app.main:app --reload --port 8000

