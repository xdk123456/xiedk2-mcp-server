# -*- coding: utf-8 -*-
"""
配置路径测试工具

该工具用于测试配置文件路径的正确性，确保MCP Server和Client能够正确加载配置文件。
"""
import os
import sys
import json

def test_config_file(file_path):
    """测试配置文件是否存在并可读取
    
    Args:
        file_path: 配置文件路径
        
    Returns:
        布尔值，表示配置文件是否有效
    """
    print(f"测试配置文件: {file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在")
        return False
    
    # 检查文件是否可读
    if not os.access(file_path, os.R_OK):
        print(f"错误: 文件不可读取")
        return False
    
    # 检查文件是否为JSON格式
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"成功: 配置文件可读取，包含 {len(config)} 个配置项")
        return True
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {str(e)}")
        return False
    except Exception as e:
        print(f"错误: 读取文件时出错 - {str(e)}")
        return False

def print_file_content(file_path):
    """打印文件内容
    
    Args:
        file_path: 文件路径