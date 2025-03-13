import pytest
from fastapi.testclient import TestClient
from app import app
from app_modules.auth import fake_users_db

# 测试用户注册
def test_register_user(client, test_user_data):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "password": "newpassword",
            "email": "newuser@example.com",
            "full_name": "New User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "created_at" in data
    assert not data["disabled"]

# 测试重复用户名注册
def test_register_existing_user(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "username": test_user.username,
            "password": "somepassword",
            "email": "another@example.com",
            "full_name": "Another User"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "用户名已存在"

# 测试用户登录
def test_login_user(client, test_user, test_user_data):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# 测试错误密码登录
def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user.username,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "用户名或密码不正确"

# 测试获取当前用户信息
def test_read_users_me(authorized_client, test_user):
    response = authorized_client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name

# 测试未授权访问
def test_read_users_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401