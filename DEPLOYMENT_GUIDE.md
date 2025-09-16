# MCP Server 部署指南

本指南将帮助您在Ubuntu服务器上部署和管理MCP Server。

## 目录

- [前提条件](#前提条件)
- [快速部署](#快速部署)
- [手动部署步骤](#手动部署步骤)
- [配置说明](#配置说明)
- [服务管理](#服务管理)
- [HTTPS配置](#https配置)
- [Nginx反向代理配置](#nginx反向代理配置)
- [常见问题](#常见问题)

## 前提条件

- Ubuntu 18.04或更高版本
- 具有sudo权限的用户
- 服务器能够访问互联网（用于下载依赖）

## 快速部署

使用提供的一键部署脚本进行快速部署：

```bash
# 克隆仓库（如果尚未克隆）
git clone https://github.com/yourusername/mcp_server.git
cd mcp_server

# 赋予脚本执行权限
chmod +x deploy_mcp_server.sh

# 运行部署脚本（需要root权限）
sudo ./deploy_mcp_server.sh
```

## 手动部署步骤

如果您希望手动部署MCP Server，请按照以下步骤操作：

### 1. 安装系统依赖

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.9 python3.9-venv python3.9-dev git build-essential libssl-dev openssl
```

### 2. 克隆代码库

```bash
git clone https://github.com/yourusername/mcp_server.git
cd mcp_server
```

### 3. 创建Python虚拟环境

```bash
python3.9 -m venv venv
source venv/bin/activate
```

### 4. 安装Python依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. 创建.env配置文件

```bash
cat > .env << EOF
# 服务器端口
PORT=5000

# 调试模式
DEBUG=False

# HTTPS证书路径
SSL_CERT_PATH=cert.pem
SSL_KEY_PATH=key.pem
EOF
```

### 6. 生成自签名证书（可选）

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=mcp-server"
```

### 7. 启动服务器（开发模式）

```bash
python mcp_server.py
```

## 配置说明

MCP Server通过`.env`文件进行配置，主要配置项如下：