# MCP Server

MCP Server是一个用于将HTTPS请求转化为HTTP请求的服务器，它可以转发请求到公开的API接口，并将响应返回给客户端。

## 功能特性

- 获取出口IP信息
- 获取天气信息
- 通用HTTP请求转发
- 支持HTTPS（需要配置证书）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建`.env`文件，并配置以下环境变量：

```env
# 服务器端口
PORT=5000

# 调试模式
DEBUG=False

# HTTPS证书路径（可选）
SSL_CERT_PATH=cert.pem
SSL_KEY_PATH=key.pem
```

### 3. 生成自签名证书（可选）

如果你需要使用HTTPS，可以使用OpenSSL生成自签名证书：

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### 4. 启动服务器

#### Windows

```bash
start_server.bat
```

#### Linux/Mac

```bash
chmod +x start_server.sh
./start_server.sh
```

或者直接运行：

```bash
python mcp_server.py
```

## API 接口

### 1. 获取出口IP信息

```
GET /api/ip
```

**响应示例：**

```json
{
  "success": true,
  "data": {
    "ip": "1.2.3.4"
  },
  "message": "出口IP信息获取成功"
}
```

### 2. 获取天气信息

```
GET /api/weather
GET /api/weather/<city>
```

**响应示例：**

```json
{
  "success": true,
  "data": {"weather_data": "..."},
  "message": "beijing天气信息获取成功"
}
```