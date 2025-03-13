import pytest
from fastapi.testclient import TestClient
from app import app

# 测试根路由
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "欢迎使用喵哥docker（MCP）服务！"}

# 测试健康检查端点
def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}