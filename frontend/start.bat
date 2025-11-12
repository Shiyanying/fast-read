@echo off
REM ReadSmart 前端启动脚本 (Windows)

echo 启动 ReadSmart 前端服务...

REM 检查 node_modules
if not exist "node_modules" (
    echo 安装依赖...
    call npm install
)

REM 启动开发服务器
echo 启动开发服务器...
call npm run dev

pause

