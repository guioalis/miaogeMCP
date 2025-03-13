# MCP服务 API 参考文档

## 目录

1. [认证](#认证)
2. [容器管理](#容器管理)
3. [Compose管理](#compose管理)
4. [Claude AI](#claude-ai)
5. [客户端示例](#客户端示例)

## 认证

所有API请求（除了登录和注册）都需要在请求头中包含有效的JWT令牌。

### 注册用户

```
POST /api/auth/register
```

**请求体**:

```json
{
  "username": "用户名",
  "password": "密码",
  "email": "邮箱（可选）",
  "full_name": "全名（可选）"
}
```

**响应**:

```json
{
  "id": "用户ID",
  "username": "用户名",
  "email": "邮箱",
  "full_name": "全名",
  "disabled": false,
  "created_at": "创建时间"
}
```

### 获取访问令牌

```
POST /api/auth/token
```

**请求体**:

```
username=用户名&password=密码
```

**响应**:

```json
{
  "access_token": "JWT令牌",
  "token_type": "bearer"
}
```

### 获取当前用户信息

```
GET /api/auth/me
```

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "id": "用户ID",
  "username": "用户名",
  "email": "邮箱",
  "full_name": "全名",
  "disabled": false,
  "created_at": "创建时间"
}
```

## 容器管理

### 获取所有容器

```
GET /api/containers/
```

**响应**:

```json
[
  {
    "id": "容器ID",
    "name": "容器名称",
    "image": "镜像名称",
    "status": "容器状态",
    "created": "创建时间",
    "ports": {"容器端口/协议": [{"HostIp": "主机IP", "HostPort": "主机端口"}]},
    "volumes": [{"source": "主机路径", "target": "容器路径", "type": "挂载类型"}],
    "environment": {"环境变量名": "环境变量值"}
  }
]
```

### 获取单个容器

```
GET /api/containers/{container_id}
```

**响应**:

```json
{
  "id": "容器ID",
  "name": "容器名称",
  "image": "镜像名称",
  "status": "容器状态",
  "created": "创建时间",
  "ports": {"容器端口/协议": [{"HostIp": "主机IP", "HostPort": "主机端口"}]},
  "volumes": [{"source": "主机路径", "target": "容器路径", "type": "挂载类型"}],
  "environment": {"环境变量名": "环境变量值"}
}
```

### 创建容器

```
POST /api/containers/create
```

**请求体**:

```json
{
  "image": "镜像名称",
  "name": "容器名称（可选）",
  "ports": {"容器端口/协议": "主机端口"},
  "volumes": {"主机路径": "容器路径"},
  "environment": {"环境变量名": "环境变量值"},
  "command": "容器启动命令（可选）"
}
```

**响应**:

```json
{
  "id": "容器ID",
  "name": "容器名称",
  "image": "镜像名称",
  "status": "容器状态",
  "created": "创建时间",
  "ports": {"容器端口/协议": [{"HostIp": "主机IP", "HostPort": "主机端口"}]},
  "volumes": [{"source": "主机路径", "target": "容器路径", "type": "挂载类型"}],
  "environment": {"环境变量名": "环境变量值"}
}
```

### 启动容器

```
POST /api/containers/{container_id}/start
```

**响应**:

```json
{
  "id": "容器ID",
  "name": "容器名称",
  "image": "镜像名称",
  "status": "running",
  "created": "创建时间",
  "ports": {"容器端口/协议": [{"HostIp": "主机IP", "HostPort": "主机端口"}]},
  "volumes": [{"source": "主机路径", "target": "容器路径", "type": "挂载类型"}],
  "environment": {"环境变量名": "环境变量值"}
}
```

### 停止容器

```
POST /api/containers/{container_id}/stop
```

**响应**:

```json
{
  "id": "容器ID",
  "name": "容器名称",
  "image": "镜像名称",
  "status": "exited",
  "created": "创建时间",
  "ports": {"容器端口/协议": [{"HostIp": "主机IP", "HostPort": "主机端口"}]},
  "volumes": [{"source": "主机路径", "target": "容器路径", "type": "挂载类型"}],
  "environment": {"环境变量名": "环境变量值"}
}
```

### 删除容器

```
DELETE /api/containers/{container_id}?force=false
```

**查询参数**:
- `force`: 是否强制删除（可选，默认为false）

**响应**:

```
204 No Content
```

### 获取容器日志

```
GET /api/containers/{container_id}/logs?tail=100
```

**查询参数**:
- `tail`: 返回的日志行数（可选，默认为100）

**响应**:

```json
{
  "logs": "容器日志内容"
}
```

## Compose管理

### 部署Compose堆栈

```
POST /api/compose/up
```

**请求体**:

```json
{
  "content": "docker-compose.yml文件内容",
  "path": "保存路径（可选）"
}
```

**响应**:

```json
{
  "status": "success",
  "message": "Compose堆栈已成功部署"
}
```

### 停止Compose堆栈

```
POST /api/compose/down
```

**请求体**:

```json
{
  "content": "docker-compose.yml文件内容",
  "path": "保存路径（可选）"
}
```

**响应**:

```json
{
  "status": "success",
  "message": "Compose堆栈已成功停止"
}
```

### 获取Compose堆栈状态

```
POST /api/compose/status
```

**请求体**:

```json
{
  "content": "docker-compose.yml文件内容",
  "path": "保存路径（可选）"
}
```

**响应**:

```json
{
  "services": {
    "服务名称": {
      "id": "容器ID",
      "status": "容器状态",
      "running": true/false
    }
  },
  "is_running": true/false
}
```

## Claude AI

### 获取Claude AI配置

```
GET /api/claude/config
```

**响应**:

```json
{
  "available_models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
  "default_model": "claude-3-opus-20240229",
  "max_tokens_limit": 4096,
  "api_status": "available"
}
```

### 与Claude AI聊天

```
POST /api/claude/chat
```

**请求体**:

```json
{
  "prompt": "用户提问内容",
  "model": "模型名称（可选，默认为claude-3-opus-20240229）",
  "max_tokens_to_sample": 1000,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40
}
```

**响应**:

```json
{
  "completion": "Claude AI的回答内容",
  "stop_reason": "停止原因",
  "model": "使用的模型名称"
}
```

### 异步与Claude AI聊天

```
POST /api/claude/chat/async
```

**请求体**:

```json
{
  "prompt": "用户提问内容",
  "model": "模型名称（可选，默认为claude-3-opus-20240229）",
  "max_tokens_to_sample": 1000,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40
}
```

**响应**:

```json
{
  "status": "processing",
  "request_id": "请求ID",
  "message": "请求已提交，正在处理中"
}
```

## 客户端示例

### Python客户端示例

在`examples/client_example.py`文件中提供了完整的Python客户端示例代码，展示了如何调用MCP服务的各个API。

基本用法示例：

```python
# 登录获取令牌
login()

# 获取Claude AI配置
config = get_claude_config()

# 与Claude AI聊天
response = chat_with_claude("如何使用Docker部署一个简单的Web应用？")

# 获取所有容器
containers = get_containers()
```

### 使用curl调用API示例

#### 1. 获取访问令牌

```bash
curl -X POST http://localhost:5000/api/auth/token \
  -d "username=admin&password=password" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

#### 2. 与Claude AI聊天

```bash
curl -X POST http://localhost:5000/api/claude/chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "如何使用Docker部署一个简单的Web应用？",
    "model": "claude-3-opus-20240229",
    "max_tokens_to_sample": 1000,
    "temperature": 0.7
  }'
```

#### 3. 获取所有容器

```bash
curl -X GET http://localhost:5000/api/containers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4. 创建容器

```bash
curl -X POST http://localhost:5000/api/containers/create \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "nginx:latest",
    "name": "mcp-nginx-example",
    "ports": {"80/tcp": "8080"}
  }'
```