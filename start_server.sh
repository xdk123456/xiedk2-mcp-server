#!/bin/bash

# MCP Server 启动脚本 (Linux/Ubuntu)

# 设置Python解释器路径
PYTHON_PATH="$(which python3)"

# 检查Python是否存在
if [ ! -x "$PYTHON_PATH" ]; then
    echo "Python解释器未找到"
    echo "请安装Python 3"
    exit 1
fi

# 安装依赖
"$PYTHON_PATH" -m pip install -r requirements.txt

# 启动服务器
"$PYTHON_PATH" mcp_server.py