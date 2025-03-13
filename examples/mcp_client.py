import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MCPClient:
    """
    MCP服务的基础客户端类，提供通用的API调用功能
    """
    def __init__(self, base_url=None, username=None, password=None):
        # 服务器配置
        self.base_url = base_url or "http://localhost:5000/api"
        
        # 用户凭据
        self.username = username or os.getenv("MCP_USERNAME", "admin")
        self.password = password or os.getenv("MCP_PASSWORD", "password")
        
        # 存储访问令牌
        self.access_token = None
    
    def login(self):
        """
        登录并获取令牌
        """
        url = f"{self.base_url}/auth/token"
        data = {
            "username": self.username,
            "password": self.password
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result["access_token"]
            print(f"登录成功，获取令牌: {self.access_token[:10]}...")
            return True
        else:
            print(f"登录失败: {response.text}")
            return False
    
    def get_headers(self):
        """
        获取请求头（包含认证信息）
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_containers(self):
        """
        获取所有容器
        """
        url = f"{self.base_url}/containers/"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            containers = response.json()
            print(f"获取到 {len(containers)} 个容器:")
            for container in containers:
                print(f"  - {container['name']} ({container['id'][:12]}): {container['status']}")
            return containers
        else:
            print(f"获取容器失败: {response.text}")
            return []
    
    def create_container(self, image, name=None, ports=None, volumes=None, environment=None, command=None):
        """
        创建新容器
        """
        url = f"{self.base_url}/containers/create"
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
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        
        if response.status_code == 201:
            container = response.json()
            print(f"容器创建成功: {container['name']} ({container['id'][:12]})")
            return container
        else:
            print(f"创建容器失败: {response.text}")
            return None
    
    def start_container(self, container_id):
        """
        启动容器
        """
        url = f"{self.base_url}/containers/{container_id}/start"
        response = requests.post(url, headers=self.get_headers())
        
        if response.status_code == 200:
            container = response.json()
            print(f"容器启动成功: {container['name']} ({container['id'][:12]})")
            return container
        else:
            print(f"启动容器失败: {response.text}")
            return None
    
    def stop_container(self, container_id):
        """
        停止容器
        """
        url = f"{self.base_url}/containers/{container_id}/stop"
        response = requests.post(url, headers=self.get_headers())
        
        if response.status_code == 200:
            container = response.json()
            print(f"容器停止成功: {container['name']} ({container['id'][:12]})")
            return container
        else:
            print(f"停止容器失败: {response.text}")
            return None
    
    def delete_container(self, container_id, force=False):
        """
        删除容器
        """
        url = f"{self.base_url}/containers/{container_id}?force={str(force).lower()}"
        response = requests.delete(url, headers=self.get_headers())
        
        if response.status_code == 204:
            print(f"容器删除成功: {container_id}")
            return True
        else:
            print(f"删除容器失败: {response.text}")
            return False
    
    def deploy_compose(self, compose_content):
        """
        部署Compose堆栈
        """
        url = f"{self.base_url}/compose/up"
        data = {
            "content": compose_content
        }
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Compose堆栈部署成功: {result['message']}")
            return result
        else:
            print(f"部署Compose堆栈失败: {response.text}")
            return None
    
    def stop_compose(self, compose_content):
        """
        停止Compose堆栈
        """
        url = f"{self.base_url}/compose/down"
        data = {
            "content": compose_content
        }
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Compose堆栈停止成功: {result['message']}")
            return result
        else:
            print(f"停止Compose堆栈失败: {response.text}")
            return None
    
    def get_compose_status(self, compose_content):
        """
        获取Compose堆栈状态
        """
        url = f"{self.base_url}/compose/status"
        data = {
            "content": compose_content
        }
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        
        if response.status_code == 200:
            status = response.json()
            print(f"Compose堆栈状态: {'运行中' if status['is_running'] else '未运行'}")
            for service, info in status['services'].items():
                print(f"  - {service}: {info['status']}")
            return status
        else:
            print(f"获取Compose堆栈状态失败: {response.text}")
            return None
    
    def get_claude_config(self):
        """
        获取Claude AI配置
        """
        url = f"{self.base_url}/claude/config"
        response = requests.get(url, headers=self.get_headers())
        
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
    
    def chat_with_claude(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        """
        与Claude AI聊天
        """
        url = f"{self.base_url}/claude/chat"
        data = {
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature
        }
        
        if model:
            data["model"] = model
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        
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
    
    def chat_with_claude_async(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        """
        异步与Claude AI聊天
        """
        url = f"{self.base_url}/claude/chat/async"
        data = {
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature
        }
        
        if model:
            data["model"] = model
        
        response = requests.post(url, headers=self.get_headers(), json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"异步请求已提交:")
            print(f"请求ID: {result['request_id']}")
            print(f"状态: {result['status']}")
            return result
        else:
            print(f"提交异步请求失败: {response.text}")
            return None