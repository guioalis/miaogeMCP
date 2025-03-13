import pytest
from unittest.mock import MagicMock, patch
import os
import tempfile
from fastapi.testclient import TestClient
from app import app

# 测试部署Compose堆栈
@patch('os.system')
@patch('tempfile.NamedTemporaryFile')
def test_compose_up(mock_temp_file, mock_system, authorized_client):
    # 模拟临时文件
    mock_file = MagicMock()
    mock_file.name = "/tmp/test_compose_12345.yml"
    mock_temp_file.return_value.__enter__.return_value = mock_file
    
    # 模拟系统命令执行成功
    mock_system.return_value = 0
    
    # 发送请求
    response = authorized_client.post(
        "/api/compose/up",
        json={
            "content": "version: '3'\nservices:\n  web:\n    image: nginx\n    ports:\n      - '80:80'"
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "已成功部署" in data["message"]
    
    # 验证临时文件写入
    mock_file.write.assert_called_once()
    
    # 验证系统命令调用
    mock_system.assert_called_once()
    assert "docker-compose" in mock_system.call_args[0][0]
    assert "up -d" in mock_system.call_args[0][0]

# 测试停止Compose堆栈
@patch('os.system')
@patch('tempfile.NamedTemporaryFile')
def test_compose_down(mock_temp_file, mock_system, authorized_client):
    # 模拟临时文件
    mock_file = MagicMock()
    mock_file.name = "/tmp/test_compose_12345.yml"
    mock_temp_file.return_value.__enter__.return_value = mock_file
    
    # 模拟系统命令执行成功
    mock_system.return_value = 0
    
    # 发送请求
    response = authorized_client.post(
        "/api/compose/down",
        json={
            "content": "version: '3'\nservices:\n  web:\n    image: nginx\n    ports:\n      - '80:80'"
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "已成功停止" in data["message"]
    
    # 验证临时文件写入
    mock_file.write.assert_called_once()
    
    # 验证系统命令调用
    mock_system.assert_called_once()
    assert "docker-compose" in mock_system.call_args[0][0]
    assert "down" in mock_system.call_args[0][0]

# 测试获取Compose堆栈状态
@patch('app_modules.compose.client')
@patch('yaml.safe_load')
@patch('tempfile.NamedTemporaryFile')
def test_compose_status(mock_temp_file, mock_yaml_load, mock_client, authorized_client):
    # 模拟临时文件
    mock_file = MagicMock()
    mock_file.name = "/tmp/test_compose_12345.yml"
    mock_temp_file.return_value.__enter__.return_value = mock_file
    
    # 模拟YAML解析
    mock_yaml_load.return_value = {
        'services': {
            'web': {'image': 'nginx'},
            'db': {'image': 'postgres'}
        }
    }
    
    # 模拟容器
    mock_web_container = MagicMock()
    mock_web_container.id = "web-container-id"
    mock_web_container.name = "web"
    mock_web_container.status = "running"
    
    mock_db_container = MagicMock()
    mock_db_container.id = "db-container-id"
    mock_db_container.name = "db"
    mock_db_container.status = "exited"
    
    # 设置模拟客户端返回值
    mock_client.containers.list.return_value = [mock_web_container, mock_db_container]
    
    # 发送请求
    response = authorized_client.post(
        "/api/compose/status",
        json={
            "content": "version: '3'\nservices:\n  web:\n    image: nginx\n  db:\n    image: postgres"
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "is_running" in data
    assert data["is_running"] == False  # 因为db容器状态为exited