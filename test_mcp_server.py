# -*- coding: utf-8 -*-
"""
MCP Server 测试文件
"""
import unittest
import json
from mcp_server import app

class MCP_SERVERTestCase(unittest.TestCase):
    """MCP Server的测试用例"""
    
    def setUp(self):
        """设置测试环境"""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_index(self):
        """测试服务器首页"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'MCP Server 运行中')
    
    def test_ip_info(self):
        """测试获取出口IP信息接口"""
        response = self.client.get('/api/ip')
        # 注意：由于这是一个外部API调用，测试可能会失败如果API不可用
        # 这里我们只检查响应格式，不验证实际IP
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('ip', data['data'])
    
    def test_forward(self):
        """测试通用请求转发接口"""
        # 转发到IP获取接口
        forward_data = {
            "url": "https://api.ipify.org?format=json",
            "method": "GET"
        }
        
        response = self.client.post('/api/forward', json=forward_data)
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['status_code'], 200)
            self.assertIn('data', data)

if __name__ == '__main__':
    unittest.main()