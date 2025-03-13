from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# 用户模型
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class UserInDB(User):
    hashed_password: str

# 令牌模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 容器模型
class ContainerCreate(BaseModel):
    image: str
    name: Optional[str] = None
    ports: Optional[Dict[str, str]] = None
    volumes: Optional[Dict[str, str]] = None
    environment: Optional[Dict[str, str]] = None
    command: Optional[str] = None

class Container(BaseModel):
    id: str
    name: str
    image: str
    status: str
    created: datetime
    ports: Optional[Dict[str, Any]] = None
    volumes: Optional[List[Dict[str, Any]]] = None
    environment: Optional[Dict[str, str]] = None

# Docker Compose模型
class ComposeFile(BaseModel):
    content: str
    path: Optional[str] = None

class ComposeStatus(BaseModel):
    services: Dict[str, Dict[str, Any]]
    is_running: bool

# Claude AI请求模型
class ClaudeRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    max_tokens_to_sample: int = 1000
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40

class ClaudeResponse(BaseModel):
    completion: str
    stop_reason: Optional[str] = None
    model: Optional[str] = None