import requests
import json
import os
from dotenv import load_dotenv
from mcp_client import MCPClient

# 加载环境变量
load_dotenv()

# 服务器配置
BASE_URL = "http://localhost:5000/api"

# 用户凭据
USERNAME = os.getenv("MCP_USERNAME", "admin")
PASSWORD = os.getenv("MCP_PASSWORD", "password")

# 存储访问令牌
access_token = None

# 登录并获取令牌
def login():
    global access_token
    
    url = f"{BASE_URL}/auth/token"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        result = response.json()
        access_token = result["access_token"]
        print(f"登录成功，获取令牌: {access_token[:10]}...")
        return True
    else:
        print(f"登录失败: {response.text}")
        return False

# 获取请求头（包含认证信息）
def get_headers():
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

# 获取Claude AI配置
def get_claude_config():
    url = f"{BASE_URL}/claude/config"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code == 200:
        config = response.json()
        print(f"Claude AI配置:")
        print(f"  - 可用模型: {', '.join(config['available_models'])}")
        print(f"  - 默认模型: {config['default_model']}")
        print(f"  - API状态: {config['api_status']}")
        return config
    else:
        print(f"获取Claude AI配置失败: {response.text}")
        return None

# 与Claude AI聊天
def chat_with_claude(prompt, model=None, max_tokens=1000, temperature=0.7):
    url = f"{BASE_URL}/claude/chat"
    data = {
        "prompt": prompt,
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature
    }
    
    if model:
        data["model"] = model
    
    response = requests.post(url, headers=get_headers(), json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Claude AI响应:")
        print(f"模型: {result['model']}")
        print(f"停止原因: {result['stop_reason']}")
        print(f"\n{result['completion']}")
        return result
    else:
        print(f"与Claude AI聊天失败: {response.text}")
        return None

# 异步与Claude AI聊天
def chat_with_claude_async(prompt, model=None, max_tokens=1000, temperature=0.7):
    url = f"{BASE_URL}/claude/chat/async"
    data = {
        "prompt": prompt,
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature
    }
    
    if model:
        data["model"] = model
    
    response = requests.post(url, headers=get_headers(), json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"异步请求已提交:")
        print(f"请求ID: {result['request_id']}")
        print(f"状态: {result['status']}")
        return result
    else:
        print(f"提交异步请求失败: {response.text}")
        return None

# 示例用法
if __name__ == "__main__":
    # 创建MCP客户端实例
    client = MCPClient()
    
    # 登录获取令牌
    if not client.login():
        exit(1)
    
    # 获取Claude AI配置
    config = client.get_claude_config()
    
    # 检查API是否可用
    if config and config["api_status"] == "available":
        # 基本聊天示例
        print("\n=== 基本聊天示例 ===")
        client.chat_with_claude("如何使用Docker部署一个简单的Web应用？")
        
        # 指定模型示例
        if "claude-3-haiku-20240307" in config["available_models"]:
            print("\n=== 指定模型示例 ===")
            client.chat_with_claude(
                "简要介绍Docker Compose的基本用法", 
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.5
            )
        
        # 异步聊天示例
        print("\n=== 异步聊天示例 ===")
        client.chat_with_claude_async("列出5个常用的Docker命令及其用途")
    else:
        print("Claude API不可用，请检查API密钥配置")