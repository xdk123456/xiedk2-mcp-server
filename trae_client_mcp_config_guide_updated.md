# Trae客户端 MCP Server配置指南（更新版）

### 为什么需要本指南？

您提到配置中引用的是本地路径，希望了解如何调整为使用`http://127.0.0.1:5000`这个MCP Server地址。这是一个很好的问题，涉及到MCP系统的配置机制。本指南将详细解释Trae客户端与MCP Server的交互原理，并提供多种方法来确保您的配置正确指向`http://127.0.0.1:5000`地址。

### 配置说明

根据您的需求，以下是在Trae客户端添加查询出口IP的MCP Server工具的完整配置指南。本指南将详细解释如何配置Trae客户端以连接到`http://127.0.0.1:5000`上运行的MCP Server。

### MCP客户端配置机制详解

通过查看代码，我发现MCP客户端程序（mcp_client.py）的配置加载机制如下：

1. **默认配置**：程序内部有一组默认配置（默认服务器地址为`https://localhost:5000`）
2. **配置文件**：程序会尝试加载`mcp_client_config.json`文件中的配置（如果存在）
3. **环境变量**：程序会读取环境变量，覆盖配置文件中的设置

这解释了为什么Trae客户端配置中使用本地路径，而不是直接指向MCP Server地址。Trae客户端只负责启动MCP客户端程序，而MCP客户端程序会根据自己的配置连接到正确的服务器地址。

### 完整的配置解决方案

我们需要确保MCP客户端程序能够正确连接到`http://127.0.0.1:5000`，有以下几种方法：

### 方法1：通过配置文件指定服务器地址

创建或修改`mcp_client_config.json`文件，确保它包含以下内容：

```json
{
  "server_url": "http://127.0.0.1:5000",
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

### 方法2：通过环境变量指定服务器地址

在Trae客户端配置中，您可以直接在`env`字段中设置环境变量：

```json
{
  "mcpServers": {
    "ipInfoTool": {
      "command": "C:/Users/xiedk2/AppData/Local/Programs/Python/Python313/python.exe",
      "args": [
        "mcp_client.py"
      ],
      "env": {
        "MCP_SERVER_URL": "http://127.0.0.1:5000"
      }
    }
  }
}
```

这种方法的优点是不需要创建或修改配置文件，直接在Trae配置中完成所有设置。

### 方法3：修改start_server.bat文件

如果您希望在启动服务器时同时确保客户端使用正确的地址，可以修改`start_server.bat`文件：

```batch
REM MCP Server 启动脚本 (Windows)

REM 设置Python解释器路径
SET PYTHON_PATH=C:/Users/xiedk2/AppData/Local/Programs/Python/Python313/python.exe

REM 设置MCP服务器地址环境变量
SET MCP_SERVER_URL=http://127.0.0.1:5000

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
```

### 完整的工作流程

以方法2（通过环境变量）为例，完整的工作流程如下：

1. **用户操作**：在Trae客户端中点击运行`ipInfoTool`工具
2. **Trae执行**：Trae调用配置中指定的Python解释器执行`mcp_client.py`，并传递`MCP_SERVER_URL=http://127.0.0.1:5000`环境变量