import docker
import os
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app_modules.models import Container, ContainerCreate, User
from app_modules.auth import get_current_active_user

# 创建路由器
container_router = APIRouter()

# 创建Docker客户端
client = docker.from_env()

# 将Docker容器对象转换为API模型
def convert_container(container):
    ports = {}
    if container.attrs['NetworkSettings']['Ports']:
        for port, bindings in container.attrs['NetworkSettings']['Ports'].items():
            if bindings:
                ports[port] = bindings
    
    volumes = []
    if container.attrs['Mounts']:
        for mount in container.attrs['Mounts']:
            volumes.append({
                'source': mount['Source'],
                'target': mount['Destination'],
                'type': mount['Type']
            })
    
    environment = {}
    if container.attrs['Config']['Env']:
        for env in container.attrs['Config']['Env']:
            if '=' in env:
                key, value = env.split('=', 1)
                environment[key] = value
    
    return Container(
        id=container.id,
        name=container.name,
        image=container.image.tags[0] if container.image.tags else container.image.id,
        status=container.status,
        created=container.attrs['Created'],
        ports=ports,
        volumes=volumes,
        environment=environment
    )

# 获取所有容器
@container_router.get("/", response_model=List[Container])
async def list_containers(current_user: User = Depends(get_current_active_user)):
    try:
        containers = client.containers.list(all=True)
        return [convert_container(container) for container in containers]
    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Docker API错误: {str(e)}")

# 获取单个容器
@container_router.get("/{container_id}", response_model=Container)
async def get_container(container_id: str, current_user: User = Depends(get_current_active_user)):
    try:
        container = client.containers.get(container_id)
        return convert_container(container)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="容器未找到")
    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Docker API错误: {str(e)}")

# 创建容器
@container_router.post("/create", response_model=Container, status_code=status.HTTP_201_CREATED)
async def create_container(container_data: ContainerCreate, current_user: User = Depends(get_current_active_user)):
    try:
        # 准备端口映射
        ports = {}
        if container_data.ports:
            for container_port, host_port in container_data.ports.items():
                ports[container_port] = host_port
        
        # 准备卷映射
        volumes = {}
        if container_data.volumes:
            for host_path, container_path in container_data.volumes.items():
                volumes[host_path] = {'bind': container_path, 'mode': 'rw'}
        
        # 创建容器
        container = client.containers.create(
            image=container_data.image,
            name=container_data.name,
            ports=ports,
            volumes=volumes,
            environment=container_data.environment,
            command=container_data.command
        )
        
        return convert_container(container)
    except docker.errors.ImageNotFound:
        raise HTTPException(status_code=404, detail="镜像未找到")
    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Docker API错误: {str(e)}")

# 启动容器
@container_router.post("/{container_id}/start", response_model=Container)
async def start_container(container_id: str, current_user: User = Depends(get_current_active_user)):
    try:
        container = client.containers.get(container_id)
        container.start()
        return convert_container(container)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="容器未找到")
    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Docker API错误: {str(e)}")

# 停止容器
@container_router.post("/{container_id}/stop", response_model=Container)
async def stop_container(container_id: str, current_user: User = Depends(get_current_active_user)):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return convert_container(container)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="容器未找到")
    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Docker API错误: {str(e)}")

# 删除容器
@container_router.delete("/{container_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_container(container_id: str, force: bool = False, current_user: User = Depends(get_current_active_user)):
    try:
        container = client.containers.get(container_id)
        container.remove(force=force)
        return {"detail": "容器已删除"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="容器未找到")
    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Docker API错误: {str(e)}")

# 获取容器日志
@container_router.get("/{container_id}/logs")
async def get_container_logs(container_id: str, tail: Optional[int] = 100, current_user: User = Depends(get_current_active_user)):
    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=tail, timestamps=True).decode('utf-8')
        return {"logs": logs}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="容器未找到")
    except docker.errors.APIError as e:
        raise HTTPException(status_code=500, detail=f"Docker API错误: {str(e)}")