import requests
import json
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClient:
    """MCP服务器客户端，用于与MCP服务器进行通信"""
    
    def __init__(self, config_file='mcp_client_server_config.json'):
        """初始化MCP客户端
        
        Args:
            config_file: 配置文件路径
        """
        self.config = self.load_config(config_file)
        self.server_url = self.config.get('server_url', 'http://127.0.0.1:5000')
        
    def load_config(self, config_file):
        """加载配置文件
        
        Args:
            config_file: 配置文件路径
        
        Returns:
            dict: 配置字典
        """
        default_config = {
            'server_url': 'http://127.0.0.1:5000',
            'timeout': 30,
            'retry_count': 3,
            'retry_delay': 2,
            'verify_ssl': False
        }
        
        # 从配置文件加载配置
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                default_config.update(config)
                logger.info(f"成功加载配置文件: {config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
        else:
            logger.warning(f"配置文件不存在: {config_file}，使用默认配置")
        
        # 环境变量覆盖配置
        for key, value in default_config.items():
            env_key = f'MCP_{key.upper()}'
            if env_key in os.environ:
                env_value = os.environ[env_key]
                # 根据值的类型进行转换
                if isinstance(value, bool):
                    default_config[key] = env_value.lower() == 'true'
                elif isinstance(value, int):
                    try:
                        default_config[key] = int(env_value)
                    except ValueError:
                        pass
                else:
                    default_config[key] = env_value
                logger.info(f"环境变量覆盖配置: {key} = {default_config[key]}")
        
        return default_config
        
    def _send_request(self, endpoint, method='GET', **kwargs):
        """向MCP服务器发送请求
        
        Args:
            endpoint: API端点
            method: 请求方法
            **kwargs: 其他请求参数
        
        Returns:
            dict: 响应结果
        """
        url = f"{self.server_url}{endpoint}"
        
        # 配置请求参数
        request_kwargs = {
            'timeout': self.config.get('timeout', 30),
            'verify': self.config.get('verify_ssl', False)
        }
        request_kwargs.update(kwargs)
        
        # 添加请求头
        headers = request_kwargs.get('headers', {})
        headers.setdefault('Content-Type', 'application/json')
        request_kwargs['headers'] = headers
        
        # 重试机制
        retry_count = self.config.get('retry_count', 3)
        retry_delay = self.config.get('retry_delay', 2)
        
        for attempt in range(retry_count):
            try:
                logger.info(f"发送请求: {method} {url}")
                
                # 发送请求
                response = requests.request(method, url, **request_kwargs)
                
                # 检查响应状态
                response.raise_for_status()
                
                # 尝试解析JSON响应
                try:
                    return response.json()
                except ValueError:
                    return {'status': 'success', 'data': response.text}
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"请求失败 (尝试 {attempt + 1}/{retry_count}): {e}")
                
                # 如果不是最后一次尝试，则等待后重试
                if attempt < retry_count - 1:
                    import time
                    time.sleep(retry_delay)
                else:
                    logger.error(f"请求最终失败: {e}")
                    return {'status': 'error', 'message': str(e)}
    
    def get_server_status(self):
        """获取MCP服务器状态
        
        Returns:
            dict: 服务器状态信息
        """
        return self._send_request('/')
    
    def get_ip_info(self):
        """获取出口IP信息
        
        Returns:
            dict: IP信息
        """
        return self._send_request('/api/ip-info')
    
    def forward_request(self, target_url, method='GET', headers=None, data=None, params=None):
        """转发HTTP请求到目标URL
        
        Args:
            target_url: 目标URL
            method: 请求方法
            headers: 请求头
            data: 请求数据
            params: 查询参数
        
        Returns:
            dict: 转发请求的响应结果
        """
        # 准备查询参数
        forward_params = {'url': target_url}
        if params:
            forward_params.update(params)
        
        # 准备请求体
        request_data = None
        if data:
            # 如果data是字典，转换为JSON字符串
            if isinstance(data, dict):
                request_data = json.dumps(data)
            else:
                request_data = data
        
        # 发送转发请求
        return self._send_request(
            '/api/forward',
            method=method,
            headers=headers,
            data=request_data,
            params=forward_params
        )
    
    def get_weather_info(self, location):
        """获取天气信息（示例功能）
        
        Args:
            location: 位置信息
        
        Returns:
            dict: 天气信息
        """
        # 这里使用一个示例API，实际应用中需要替换为真实的天气API
        weather_api_url = f"https://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q={location}&aqi=no"
        
        return self.forward_request(weather_api_url)
    
    def get_time_info(self):
        """获取当前时间信息
        
        Returns:
            dict: 时间信息
        """
        # 使用世界时间API
        time_api_url = "http://worldtimeapi.org/api/ip"
        
        return self.forward_request(time_api_url)
    
    def save_config(self, config_file='mcp_client_server_config.json'):
        """保存当前配置到文件
        
        Args:
            config_file: 配置文件路径
        
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"配置已保存到: {config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def update_config(self, new_config):
        """更新配置
        
        Args:
            new_config: 新的配置字典
        
        Returns:
            dict: 更新后的配置
        """
        self.config.update(new_config)
        logger.info(f"配置已更新: {new_config}")
        
        # 如果更新了server_url，同步更新
        if 'server_url' in new_config:
            self.server_url = new_config['server_url']
            
        return self.config

# 示例用法
if __name__ == '__main__':
    # 创建MCP客户端实例
    client = MCPClient()
    
    # 获取服务器状态
    print("\n=== 获取服务器状态 ===")
    status = client.get_server_status()
    print(json.dumps(status, indent=4, ensure_ascii=False))
    
    # 获取IP信息
    print("\n=== 获取IP信息 ===")
    ip_info = client.get_ip_info()
    print(json.dumps(ip_info, indent=4, ensure_ascii=False))
    
    # 转发请求获取时间信息
    print("\n=== 获取时间信息 ===")
    time_info = client.get_time_info()
    print(json.dumps(time_info, indent=4, ensure_ascii=False))
    
    # 自定义转发请求示例
    print("\n=== 自定义转发请求示例 ===")
    custom_headers = {'X-Custom-Header': 'MCP-Client'}
    custom_response = client.forward_request(
        'https://httpbin.org/get',
        method='GET',
        headers=custom_headers,
        params={'test': '123'}
    )
    print(json.dumps(custom_response, indent=4, ensure_ascii=False))