# Trae客户端 MCP Server配置指南

## 配置说明

根据您的需求，以下是在Trae客户端添加查询出口IP的MCP Server工具的完整配置：

```json
{
  "mcpServers": {
    "ipInfoTool": {
      "command": "C:/Users/xiedk2/AppData/Local/Programs/Python/Python313/python.exe",
      "args": [
        "mcp_client.py"
      ],
      "env": {}
    }
  }
}
```

## 添加步骤

按照以下步骤在Trae客户端中添加这个MCP Server工具：

1. 在Trae客户端中找到并打开"手动配置"对话框（如您提供的截图所示）

2. 复制上面的完整JSON配置

3. 将复制的配置粘贴到输入框中

4. 点击"确认"按钮完成添加

## 配置说明

- **ipInfoTool**: 工具的名称，可以根据您的需要自定义
- **command**: Python解释器的完整路径，确保使用您系统中正确的Python路径
- **args**: 运行的脚本参数，这里指向mcp_client.py文件
- **env**: 环境变量配置，这里为空对象

## 使用说明

添加完成后，您可以在Trae客户端中找到并使用这个名为"ipInfoTool"的工具。运行该工具将会调用我们的MCP客户端代码，获取您的出口IP信息。

请确保：
- mcp_client.py文件位于当前工作目录下
- MCP Server已经启动（可以通过运行start_server.bat启动）
- 您的系统已安装必要的Python依赖（可以通过requirements.txt安装）
- **特别注意**：请确保在mcp_client_server_config.json文件中，客户端配置的server_url设置为"http://127.0.0.1:5000"，这样可以更准确地模拟实际在服务端搭建mcp server后的效果