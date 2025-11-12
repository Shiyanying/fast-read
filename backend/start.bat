@echo off
REM ReadSmart 后端启动脚本 (Windows)

echo 启动 ReadSmart 后端服务...

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 检查 .env 文件
if not exist ".env" (
    echo 警告: .env 文件不存在，请从 .env.example 复制并配置
    if exist ".env.example" (
        copy .env.example .env
        echo 已创建 .env 文件，请编辑配置
    )
)

REM 运行数据库迁移
echo 运行数据库迁移...
alembic upgrade head

REM 创建上传目录
if not exist "uploads" mkdir uploads

REM 启动服务
echo 启动服务...
uvicorn app.main:app --reload --port 8000

pause

