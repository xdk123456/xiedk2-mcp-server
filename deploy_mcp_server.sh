#!/bin/bash

# MCP服务器部署脚本
# 此脚本用于在Ubuntu服务器上部署MCP服务器

# 设置变量
INSTALL_DIR="/opt/mcp_server"
REPO_URL="https://github.com/xdk123456/xiedk2-mcp-server.git"
PYTHON_VERSION="3.10"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_NAME="mcp_server"
USER="ubuntu"
GROUP="ubuntu"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 检查是否以root用户运行
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请以root用户运行此脚本${NC}"
    exit 1
fi

# 安装系统依赖
echo -e "${BLUE}安装系统依赖...${NC}"
apt update && apt upgrade -y
apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev git curl nginx

# 创建安装目录
echo -e "${BLUE}创建安装目录...${NC}"
mkdir -p $INSTALL_DIR
chown $USER:$GROUP $INSTALL_DIR

# 克隆代码库
echo -e "${BLUE}克隆代码库...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${YELLOW}代码库已存在，更新代码...${NC}"
    cd $INSTALL_DIR
    git pull
else
    git clone $REPO_URL $INSTALL_DIR
fi

# 创建Python虚拟环境
echo -e "${BLUE}创建Python虚拟环境...${NC}"
sudo -u $USER python${PYTHON_VERSION} -m venv $VENV_DIR

# 安装Python依赖
echo -e "${BLUE}安装Python依赖...${NC}"
sudo -u $USER $VENV_DIR/bin/pip install --upgrade pip
sudo -u $USER $VENV_DIR/bin/pip install -r $INSTALL_DIR/requirements.txt

# 创建.env配置文件
echo -e "${BLUE}创建.env配置文件...${NC}"
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cat > $INSTALL_DIR/.env << EOF
# MCP服务器配置
MCP_SERVER_PORT=5000
MCP_DEBUG_MODE=false
MCP_LOG_LEVEL=INFO
MCP_TIMEOUT=30
# SSL配置（可选）
# MCP_SSL_CERT_PATH=ssl/cert.pem
# MCP_SSL_KEY_PATH=ssl/key.pem
EOF
    chown $USER:$GROUP $INSTALL_DIR/.env
else
    echo -e "${YELLOW}.env配置文件已存在，跳过创建${NC}"
fi

# 创建配置文件
if [ ! -f "$INSTALL_DIR/mcp_client_server_config.json" ]; then
    echo -e "${BLUE}创建配置文件...${NC}"
    cat > $INSTALL_DIR/mcp_client_server_config.json << EOF
{
    "server_port": 5000,
    "debug_mode": false,
    "ssl_cert_path": "ssl/cert.pem",
    "ssl_key_path": "ssl/key.pem",
    "log_level": "INFO",
    "timeout": 30,
    "server_url": "http://127.0.0.1:5000",
    "verify_ssl": false,
    "retry_count": 3,
    "retry_delay": 2
}
EOF
    chown $USER:$GROUP $INSTALL_DIR/mcp_client_server_config.json
else
    echo -e "${YELLOW}配置文件已存在，跳过创建${NC}"
fi

# 创建SSL证书目录和自签名证书
echo -e "${BLUE}创建SSL证书目录和自签名证书...${NC}"
mkdir -p $INSTALL_DIR/ssl

# 检查是否已经存在SSL证书
if [ ! -f "$INSTALL_DIR/ssl/cert.pem" ] || [ ! -f "$INSTALL_DIR/ssl/key.pem" ]; then
    echo -e "${BLUE}生成自签名SSL证书...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout $INSTALL_DIR/ssl/key.pem -out $INSTALL_DIR/ssl/cert.pem -subj "/CN=mcp-server"
    chown -R $USER:$GROUP $INSTALL_DIR/ssl
else
    echo -e "${YELLOW}SSL证书已存在，跳过创建${NC}"
fi

# 创建系统服务文件
echo -e "${BLUE}创建系统服务文件...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=MCP Server
After=network.target

[Service]
User=$USER
Group=$GROUP
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/mcp_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置并启动服务
echo -e "${BLUE}重新加载systemd配置并启动服务...${NC}"
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo -e "${BLUE}配置Nginx作为反向代理...${NC}"
# 备份现有的Nginx配置
if [ -f "/etc/nginx/sites-available/default" ]; then
    mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
fi

# 创建Nginx配置文件
cat > /etc/nginx/sites-available/default << EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 静态文件配置（如果需要）
    # location /static {
    #     alias $INSTALL_DIR/static;
    # }
}
EOF

# 测试Nginx配置并重启
echo -e "${BLUE}测试Nginx配置并重启...${NC}"
nginx -t
if [ $? -eq 0 ]; then
    systemctl restart nginx
else
    echo -e "${RED}Nginx配置错误，请检查配置文件${NC}"
    exit 1
fi

# 显示服务状态
echo -e "${GREEN}\n=== MCP服务器部署完成 ===${NC}"
echo -e "服务名称: ${BLUE}$SERVICE_NAME${NC}"
echo -e "安装目录: ${BLUE}$INSTALL_DIR${NC}"
echo -e "Python虚拟环境: ${BLUE}$VENV_DIR${NC}"

systemctl status $SERVICE_NAME --no-pager

echo -e "\n${GREEN}MCP服务器部署成功！${NC}"
echo -e "您可以通过以下命令管理服务："
echo -e "  systemctl start $SERVICE_NAME   # 启动服务"
echo -e "  systemctl stop $SERVICE_NAME    # 停止服务"
echo -e "  systemctl restart $SERVICE_NAME # 重启服务"
echo -e "  systemctl status $SERVICE_NAME  # 查看服务状态"
echo -e "\n请根据需要修改配置文件：${BLUE}$INSTALL_DIR/.env${NC} 和 ${BLUE}$INSTALL_DIR/mcp_client_server_config.json${NC}"
