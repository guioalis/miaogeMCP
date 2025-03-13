import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app import app
from app_modules.containers import convert_container
from datetime import datetime

# 测试获取容器列表
@patch('app_modules.containers.client')
def test_list_containers(mock_client, authorized_client):
    # 创建模拟容器对象
    mock_container = MagicMock()
    mock_container.id = "test-container-id"
    mock_container.name = "test-container"
    mock_container.image.tags = ["test-image:latest"]
    mock_container.status = "running"
    mock_container.attrs = {
        'Created': datetime.now(),
        'NetworkSettings': {'Ports': {'80/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '8080'}]}},
        'Mounts': [{'Source': '/host/path', 'Destination': '/container/path', 'Type': 'bind'}],
        'Config': {'Env': ['KEY1=VALUE1', 'KEY2=VALUE2']}
    }
    
    # 设置模拟客户端返回值
    mock_client.containers.list.return_value = [mock_container]
    
    # 发送请求
    response = authorized_client.get("/api/containers/")
    
    # 验证响应
    assert response.status_code == 200
    containers = response.json()
    assert len(containers) == 1
    assert containers[0]["id"] == "test-container-id"
    assert containers[0]["name"] == "test-container"
    assert containers[0]["image"] == "test-image:latest"
    assert containers[0]["status"] == "running"

# 测试获取单个容器
@patch('app_modules.containers.client')
def test_get_container(mock_client, authorized_client):
    # 创建模拟容器对象
    mock_container = MagicMock()
    mock_container.id = "test-container-id"
    mock_container.name = "test-container"
    mock_container.image.tags = ["test-image:latest"]
    mock_container.status = "running"
    mock_container.attrs = {
        'Created': datetime.now(),
        'NetworkSettings': {'Ports': {'80/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '8080'}]}},
        'Mounts': [{'Source': '/host/path', 'Destination': '/container/path', 'Type': 'bind'}],
        'Config': {'Env': ['KEY1=VALUE1', 'KEY2=VALUE2']}
    }
    
    # 设置模拟客户端返回值
    mock_client.containers.get.return_value = mock_container
    
    # 发送请求
    response = authorized_client.get("/api/containers/test-container-id")
    
    # 验证响应
    assert response.status_code == 200
    container = response.json()
    assert container["id"] == "test-container-id"
    assert container["name"] == "test-container"
    assert container["image"] == "test-image:latest"
    assert container["status"] == "running"

# 测试创建容器
@patch('app_modules.containers.client')
def test_create_container(mock_client, authorized_client):
    # 创建模拟容器对象
    mock_container = MagicMock()
    mock_container.id = "new-container-id"
    mock_container.name = "new-container"
    mock_container.image.tags = ["test-image:latest"]
    mock_container.status = "created"
    mock_container.attrs = {
        'Created': datetime.now(),
        'NetworkSettings': {'Ports': {'80/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '8080'}]}},
        'Mounts': [],
        'Config': {'Env': []}
    }
    
    # 设置模拟客户端返回值
    mock_client.containers.create.return_value = mock_container
    
    # 发送请求
    response = authorized_client.post(
        "/api/containers/create",
        json={
            "image": "test-image:latest",
            "name": "new-container",
            "ports": {"80/tcp": "8080"},
            "volumes": {"/host/path": "/container/path"},
            "environment": {"KEY1": "VALUE1"}
        }
    )
    
    # 验证响应
    assert response.status_code == 201
    container = response.json()
    assert container["id"] == "new-container-id"
    assert container["name"] == "new-container"
    assert container["image"] == "test-image:latest"
    assert container["status"] == "created"