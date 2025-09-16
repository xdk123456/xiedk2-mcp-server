@echo off

REM MCP Server 启动脚本 (Windows)

REM 设置Python解释器路径
SET PYTHON_PATH=C:/Users/xiedk2/AppData/Local/Programs/Python/Python313/python.exe

REM 检查Python是否存在
IF NOT EXIST "%PYTHON_PATH%" (
    echo Python解释器未找到: %PYTHON_PATH%
    echo 请检查Python安装路径是否正确
    pause
    exit /b 1
)

REM 安装依赖
"%PYTHON_PATH%" -m pip install -r requirements.txt

REM 启动服务器
"%PYTHON_PATH%" mcp_server.py

pause