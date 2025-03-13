# 喵哥docker（MCP）服务
一个用于Docker操作的强大模型上下文协议(MCP)服务器，通过Claude AI实现无缝容器和组合堆栈管理。

特点
容器创建和实例化
Docker Compose堆栈部署
容器日志检索
容器列表和状态监控

安装

前提条件
Python 3.8+
Docker
Docker Compose

安装步骤

克隆仓库

git clone https://github.com/guioalis/miaogeMCP.git

cd miaogeMCP

安装依赖

pip install -r requirements.txt

配置环境变量

创建一个.env文件并设置必要的环境变量：

plaintext
API_KEY=your_claude_api_key
SECRET_KEY=your_secret_key

使用方法

启动服务

python app.py


服务将在http://localhost:5000上运行。

API端点

容器管理
POST /api/containers/create - 创建新容器
GET /api/containers - 列出所有容器
GET /api/containers/{id} - 获取容器详情
POST /api/containers/{id}/start - 启动容器
POST /api/containers/{id}/stop - 停止容器
DELETE /api/containers/{id} - 删除容器
GET /api/containers/{id}/logs - 获取容器日志
Docker Compose管理
POST /api/compose/up - 部署Compose堆栈
POST /api/compose/down - 停止Compose堆栈
GET /api/compose/status - 获取Compose堆栈状态
与Claude AI集成

本服务集成了Claude AI，可以通过自然语言处理来执行Docker操作。例如：

"创建一个运行Nginx的容器"
"显示所有正在运行的容器"
"部署我的Web应用堆栈"

许可证
MIT
