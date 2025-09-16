from flask import Flask, request, jsonify, Response
import requests
import logging
import os
import json
from datetime import datetime
import ssl
import socket

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 从配置文件加载配置
def load_config():
    """加载服务器配置"""
    config_path = 'mcp_client_server_config.json'
    default_config = {
        'server_port': 5000,
        'debug_mode': True,
        'ssl_cert_path': 'ssl/cert.pem',
        'ssl_key_path': 'ssl/key.pem',
        'log_level': 'INFO',
        'timeout': 30
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            default_config.update(user_config)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
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
    
    return default_config

# 加载配置
config = load_config()

# 设置日志级别
logger.setLevel(getattr(logging, config['log_level'], logging.INFO))

# IP信息资源类
class IPInfoResource:
    """提供IP信息相关功能"""
    
    @staticmethod
    def get_ip_info():
        """获取当前服务器的出口IP信息"""
        try:
            # 获取本地IP地址
            local_ip = socket.gethostbyname(socket.gethostname())
            
            # 获取公网IP地址
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
            
            # 获取地理位置信息
            geo_info = requests.get(f'https://ipapi.co/{public_ip}/json/', timeout=5).json()
            
            return {
                'local_ip': local_ip,
                'public_ip': public_ip,
                'location': geo_info.get('city', '') + ', ' + geo_info.get('region', '') + ', ' + geo_info.get('country_name', ''),
                'isp': geo_info.get('org', '')
            }
        except Exception as e:
            logger.error(f"获取IP信息失败: {e}")
            return {
                'local_ip': '无法获取',
                'public_ip': '无法获取',
                'location': '无法获取',
                'isp': '无法获取',
                'error': str(e)
            }

# MCP转发资源类
class MCPForwardResource:
    """提供MCP请求转发功能"""
    
    @staticmethod
    def forward_request(url, method, headers=None, data=None, params=None):
        """转发HTTP请求"""
        try:
            # 准备请求头
            request_headers = headers or {}
            
            # 记录请求信息
            logger.info(f"转发请求: {method} {url}")
            logger.debug(f"请求头: {request_headers}")
            logger.debug(f"请求数据: {data}")
            
            # 发送请求
            response = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                data=data,
                params=params,
                timeout=config['timeout'],
                verify=False  # 忽略SSL验证（生产环境应设为True）
            )
            
            # 记录响应信息
            logger.info(f"响应状态码: {response.status_code}")
            
            # 尝试解析JSON响应
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response_data
            }
        except Exception as e:
            logger.error(f"转发请求失败: {e}")
            return {
                'status_code': 500,
                'error': str(e)
            }

# 首页路由
@app.route('/')
def index():
    """首页，返回服务器信息"""
    return jsonify({
        'status': 'running',
        'name': 'MCP Server',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'available_endpoints': ['/', '/api/ip-info', '/api/forward']
    })

# IP信息路由
@app.route('/api/ip-info', methods=['GET'])
def get_ip_info():
    """获取出口IP信息"""
    ip_info = IPInfoResource.get_ip_info()
    return jsonify(ip_info)

# 通用请求转发路由
@app.route('/api/forward', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def forward_request():
    """转发HTTP请求"""
    # 获取目标URL
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing target URL'}), 400
    
    # 获取请求方法
    method = request.method
    
    # 获取请求头（排除Flask特定的头信息）
    headers = {
        key: value for key, value in request.headers.items()
        if not key.lower().startswith('x-') and key.lower() != 'host'
    }
    
    # 获取请求数据
    try:
        data = request.get_json() if request.is_json else request.data
    except Exception:
        data = request.data
    
    # 获取查询参数（排除url参数）
    params = {
        key: value for key, value in request.args.items()
        if key.lower() != 'url'
    }
    
    # 转发请求
    result = MCPForwardResource.forward_request(url, method, headers, data, params)
    
    # 返回响应
    if 'error' in result:
        return jsonify(result), result.get('status_code', 500)
    
    # 创建响应对象
    response = Response(
        json.dumps(result['data']),
        status=result['status_code'],
        mimetype='application/json'
    )
    
    # 设置响应头
    for key, value in result['headers'].items():
        if key.lower() not in ['content-length', 'content-encoding']:
            response.headers[key] = value
    
    return response

# 启动服务器
if __name__ == '__main__':
    # 检查是否启用SSL
    use_ssl = os.path.exists(config['ssl_cert_path']) and os.path.exists(config['ssl_key_path'])
    
    if use_ssl:
        # 使用SSL启动服务器
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(config['ssl_cert_path'], config['ssl_key_path'])
        
        logger.info(f"MCP Server 启动成功 (HTTPS)，端口: {config['server_port']}")
        app.run(
            host='0.0.0.0',
            port=config['server_port'],
            debug=config['debug_mode'],
            ssl_context=context
        )
    else:
        # 不使用SSL启动服务器
        logger.info(f"MCP Server 启动成功 (HTTP)，端口: {config['server_port']}")
        app.run(
            host='0.0.0.0',
            port=config['server_port'],
            debug=config['debug_mode']
        )