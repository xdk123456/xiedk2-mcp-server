# MCP Client 配置指南

本指南将帮助您配置MCP Client以连接到MCP Server。

## 配置文件说明

`mcp_client_config.json` 文件包含了客户端连接服务器所需的所有配置参数。以下是各参数的详细说明：

### 1. server_url

服务器的URL地址，格式为 `https://[hostname]:[port]`

**示例：**
```json
"server_url": "https://localhost:5000"
```

### 2. timeout

请求超时时间（秒）

**示例：**
```json
"timeout": 30
```

### 3. retry_count

请求失败时的重试次数

**示例：**
```json
"retry_count": 3
```

### 4. retry_delay

重试间隔时间（秒）

**示例：**
```json
"retry_delay": 1
```

### 5. verify_ssl

是否验证SSL证书

- `true`: 验证SSL证书（生产环境推荐）
- `false`: 不验证SSL证书（开发环境使用自签名证书时推荐）

**示例：**
```json
"verify_ssl": false
```

### 6. headers

请求头信息

**示例：**
```json
"headers": {
    "Content-Type": "application/json",
    "User-Agent": "MCP Client/1.0"
}
```

## 配置示例

下面是一个完整的配置文件示例：

```json
{
    "server_url": "https://localhost:5000",
    "timeout": 30,
    "retry_count": 3,
    "retry_delay": 1,
    "verify_ssl": false,
    "headers": {
        "Content-Type": "application/json",
        "User-Agent": "MCP Client/1.0"
    }
}
```

## 环境变量覆盖

您可以通过环境变量来覆盖配置文件中的参数。环境变量的命名规则为 `MCP_` 前缀加上配置参数名（大写）。

例如，要覆盖 `server_url` 参数：

```bash
# Windows
set MCP_SERVER_URL=https://example.com:5000

# Linux/Mac
export MCP_SERVER_URL=https://example.com:5000
```