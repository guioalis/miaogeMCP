import os
import docker
import yaml
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Dict, Any, Optional
from app_modules.models import ComposeFile, ComposeStatus, User
from app_modules.auth import get_current_active_user

# 创建路由器
compose_router = APIRouter()

# 创建Docker客户端
client = docker.from_env()

# 部署Compose堆栈
@compose_router.post("/up", response_model=Dict[str, Any])
async def compose_up(compose_file: ComposeFile, current_user: User = Depends(get_current_active_user)):
    try:
        # 创建临时文件保存compose内容
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as tmp:
            tmp.write(compose_file.content)
            tmp_path = tmp.name
        
        # 使用docker-compose命令部署堆栈
        project_name = f"mcp_{os.path.basename(tmp_path).split('.')[0]}"
        
        # 使用Docker SDK的API调用docker-compose
        cmd = f"docker-compose -f {tmp_path} -p {project_name} up -d"
        result = os.system(cmd)
        
        # 清理临时文件
        os.unlink(tmp_path)
        
        if result != 0:
            raise HTTPException(status_code=500, detail="部署Compose堆栈失败")
        
        return {"status": "success", "message": f"Compose堆栈 {project_name} 已成功部署"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"部署Compose堆栈错误: {str(e)}")

# 停止Compose堆栈
@compose_router.post("/down", response_model=Dict[str, Any])
async def compose_down(compose_file: ComposeFile, current_user: User = Depends(get_current_active_user)):
    try:
        # 创建临时文件保存compose内容
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as tmp:
            tmp.write(compose_file.content)
            tmp_path = tmp.name
        
        # 使用docker-compose命令停止堆栈
        project_name = f"mcp_{os.path.basename(tmp_path).split('.')[0]}"
        
        # 使用Docker SDK的API调用docker-compose
        cmd = f"docker-compose -f {tmp_path} -p {project_name} down"
        result = os.system(cmd)
        
        # 清理临时文件
        os.unlink(tmp_path)
        
        if result != 0:
            raise HTTPException(status_code=500, detail="停止Compose堆栈失败")
        
        return {"status": "success", "message": f"Compose堆栈 {project_name} 已成功停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止Compose堆栈错误: {str(e)}")

# 获取Compose堆栈状态
@compose_router.post("/status", response_model=ComposeStatus)
async def compose_status(compose_file: ComposeFile, current_user: User = Depends(get_current_active_user)):
    try:
        # 创建临时文件保存compose内容
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as tmp:
            tmp.write(compose_file.content)
            tmp_path = tmp.name
        
        # 解析compose文件获取服务名称
        compose_data = yaml.safe_load(compose_file.content)
        services = compose_data.get('services', {})
        
        # 获取所有容器
        containers = client.containers.list(all=True)
        
        # 检查每个服务的状态
        services_status = {}
        is_running = True
        
        for service_name in services.keys():
            service_containers = [c for c in containers if service_name in c.name]
            
            if service_containers:
                container = service_containers[0]
                services_status[service_name] = {
                    "id": container.id,
                    "status": container.status,
                    "running": container.status == "running"
                }
                if container.status != "running":
                    is_running = False
            else:
                services_status[service_name] = {
                    "id": None,
                    "status": "not_created",
                    "running": False
                }
                is_running = False
        
        # 清理临时文件
        os.unlink(tmp_path)
        
        return ComposeStatus(services=services_status, is_running=is_running)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Compose堆栈状态错误: {str(e)}")