# Dify + Python 脚本综合部署方案

## 1. 项目架构设计

### 1.1 系统架构图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Python 脚本层   │     │   中间件层       │     │    Dify 层      │
│                 │     │                 │     │                 │
│  1. 视频下载     │────▶│  1. 文件存储     │────▶│  1. 知识库管理    │
│  2. 视频处理     │     │  2. 消息队列     │     │  2. Chatflow 设计│
│  3. 文档生成     │     │  3. 调度系统     │     │  3. API 服务     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          ▲                     ▲                     ▲
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                           ┌─────────────┐
                           │   监控层     │
                           │             │
                           │ 1. 日志收集  │
                           │ 2. 监控告警  │
                           │ 3. 性能分析  │
                           └─────────────┘
```

### 1.2 核心组件说明

| 组件 | 功能 | 技术选型 |
|------|------|----------|
| 视频处理脚本 | 下载、处理视频，生成文档 | Python 3.9+、yt-dlp |
| 文件存储 | 存储视频和生成的文档 | 本地文件系统、云存储（可选） |
| 调度系统 | 定时触发脚本执行 | Airflow、Cron、云函数 |
| Dify 知识库 | 存储生成的文档 | Dify 平台 |
| Dify Chatflow | 提供对话和检索功能 | Dify 平台 |
| 监控系统 | 日志收集和监控告警 | ELK Stack、Prometheus、Grafana |

## 2. 部署方案

### 2.1 整体部署架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      部署环境                                    │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌───────────────────┐  │
│  │  Docker     │     │  Docker     │     │  Docker           │  │
│  │  容器 1      │     │  容器 2     │     │  容器 3            │  │
│  │  (视频处理)  │────▶│  (Airflow)  │────▶│  (监控系统)         │  │
│  └─────────────┘     └─────────────┘     └───────────────────┘  │
│         │                     │                     │           │
│         ▼                     ▼                     ▼           │
│  ┌─────────────┐     ┌─────────────┐     ┌───────────────────┐  │
│  │  文件存储    │     │  Dify API   │     │  日志存储         │  │
│  └─────────────┘     └─────────────┘     └───────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                 │                     │
                 ▼                     ▼
         ┌─────────────┐     ┌───────────────────┐
         │  Dify 平台   │     │  用户访问          │
         │  知识库      │     │  (Web/API)        │
         │  Chatflow   │     │                   │
         └─────────────┘     └───────────────────┘
```

### 2.2 部署步骤

#### 2.2.1 环境准备

1. **安装 Docker 和 Docker Compose**
   ```bash
   # 安装 Docker
   # Windows: 下载 Docker Desktop 安装
   # Linux: 参考 Docker 官方文档
   
   # 安装 Docker Compose
   # Docker Desktop 已包含 Docker Compose
   ```

2. **创建项目目录结构**
   ```bash
   mkdir -p video-rag-docker/{scripts,data,logs,airflow}
   cd video-rag-docker
   ```

3. **配置环境变量**
   ```bash
   # 创建 .env 文件
   touch .env
   ```

   ```env
   # Dify 配置
   DIFY_API_KEY=your-dify-api-key
   DIFY_WORKSPACE_ID=your-dify-workspace-id
   DIFY_KNOWLEDGE_BASE_ID=your-dify-knowledge-base-id
   
   # 视频处理配置
   VIDEO_SAVE_PATH=/app/data/videos
   DOC_SAVE_PATH=/app/data/docs
   COOKIE_FILE_PATH=/app/data/cookies.txt
   
   # Airflow 配置
   AIRFLOW_USERNAME=admin
   AIRFLOW_PASSWORD=admin
   
   # 监控配置
   ELK_VERSION=8.10.0
   ```

#### 2.2.2 Python 脚本部署

1. **创建视频处理脚本**
   ```bash
   # 将现有的 testv3.py 复制到 scripts 目录
   cp /path/to/testv3.py video-rag-docker/scripts/
   ```

2. **创建 Dify 集成脚本**
   ```python
   # video-rag-docker/scripts/dify_upload.py
   import os
   import requests
   import json
   
   def upload_to_dify_knowledge_base(file_path, api_key, workspace_id, knowledge_base_id):
       """将文件上传到 Dify 知识库"""
       url = f"https://api.dify.ai/v1/knowledge/{knowledge_base_id}/documents"
       
       headers = {
           "Authorization": f"Bearer {api_key}",
           "X-Workspace-ID": workspace_id
       }
       
       with open(file_path, 'rb') as f:
           files = {
               'file': (os.path.basename(file_path), f)
           }
           
           response = requests.post(url, headers=headers, files=files)
           
           if response.status_code == 200:
               return {
                   "success": True,
                   "message": "文件上传成功",
                   "data": response.json()
               }
           else:
               return {
                   "success": False,
                   "message": f"文件上传失败: {response.text}",
                   "status_code": response.status_code
               }
   
   def main():
       """主函数"""
       # 从环境变量获取配置
       api_key = os.environ.get('DIFY_API_KEY')
       workspace_id = os.environ.get('DIFY_WORKSPACE_ID')
       knowledge_base_id = os.environ.get('DIFY_KNOWLEDGE_BASE_ID')
       doc_save_path = os.environ.get('DOC_SAVE_PATH', '/app/data/docs')
       
       # 检查配置
       if not all([api_key, workspace_id, knowledge_base_id]):
           print("缺少必要的 Dify 配置")
           return False
       
       # 遍历文档目录，上传所有文档
       for filename in os.listdir(doc_save_path):
           file_path = os.path.join(doc_save_path, filename)
           if os.path.isfile(file_path):
               print(f"正在上传文件: {filename}")
               result = upload_to_dify_knowledge_base(file_path, api_key, workspace_id, knowledge_base_id)
               if result['success']:
                   print(f"文件上传成功: {filename}")
               else:
                   print(f"文件上传失败: {filename}, 错误: {result['message']}")
       
       return True
   
   if __name__ == "__main__":
       main()
   ```

3. **创建主执行脚本**
   ```python
   # video-rag-docker/scripts/main.py
   import os
   import sys
   import subprocess
   
   def run_video_download():
       """运行视频下载脚本"""
       print("开始下载视频...")
       result = subprocess.run([sys.executable, "scripts/testv3.py"], capture_output=True, text=True)
       print(f"视频下载脚本输出: {result.stdout}")
       if result.stderr:
           print(f"视频下载脚本错误: {result.stderr}")
       return result.returncode == 0
   
   def run_dify_upload():
       """运行 Dify 上传脚本"""
       print("开始上传到 Dify 知识库...")
       result = subprocess.run([sys.executable, "scripts/dify_upload.py"], capture_output=True, text=True)
       print(f"Dify 上传脚本输出: {result.stdout}")
       if result.stderr:
           print(f"Dify 上传脚本错误: {result.stderr}")
       return result.returncode == 0
   
   def main():
       """主函数"""
       try:
           # 运行视频下载
           if not run_video_download():
               print("视频下载失败")
               return 1
           
           # 运行 Dify 上传
           if not run_dify_upload():
               print("Dify 上传失败")
               return 1
           
           print("所有任务执行成功")
           return 0
           
       except Exception as e:
           print(f"执行过程中发生错误: {str(e)}")
           return 1
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

#### 2.2.3 Docker 容器化部署

1. **创建 Dockerfile**
   ```dockerfile
   # video-rag-docker/Dockerfile
   FROM python:3.9-slim
   
   # 设置工作目录
   WORKDIR /app
   
   # 安装系统依赖
   RUN apt-get update && apt-get install -y --no-install-recommends \
       curl \
       && rm -rf /var/lib/apt/lists/*
   
   # 安装 Python 依赖
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # 复制项目文件
   COPY scripts/ /app/scripts/
   
   # 创建数据目录
   RUN mkdir -p /app/data/videos /app/data/docs
   
   # 设置环境变量
   ENV PYTHONUNBUFFERED=1
   
   # 运行主脚本
   CMD ["python", "/app/scripts/main.py"]
   ```

2. **创建 requirements.txt**
```
requests
python-dotenv
flask
yt-dlp
```


3. **创建 docker-compose.yml**
   ```yaml
   # video-rag-docker/docker-compose.yml
   version: '3.8'
   
   services:
     # 视频处理服务
     video-processor:
       build: .
       container_name: video-processor
       env_file: .env
       volumes:
         - ./data:/app/data
         - ./logs:/app/logs
       restart: unless-stopped
       networks:
         - video-rag-network
     
     # Airflow 调度服务
     airflow:
       image: apache/airflow:2.6.0
       container_name: airflow
       env_file: .env
       environment:
         - AIRFLOW__CORE__LOAD_EXAMPLES=False
         - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
         - AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key
       volumes:
         - ./airflow/dags:/opt/airflow/dags
         - ./airflow/logs:/opt/airflow/logs
         - ./airflow/plugins:/opt/airflow/plugins
       depends_on:
         - postgres
       restart: unless-stopped
       networks:
         - video-rag-network
     
     # PostgreSQL 数据库（Airflow 使用）
     postgres:
       image: postgres:13
       container_name: postgres
       environment:
         - POSTGRES_USER=airflow
         - POSTGRES_PASSWORD=airflow
         - POSTGRES_DB=airflow
       volumes:
         - postgres_data:/var/lib/postgresql/data
       restart: unless-stopped
       networks:
         - video-rag-network
     
   volumes:
     postgres_data:
   
   networks:
     video-rag-network:
       driver: bridge
   ```

#### 2.2.4 Airflow 调度配置

1. **创建 Airflow DAG**
   ```python
   # video-rag-docker/airflow/dags/video_rag_dag.py
   from airflow import DAG
   from airflow.operators.bash_operator import BashOperator
   from datetime import datetime, timedelta
   
   default_args = {
       'owner': 'airflow',
       'depends_on_past': False,
       'start_date': datetime(2023, 1, 1),
       'email_on_failure': False,
       'email_on_retry': False,
       'retries': 1,
       'retry_delay': timedelta(minutes=5),
   }
   
   # 创建 DAG，每天执行一次
   dag = DAG(
       'video_rag_pipeline',
       default_args=default_args,
       description='Video RAG Pipeline: Download videos and upload to Dify',
       schedule_interval=timedelta(days=1),
   )
   
   # 定义任务
   run_video_rag = BashOperator(
       task_id='run_video_rag_pipeline',
       bash_command='docker exec video-processor python /app/scripts/main.py',
       dag=dag,
   )
   
   # 设置任务依赖
   run_video_rag
   ```

2. **初始化 Airflow**
   ```bash
   # 初始化 Airflow 数据库
   docker-compose up -d postgres
   docker-compose run --rm airflow airflow db init
   
   # 创建 Airflow 用户
   docker-compose run --rm airflow airflow users create \
     --username admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com
   ```

#### 2.2.5 Dify Chatflow 配置

1. **创建知识库**
   - 登录 Dify 控制台
   - 进入知识库管理页面
   - 创建新的知识库，记录知识库 ID
   - 配置知识库的索引和检索设置

2. **设计 Chatflow**
   - 进入 Chatflow 设计页面
   - 创建新的 Chatflow，选择 "对话机器人" 类型
   - 配置以下节点：
     1. **用户输入节点**：接收用户的提问
     2. **LLM 节点**：提取用户意图和关键词
     3. **知识库检索节点**：使用提取的关键词检索知识库
     4. **LLM 节点**：总结检索结果，生成回复
     5. **输出节点**：返回结果给用户
   - 配置节点之间的连接和条件

3. **发布 Chatflow**
   - 测试 Chatflow 的运行效果
   - 调整节点配置和提示词
   - 发布 Chatflow，获取访问链接

## 3. 监控和日志方案

### 3.1 日志收集

1. **Python 脚本日志**
   ```python
   # 在脚本中添加日志配置
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('/app/logs/video_rag.log'),
           logging.StreamHandler()
       ]
   )
   
   logger = logging.getLogger(__name__)
   ```

2. **Docker 日志**
   ```bash
   # 查看容器日志
   docker logs video-processor
   docker logs airflow
   
   # 跟踪日志
   docker logs -f video-processor
   ```

3. **Airflow 日志**
   - 访问 Airflow Web UI（http://localhost:8080）
   - 在 "DAGs" 页面查看任务执行情况
   - 点击具体任务查看详细日志

### 3.2 监控告警

1. **使用 Prometheus 和 Grafana 监控**
   ```yaml
   # 添加到 docker-compose.yml
   services:
     prometheus:
       image: prom/prometheus:v2.45.0
       container_name: prometheus
       volumes:
         - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
       ports:
         - "9090:9090"
       networks:
         - video-rag-network
     
     grafana:
       image: grafana/grafana:9.5.0
       container_name: grafana
       ports:
         - "3000:3000"
       depends_on:
         - prometheus
       networks:
         - video-rag-network
   ```

2. **配置告警规则**
   ```yaml
   # prometheus/prometheus.yml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'docker'
       static_configs:
         - targets: ['docker-exporter:9107']
   
   rule_files:
     - "alert.rules.yml"
   ```

3. **配置告警渠道**
   - 在 Grafana 中配置邮件、Slack 或企业微信告警
   - 设置告警阈值和通知规则

## 4. 自动化部署和 CI/CD

### 4.1 GitHub Actions 配置

```yaml
# .github/workflows/deploy.yml
name: Deploy Video-RAG

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # 每天凌晨执行

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_HUB_USERNAME }}
        password: ${{ secrets.DOCKER_HUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: your-docker-hub-username/video-rag:latest
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USERNAME }}
        password: ${{ secrets.SERVER_PASSWORD }}
        script: |
          cd /path/to/video-rag-docker
          docker-compose pull
          docker-compose up -d
          docker-compose logs -f --tail=50 video-processor
```

### 4.2 手动部署脚本

```bash
#!/bin/bash
# deploy.sh

echo "开始部署 Video-RAG 项目..."

# 停止现有容器
echo "停止现有容器..."
docker-compose down

# 拉取最新代码
echo "拉取最新代码..."
git pull

# 构建新镜像
echo "构建新镜像..."
docker-compose build

# 启动容器
echo "启动容器..."
docker-compose up -d

# 查看日志
echo "查看视频处理器日志..."
docker-compose logs -f --tail=100 video-processor

echo "部署完成！"
```

## 5. 安全性配置

### 5.1 敏感信息管理

1. **使用环境变量存储敏感信息**
   - 不在代码中硬编码 API 密钥、密码等
   - 使用 `.env` 文件或云服务商的密钥管理服务

2. **配置文件权限**
   ```bash
   # 设置 .env 文件权限
   chmod 600 .env
   
   # 设置密钥文件权限
   chmod 600 cookies.txt
   ```

3. **使用 Docker Secrets**
   ```yaml
   # docker-compose.yml
   services:
     video-processor:
       secrets:
         - dify_api_key
         - cookie_file
   
   secrets:
     dify_api_key:
       file: ./secrets/dify_api_key.txt
     cookie_file:
       file: ./secrets/cookies.txt
   ```

### 5.2 访问控制

1. **配置网络隔离**
   - 使用 Docker 网络隔离不同服务
   - 配置防火墙规则，只允许必要的端口访问

2. **Airflow 安全配置**
   - 使用强密码
   - 配置 HTTPS
   - 限制访问 IP

3. **Dify API 安全**
   - 限制 API 密钥的使用范围
   - 定期轮换 API 密钥
   - 监控 API 调用情况

## 6. 扩展性设计

### 6.1 模块化架构

1. **视频处理模块**
   - 支持多种视频来源（B站、YouTube 等）
   - 支持不同的视频处理算法

2. **文档生成模块**
   - 支持多种文档格式（Markdown、PDF 等）
   - 支持不同的文档生成策略

3. **知识库模块**
   - 支持多种知识库服务（Dify、Elasticsearch 等）
   - 支持不同的索引和检索算法

### 6.2 水平扩展

1. **使用 Kubernetes 部署**
   - 将 Docker 容器部署到 Kubernetes 集群
   - 配置自动扩展和负载均衡

2. **使用消息队列**
   ```yaml
   # 添加到 docker-compose.yml
   services:
     rabbitmq:
       image: rabbitmq:3.12.0-management
       container_name: rabbitmq
       ports:
         - "5672:5672"
         - "15672:15672"
       networks:
         - video-rag-network
   ```

3. **异步处理**
   - 使用 Celery 或其他任务队列处理异步任务
   - 提高系统的并发处理能力

## 7. 部署后的测试和验证

### 7.1 功能测试

1. **测试视频下载**
   ```bash
   docker exec -it video-processor python scripts/testv3.py
   ```

2. **测试 Dify 上传**
   ```bash
   docker exec -it video-processor python scripts/dify_upload.py
   ```

3. **测试完整流程**
   ```bash
   docker exec -it video-processor python scripts/main.py
   ```

4. **测试 Airflow 调度**
   - 访问 Airflow Web UI
   - 手动触发 DAG 执行
   - 查看任务执行结果

### 7.2 性能测试

1. **测试视频下载速度**
   - 下载不同大小的视频
   - 记录下载时间
   - 分析性能瓶颈

2. **测试知识库检索性能**
   - 进行多次检索请求
   - 记录响应时间
   - 分析检索效率

3. **测试系统并发能力**
   - 模拟多个用户同时访问
   - 记录系统资源使用情况
   - 分析系统的并发处理能力

## 8. 维护和更新

### 8.1 定期维护

1. **更新依赖**
   ```bash
   # 更新 Python 依赖
   pip install --upgrade yt-dlp requests
   
   # 更新 Docker 镜像
   docker-compose pull
   docker-compose up -d
   ```

2. **清理存储空间**
   ```bash
   # 清理未使用的 Docker 资源
   docker system prune -f
   
   # 清理旧视频和文档
   find ./data/videos -type f -mtime +30 -delete
   find ./data/docs -type f -mtime +30 -delete
   ```

3. **备份数据**
   ```bash
   # 备份文档和配置
   tar -czf video-rag-backup-$(date +%Y%m%d).tar.gz data/ .env
   
   # 备份到远程存储
   rsync -avz video-rag-backup-$(date +%Y%m%d).tar.gz user@remote-server:/path/to/backup/
   ```

### 8.2 日志分析

1. **分析视频下载日志**
   - 查找下载失败的视频
   - 分析失败原因
   - 优化下载策略

2. **分析检索日志**
   - 查看用户的检索请求
   - 分析检索结果的相关性
   - 优化知识库和检索算法

3. **分析系统日志**
   - 查找系统错误和异常
   - 分析系统性能瓶颈
   - 优化系统配置

## 9. 总结

本部署方案提供了一个完整的 Dify + Python 脚本综合部署解决方案，包括：

1. **系统架构设计**：清晰的三层架构，便于维护和扩展
2. **详细部署步骤**：从环境准备到应用部署的完整流程
3. **调度和监控**：使用 Airflow 进行任务调度，Prometheus 和 Grafana 进行监控
4. **安全性配置**：敏感信息管理、访问控制和网络隔离
5. **自动化部署**：CI/CD 配置，实现自动化部署
6. **扩展性设计**：模块化架构，支持水平扩展
7. **测试和验证**：功能测试和性能测试方法
8. **维护和更新**：定期维护和日志分析策略

通过这个部署方案，可以实现 Python 视频处理脚本与 Dify Chatflow 的无缝集成，构建一个稳定、可靠、可扩展的 Video-RAG 系统。