# Video-RAG 项目部署指南

## 1. 项目概述

Video-RAG 是一个基于 Python 和 yt-dlp 的视频检索增强生成项目，主要功能是下载 B 站视频并进行相关处理。项目包含以下核心文件：
- `test.py`、`testv2.py`、`testv3.py`：基于 yt-dlp 的视频下载脚本
- `support-doc/`：项目文档和配置指南

## 2. 部署方式

### 2.1 本地部署

**适用场景**：开发测试、个人使用

**部署步骤**：

1. **安装依赖**
   ```bash
   # 安装 Python 3.8+（推荐 3.9 或 3.10）
   # 安装项目依赖
   pip install yt-dlp
   ```

2. **配置环境**
   ```bash
   # 创建 cookies.txt 文件（用于访问 B 站收藏夹）
   # 可以使用浏览器插件如 Get cookies.txt LOCALLY 导出 B 站 cookies
   ```

3. **运行脚本**
   ```bash
   # 运行基础版本
   python test.py
   
   # 运行支持 Dify 的版本
   python testv3.py
   ```

**优点**：
- 部署简单，无需额外配置
- 适合开发调试
- 无额外成本

**缺点**：
- 无法远程访问
- 依赖本地环境
- 不适合大规模使用

### 2.2 Docker 容器化部署

**适用场景**：生产环境、团队协作、稳定运行

**部署步骤**：

1. **创建 Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   # 设置工作目录
   WORKDIR /app
   
   # 安装依赖
   RUN pip install --no-cache-dir yt-dlp
   
   # 复制项目文件
   COPY . /app
   
   # 创建必要的目录
   RUN mkdir -p my_videos
   
   # 设置环境变量
   ENV PYTHONUNBUFFERED=1
   
   # 运行命令
   CMD ["python", "testv3.py"]
   ```

2. **创建 docker-compose.yml（可选）**
   ```yaml
   version: '3.8'
   
   services:
     video-rag:
       build: .
       container_name: video-rag
       volumes:
         - ./cookies.txt:/app/cookies.txt
         - ./my_videos:/app/my_videos
       environment:
         - PYTHONUNBUFFERED=1
       restart: unless-stopped
   ```

3. **构建和运行容器**
   ```bash
   # 构建镜像
   docker build -t video-rag .
   
   # 运行容器
   docker run -d --name video-rag -v ./cookies.txt:/app/cookies.txt -v ./my_videos:/app/my_videos video-rag
   
   # 或使用 docker-compose
   docker-compose up -d
   ```

**优点**：
- 环境隔离，避免依赖冲突
- 便于管理和扩展
- 支持自动重启
- 适合生产环境

**缺点**：
- 需要 Docker 环境
- 配置相对复杂

### 2.3 云平台部署

**适用场景**：大规模应用、高可用性要求

#### 2.3.1 腾讯云函数（SCF）

**部署步骤**：
1. 登录腾讯云函数控制台
2. 创建新函数，选择 "Python 3.9" 运行环境
3. 上传 `testv3.py` 代码
4. 添加依赖 `yt-dlp`
5. 配置触发器（API 网关或定时触发）
6. 部署并测试

#### 2.3.2 阿里云函数计算（FC）

**部署步骤**：
1. 登录阿里云函数计算控制台
2. 创建服务和函数，选择 "Python 3.9" 运行环境
3. 上传 `testv3.py` 代码
4. 配置函数入口为 `testv3.main`
5. 添加依赖 `yt-dlp`
6. 配置触发器
7. 部署并测试

#### 2.3.3 AWS Lambda

**部署步骤**：
1. 登录 AWS Lambda 控制台
2. 创建新函数，选择 "Python 3.9" 运行环境
3. 上传包含依赖的部署包（使用 Lambda Layer 或打包成 zip）
4. 配置函数入口为 `testv3.main`
5. 配置触发器（API Gateway 或 CloudWatch Events）
6. 部署并测试

**优点**：
- 高可用性和可扩展性
- 按需付费，成本低
- 无需管理服务器

**缺点**：
- 冷启动延迟
- 执行时间限制（通常 < 15分钟）
- 依赖云平台

### 2.4 Dify 集成部署

**适用场景**：作为 Dify 应用的一部分使用

**部署步骤**：

1. **配置 Dify 代码执行块**
   - 登录 Dify 控制台
   - 创建新应用或打开现有应用
   - 添加 "代码执行" 节点
   - 复制 `testv3.py` 代码到代码执行块
   - 添加依赖 `yt-dlp`
   - 配置输入输出参数

2. **配置 Dify 工作流**
   - 添加用户输入节点
   - 添加 LLM 节点用于内容提取
   - 添加知识库检索节点
   - 添加代码执行节点（Video-RAG）
   - 添加 LLM 节点用于结果总结
   - 配置输出节点

3. **测试和发布**
   - 测试工作流
   - 发布应用

**优点**：
- 无需独立部署
- 集成到 Dify 应用生态
- 支持可视化配置

**缺点**：
- 受 Dify 平台限制
- 无法独立运行

### 2.5 API 服务部署

**适用场景**：提供给其他应用调用、微服务架构

**部署步骤**：

1. **创建 API 服务**
   ```python
   # api_server.py
   from flask import Flask, request, jsonify
   import testv3
   
   app = Flask(__name__)
   
   @app.route('/api/download', methods=['POST'])
   def download_video():
       data = request.json
       url = data.get('url')
       save_path = data.get('save_path')
       return_file = data.get('return_file', False)
       
       if not url:
           return jsonify({'success': False, 'message': 'Missing URL parameter'}), 400
       
       result = testv3.download_bilibili_lowest_quality(url, save_path, return_file)
       return jsonify(result)
   
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=True)
   ```

2. **安装依赖**
   ```bash
   pip install flask yt-dlp
   ```

3. **运行 API 服务**
   ```bash
   python api_server.py
   ```

4. **使用 Gunicorn 或 uWSGI 部署**
   ```bash
   # 使用 Gunicorn（生产环境推荐）
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
   ```

5. **配置 Nginx 反向代理**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

**优点**：
- 提供标准 API 接口
- 支持多种客户端调用
- 适合微服务架构

**缺点**：
- 需要配置 Web 服务器
- 安全性需要额外考虑

## 3. 部署架构选择

| 部署方式 | 适用场景 | 优点 | 缺点 |
|----------|----------|------|------|
| 本地部署 | 开发测试 | 配置简单，成本低 | 无法远程访问，稳定性差 |
| Docker 容器化 | 生产环境 | 环境隔离，易于管理 | 需要 Docker 环境 |
| 云函数 | 大规模应用 | 高可用，按需付费 | 冷启动延迟，执行时间限制 |
| Dify 集成 | Dify 应用 | 无需独立部署，可视化配置 | 受 Dify 平台限制 |
| API 服务 | 微服务架构 | 标准 API 接口，支持多种客户端 | 需要配置 Web 服务器 |

## 4. 部署最佳实践

### 4.1 环境配置
- 使用虚拟环境或 Docker 隔离依赖
- 定期更新依赖版本
- 配置合理的超时时间

### 4.2 安全配置
- 不要在代码中硬编码敏感信息
- 使用环境变量存储配置
- 配置适当的访问权限
- 启用 HTTPS（API 服务）

### 4.3 监控和日志
- 添加详细的日志输出
- 配置日志收集和分析
- 监控系统资源使用情况
- 设置告警机制

### 4.4 扩展和优化
- 使用异步处理提高并发能力
- 优化下载和处理流程
- 考虑使用缓存减少重复下载
- 配置自动扩展机制

## 5. 常见问题排查

### 5.1 依赖安装失败
- 检查网络连接
- 使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple yt-dlp`
- 检查 Python 版本

### 5.2 视频下载失败
- 检查 B 站 cookies 是否有效
- 检查 URL 是否正确
- 检查网络连接
- 查看详细日志

### 5.3 API 服务无法访问
- 检查端口是否开放
- 检查防火墙配置
- 检查服务是否正常运行
- 查看服务日志

## 6. 部署计划示例

### 开发阶段
1. 使用本地部署进行开发和测试
2. 编写单元测试和集成测试
3. 完善文档

### 测试阶段
1. 部署到 Docker 容器进行测试
2. 进行性能测试和负载测试
3. 修复发现的问题

### 生产阶段
1. 根据需求选择合适的部署方式
2. 配置监控和日志系统
3. 设置自动扩展机制
4. 定期更新和维护

## 7. 总结

Video-RAG 项目可以通过多种方式部署，选择合适的部署方式取决于具体的使用场景和需求。对于开发测试，推荐使用本地部署或 Docker 容器化；对于生产环境，推荐使用云函数或 API 服务部署；对于 Dify 生态集成，推荐使用 Dify 集成部署。

无论选择哪种部署方式，都需要考虑环境配置、安全配置、监控和日志等方面，确保系统的稳定性和可靠性。