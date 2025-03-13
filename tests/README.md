# MCP服务测试指南

## 测试概述

本目录包含MCP服务的自动化测试套件，使用pytest框架实现。测试覆盖了以下模块：

- 基本应用功能（根路由和健康检查）
- 用户认证（注册、登录、获取用户信息）
- 容器管理（列表、获取、创建容器）
- Compose管理（部署、停止、状态查询）
- Claude AI集成（配置获取、聊天功能）

## 运行测试

### 安装依赖

首先确保已安装所有测试依赖：

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### 运行所有测试

在项目根目录执行以下命令运行所有测试：

```bash
pytest
```

### 运行特定测试模块

```bash
pytest tests/test_app.py
pytest tests/test_auth.py
pytest tests/test_containers.py
pytest tests/test_compose.py
pytest tests/test_claude.py
```

### 生成测试覆盖率报告

```bash
pytest --cov=app_modules tests/
```

## 测试结构

- `conftest.py`: 包含共享的测试fixture和配置
- `test_app.py`: 测试基本应用功能
- `test_auth.py`: 测试用户认证功能
- `test_containers.py`: 测试容器管理功能
- `test_compose.py`: 测试Compose管理功能
- `test_claude.py`: 测试Claude AI集成功能

## 注意事项

- 测试使用mock模拟Docker客户端和Anthropic API，不需要实际的Docker环境或API密钥
- 测试数据库使用内存中的字典，不需要实际的数据库连接
- 确保在运行测试前已设置好所有必要的环境变量（可选）