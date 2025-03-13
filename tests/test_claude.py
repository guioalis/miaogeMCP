import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app import app

# 测试获取Claude配置
def test_get_claude_config(authorized_client):
    response = authorized_client.get("/api/claude/config")
    assert response.status_code == 200
    data = response.json()
    assert "available_models" in data
    assert "default_model" in data
    assert "max_tokens_limit" in data
    assert "api_status" in data

# 测试未授权访问Claude配置
def test_get_claude_config_unauthorized(client):
    response = client.get("/api/claude/config")
    assert response.status_code == 401

# 测试与Claude聊天
@patch('anthropic.Anthropic')
@patch('app_modules.claude.get_docker_context')
def test_chat_with_claude(mock_get_docker_context, mock_anthropic, authorized_client):
    # 模拟Docker上下文
    mock_get_docker_context.return_value = {
        "containers": [
            {
                "id": "abc123def456",
                "name": "test-container",
                "image": "nginx:latest",
                "status": "running"
            }
        ],
        "images": [
            {
                "id": "img123456789",
                "tags": ["nginx:latest"],
                "size": 120
            }
        ],
        "timestamp": "2023-01-01T12:00:00"
    }
    
    # 模拟Anthropic客户端
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    
    # 模拟消息响应
    mock_message = MagicMock()
    mock_message.content = [{"type": "text", "text": "这是Claude的回复"}]
    mock_message.stop_reason = "end_turn"
    mock_message.model = "claude-3-opus-20240229"
    mock_client.messages.create.return_value = mock_message
    
    # 发送请求
    response = authorized_client.post(
        "/api/claude/chat",
        json={
            "prompt": "如何使用Docker?",
            "model": "claude-3-opus-20240229",
            "max_tokens_to_sample": 1000
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert "completion" in data
    assert "stop_reason" in data
    assert "model" in data

# 测试API密钥未配置的情况
@patch('app_modules.claude.ANTHROPIC_API_KEY', None)
def test_chat_with_claude_no_api_key(authorized_client):
    response = authorized_client.post(
        "/api/claude/chat",
        json={
            "prompt": "如何使用Docker?",
            "model": "claude-3-opus-20240229",
            "max_tokens_to_sample": 1000
        }
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Claude API密钥未配置"