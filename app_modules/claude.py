import os
import json
import logging
import anthropic
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any, List, Optional
from app_modules.models import ClaudeRequest, ClaudeResponse, User
from app_modules.auth import get_current_active_user
import docker
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claude_api")

# 创建路由器
claude_router = APIRouter()

# 获取Claude API密钥
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# 创建Docker客户端
docker_client = docker.from_env()

# 可用的Claude模型
AVAILABLE_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
]

# 默认模型
DEFAULT_MODEL = "claude-3-opus-20240229"

# 系统提示词
SYSTEM_PROMPT = """
你是一个专门用于Docker操作的AI助手。你可以帮助用户管理Docker容器和Docker Compose堆栈。

你可以执行以下操作：
1. 创建和管理Docker容器
2. 部署和管理Docker Compose堆栈
3. 查询容器状态和日志
4. 提供Docker相关的技术支持和建议

请根据用户的自然语言请求，生成相应的Docker命令或操作步骤。
"""

# 获取Docker环境信息
def get_docker_context():
    try:
        # 获取当前Docker环境信息
        containers = docker_client.containers.list(all=True)
        container_info = [{
            "id": container.id[:12],
            "name": container.name,
            "image": container.image.tags[0] if container.image.tags else container.image.id,
            "status": container.status
        } for container in containers]
        
        # 获取Docker镜像信息
        images = docker_client.images.list()
        image_info = [{
            "id": image.id[:12],
            "tags": image.tags,
            "size": image.attrs["Size"] // (1024 * 1024)  # 转换为MB
        } for image in images]
        
        # 构建上下文信息
        context = {
            "containers": container_info,
            "images": image_info,
            "timestamp": str(datetime.now())
        }
        
        return context
    except Exception as e:
        logger.error(f"获取Docker环境信息失败: {str(e)}")
        return {"error": str(e), "timestamp": str(datetime.now())}

# 获取API配置信息
@claude_router.get("/config", response_model=Dict[str, Any])
async def get_claude_config(current_user: User = Depends(get_current_active_user)):
    return {
        "available_models": AVAILABLE_MODELS,
        "default_model": DEFAULT_MODEL,
        "max_tokens_limit": 4096,
        "api_status": "available" if ANTHROPIC_API_KEY else "unavailable"
    }

# 与Claude AI交互
@claude_router.post("/chat", response_model=ClaudeResponse)
async def chat_with_claude(request: ClaudeRequest, current_user: User = Depends(get_current_active_user)):
    if not ANTHROPIC_API_KEY:
        logger.error("Claude API密钥未配置")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Claude API密钥未配置")
    
    try:
        # 获取Docker环境上下文
        context = get_docker_context()
        
        # 记录请求信息
        logger.info(f"用户 {current_user.username} 发送请求: {request.prompt[:50]}...")
        
        # 调用Claude API
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # 使用请求中指定的模型，如果未指定则使用默认模型
        model = request.model if hasattr(request, 'model') and request.model in AVAILABLE_MODELS else DEFAULT_MODEL
        
        message = client.messages.create(
            model=model,
            max_tokens=request.max_tokens_to_sample,
            temperature=request.temperature,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"当前Docker环境信息:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\n{request.prompt}"
                }
            ]
        )
        
        # 记录响应信息
        logger.info(f"Claude响应: {message.content[0].text[:50]}...")
        
        return ClaudeResponse(
            completion=message.content[0].text,
            stop_reason=message.stop_reason,
            model=message.model
        )
    except anthropic.APIError as e:
        logger.error(f"Claude API错误: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Claude API错误: {str(e)}")
    except anthropic.APIConnectionError as e:
        logger.error(f"Claude API连接错误: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Claude API连接错误: {str(e)}")
    except anthropic.RateLimitError as e:
        logger.error(f"Claude API速率限制错误: {str(e)}")
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Claude API速率限制错误: {str(e)}")
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"处理请求时发生错误: {str(e)}")

# 异步与Claude AI交互
@claude_router.post("/chat/async", response_model=Dict[str, Any])
async def chat_with_claude_async(request: ClaudeRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_active_user)):
    if not ANTHROPIC_API_KEY:
        logger.error("Claude API密钥未配置")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Claude API密钥未配置")
    
    # 生成请求ID
    request_id = f"{current_user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(request.prompt)%1000}"
    
    # 添加到后台任务
    background_tasks.add_task(process_claude_request, request, request_id, current_user)
    
    return {
        "status": "processing",
        "request_id": request_id,
        "message": "请求已提交，正在处理中"
    }

# 后台处理Claude请求
async def process_claude_request(request: ClaudeRequest, request_id: str, current_user: User):
    try:
        # 获取Docker环境上下文
        context = get_docker_context()
        
        # 记录请求信息
        logger.info(f"异步处理用户 {current_user.username} 的请求 {request_id}: {request.prompt[:50]}...")
        
        # 调用Claude API
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # 使用请求中指定的模型，如果未指定则使用默认模型
        model = request.model if hasattr(request, 'model') and request.model in AVAILABLE_MODELS else DEFAULT_MODEL
        
        message = client.messages.create(
            model=model,
            max_tokens=request.max_tokens_to_sample,
            temperature=request.temperature,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"当前Docker环境信息:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\n{request.prompt}"
                }
            ]
        )
        
        # 记录响应信息
        logger.info(f"请求 {request_id} 的Claude响应: {message.content[0].text[:50]}...")
        
        # 这里可以将结果保存到数据库或缓存中，供后续查询
        # 实际项目中应该实现结果存储和查询机制
        
    except Exception as e:
        logger.error(f"处理异步请求 {request_id} 时发生错误: {str(e)}")