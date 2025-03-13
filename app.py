import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app_modules.auth import auth_router, get_current_user
from app_modules.containers import container_router
from app_modules.compose import compose_router
from app_modules.claude import claude_router
from app_modules.models import User

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="喵哥docker（MCP）服务",
    description="一个用于Docker操作的强大模型上下文协议(MCP)服务器",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(container_router, prefix="/api/containers", tags=["容器管理"], dependencies=[Depends(get_current_user)])
app.include_router(compose_router, prefix="/api/compose", tags=["Compose管理"], dependencies=[Depends(get_current_user)])
app.include_router(claude_router, prefix="/api/claude", tags=["Claude AI"], dependencies=[Depends(get_current_user)])

@app.get("/", tags=["根"])
async def root():
    return {"message": "欢迎使用喵哥docker（MCP）服务！"}

@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run("app:app", host=host, port=port, reload=debug)