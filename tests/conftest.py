import pytest
import os
import sys
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from app_modules.auth import fake_users_db, get_password_hash, create_access_token
from app_modules.models import User, UserInDB

# 测试客户端
@pytest.fixture
def client():
    return TestClient(app)

# 测试用户数据
@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com",
        "full_name": "Test User"
    }

# 创建测试用户并返回用户信息
@pytest.fixture
def test_user(test_user_data):
    user_id = "test-user-id"
    hashed_password = get_password_hash(test_user_data["password"])
    
    user_dict = {
        "id": user_id,
        "username": test_user_data["username"],
        "email": test_user_data["email"],
        "full_name": test_user_data["full_name"],
        "disabled": False,
        "hashed_password": hashed_password,
        "created_at": datetime.now()
    }
    
    fake_users_db[test_user_data["username"]] = user_dict
    
    return UserInDB(**user_dict)

# 创建测试用户并返回访问令牌
@pytest.fixture
def test_user_token(test_user):
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": test_user.username}, expires_delta=access_token_expires
    )
    return access_token

# 带有授权头的客户端
@pytest.fixture
def authorized_client(client, test_user_token):
    client.headers = {
        "Authorization": f"Bearer {test_user_token}"
    }
    return client

# 模拟Docker客户端
@pytest.fixture
def mock_docker_client(monkeypatch):
    # 这里可以使用unittest.mock或pytest-mock来模拟Docker客户端
    # 根据实际测试需求实现
    pass