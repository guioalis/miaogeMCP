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

# 获取所有容器
def get_containers():
    url = f"{BASE_URL}/containers/"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code == 200:
        containers = response.json()
        print(f"获取到 {len(containers)} 个容器:")
        for container in containers:
            print(f"  - {container['name']} ({container['id'][:12]}): {container['status']}")
        return containers
    else:
        print(f"获取容器失败: {response.text}")
        return []

# 创建新容器
def create_container(image, name=None, ports=None, volumes=None, environment=None, command=None):
    url = f"{BASE_URL}/containers/create"
    data = {
        "image": image,
        "name": name,
        "ports": ports,
        "volumes": volumes,
        "environment": environment,
        "command": command
    }
    
    # 移除None值
    data = {k: v for k, v in data.items() if v is not None}
    
    response = requests.post(url, headers=get_headers(), json=data)
    
    if response.status_code == 201:
        container = response.json()
        print(f"容器创建成功: {container['name']} ({container['id'][:12]})")
        return container
    else:
        print(f"创建容器失败: {response.text}")
        return None

# 启动容器
def start_container(container_id):
    url = f"{BASE_URL}/containers/{container_id}/start"
    response = requests.post(url, headers=get_headers())
    
    if response.status_code == 200:
        container = response.json()
        print(f"容器启动成功: {container['name']} ({container['id'][:12]})")
        return container
    else:
        print(f"启动容器失败: {response.text}")
        return None

# 停止容器
def stop_container(container_id):
    url = f"{BASE_URL}/containers/{container_id}/stop"
    response = requests.post(url, headers=get_headers())
    
    if response.status_code == 200:
        container = response.json()
        print(f"容器停止成功: {container['name']} ({container['id'][:12]})")
        return container
    else:
        print(f"停止容器失败: {response.text}")
        return None

# 删除容器
def delete_container(container_id, force=False):
    url = f"{BASE_URL}/containers/{container_id}?force={str(force).lower()}"
    response = requests.delete(url, headers=get_headers())
    
    if response.status_code == 204:
        print(f"容器删除成功: {container_id}")
        return True
    else:
        print(f"删除容器失败: {response.text}")
        return False

# 部署Compose堆栈
def deploy_compose(compose_content):
    url = f"{BASE_URL}/compose/up"
    data = {
        "content": compose_content
    }
    
    response = requests.post(url, headers=get_headers(), json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Compose堆栈部署成功: {result['message']}")
        return result
    else:
        print(f"部署Compose堆栈失败: {response.text}")
        return None

# 停止Compose堆栈
def stop_compose(compose_content):
    url = f"{BASE_URL}/compose/down"
    data = {
        "content": compose_content
    }
    
    response = requests.post(url, headers=get_headers(), json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Compose堆栈停止成功: {result['message']}")
        return result
    else:
        print(f"停止Compose堆栈失败: {response.text}")
        return None

# 获取Compose堆栈状态
def get_compose_status(compose_content):
    url = f"{BASE_URL}/compose/status"
    data = {
        "content": compose_content
    }
    
    response = requests.post(url, headers=get_headers(), json=data)
    
    if response.status_code == 200:
        status = response.json()
        print(f"Compose堆栈状态: {'运行中' if status['is_running'] else '未运行'}")
        for service, info in status['services'].items():
            print(f"  - {service}: {info['status']}")
        return status
    else:
        print(f"获取Compose堆栈状态失败: {response.text}")
        return None

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
    client.get_claude_config()
    
    # 与Claude AI聊天
    client.chat_with_claude("如何使用Docker部署一个简单的Web应用？")
    
    # 获取所有容器
    containers = client.get_containers()
    
    # 创建一个Nginx容器示例
    # container = client.create_container(
    #     image="nginx:latest",
    #     name="mcp-nginx-example",
    #     ports={"80/tcp": "8080"}
    # )
    # 
    # if container:
    #     # 启动容器
    #     client.start_container(container['id'])
    #     
    #     # 停止容器
    #     client.stop_container(container['id'])
    #     
    #     # 删除容器
    #     client.delete_container(container['id'])
    
    # Compose示例
    # compose_content = """
    # version: '3'
    # services:
    #   web:
    #     image: nginx:latest
    #     ports:
    #       - "8080:80"
    #   db:
    #     image: postgres:latest
    #     environment:
    #       POSTGRES_PASSWORD: example
    # """
    # 
    # # 部署Compose堆栈
    # client.deploy_compose(compose_content)
    # 
    # # 获取Compose堆栈状态
    # client.get_compose_status(compose_content)
    # 
    # # 停止Compose堆栈
    # client.stop_compose(compose_content)