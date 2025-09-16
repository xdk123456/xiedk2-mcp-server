import json
from mcp_client import MCPClient

def main():
    """MCP客户端使用示例"""
    # 创建MCP客户端实例
    print("=== 创建MCP客户端实例 ===")
    # 可以指定配置文件路径，默认为'mcp_client_server_config.json'
    client = MCPClient()
    
    # 1. 获取服务器状态
    print("\n=== 1. 获取服务器状态 ===")
    try:
        status = client.get_server_status()
        print("服务器状态:")
        print(json.dumps(status, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"获取服务器状态失败: {e}")
    
    # 2. 获取出口IP信息
    print("\n=== 2. 获取出口IP信息 ===")
    try:
        ip_info = client.get_ip_info()
        print("IP信息:")
        print(f"本地IP: {ip_info.get('local_ip', '无法获取')}")
        print(f"公网IP: {ip_info.get('public_ip', '无法获取')}")
        print(f"地理位置: {ip_info.get('location', '无法获取')}")
        print(f"运营商: {ip_info.get('isp', '无法获取')}")
    except Exception as e:
        print(f"获取IP信息失败: {e}")
    
    # 3. 转发GET请求 - 获取时间信息
    print("\n=== 3. 转发GET请求 - 获取时间信息 ===")
    try:
        # 方法1: 使用封装好的方法
        time_info = client.get_time_info()
        print("时间信息:")
        print(json.dumps(time_info, indent=4, ensure_ascii=False))
        
        # 方法2: 使用通用转发方法
        time_api_url = "http://worldtimeapi.org/api/ip"
        time_info_custom = client.forward_request(time_api_url)
        print("\n使用通用转发方法获取时间信息:")
        print(f"状态码: {time_info_custom.get('status_code', '未知')}")
        if 'datetime' in time_info_custom:
            print(f"日期时间: {time_info_custom['datetime']}")
    except Exception as e:
        print(f"获取时间信息失败: {e}")
    
    # 4. 转发请求 - 带自定义请求头
    print("\n=== 4. 转发请求 - 带自定义请求头 ===")
    try:
        custom_headers = {
            'X-Custom-Header': 'MCP-Client-Example',
            'User-Agent': 'MCP-Client/1.0'
        }
        
        response = client.forward_request(
            'https://httpbin.org/get',
            method='GET',
            headers=custom_headers,
            params={'example': '123'}
        )
        
        print("带自定义请求头的响应:")
        print(f"状态码: {response.get('status_code', '未知')}")
        if 'headers' in response:
            print("响应头中接收到的自定义头:")
            for key, value in response['headers'].items():
                if key.lower() == 'x-custom-header'.lower():
                    print(f"  {key}: {value}")
    except Exception as e:
        print(f"发送自定义请求失败: {e}")
    
    # 5. 转发POST请求
    print("\n=== 5. 转发POST请求 ===")
    try:
        post_data = {
            'name': 'MCP Client',
            'version': '1.0',
            'features': ['IP查询', '请求转发', 'API调用']
        }
        
        response = client.forward_request(
            'https://httpbin.org/post',
            method='POST',
            data=post_data
        )
        
        print("POST请求响应:")
        print(f"状态码: {response.get('status_code', '未知')}")
        if 'json' in response:
            print("服务器接收到的数据:")
            print(json.dumps(response['json'], indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"发送POST请求失败: {e}")
    
    # 6. 配置管理示例
    print("\n=== 6. 配置管理示例 ===")
    try:
        # 查看当前配置
        print("当前配置:")
        print(json.dumps(client.config, indent=4, ensure_ascii=False))
        
        # 更新配置
        new_config = {
            'timeout': 60,
            'retry_count': 5
        }
        client.update_config(new_config)
        print("\n更新后的配置:")
        print(json.dumps(client.config, indent=4, ensure_ascii=False))
        
        # 保存配置（可选）
        # client.save_config()
        # print("配置已保存到文件")
    except Exception as e:
        print(f"配置管理操作失败: {e}")
    
    # 7. 错误处理示例
    print("\n=== 7. 错误处理示例 ===")
    try:
        # 尝试访问不存在的URL
        invalid_response = client.forward_request(
            'https://httpbin.org/status/404'
        )
        print(f"访问不存在资源的响应状态码: {invalid_response.get('status_code', '未知')}")
        
        # 尝试访问无效的URL格式
        invalid_url_response = client.forward_request(
            'invalid-url-format'
        )
        print(f"无效URL格式的响应: {invalid_url_response.get('error', '无错误信息')}")
    except Exception as e:
        print(f"错误处理测试异常: {e}")

if __name__ == "__main__":
    main()