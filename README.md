# Digital Garden Chat

一个基于Qt和Python的智能视频知识库管理系统，支持从Bilibili等平台导入视频内容，自动转录、分析并构建知识库，通过AI对话与视频内容进行交互。

## 🌟 功能特性

### 🎯 核心功能
- **智能聊天界面**：基于Qt QML的现代化聊天界面，支持Markdown渲染
- **多对话管理**：创建、删除、重命名对话，自动保存对话历史
- **视频知识库**：从Bilibili收藏夹批量导入视频内容
- **自动转录**：使用Whisper模型自动提取视频语音内容
- **AI分析**：通过通义千问对视频内容进行深度分析
- **Dify集成**：将分析结果同步到Dify知识库，支持智能检索

### 🔧 技术特性
- **跨平台**：基于Qt的跨平台桌面应用
- **实时流式响应**：AI回复实时流式显示
- **智能视频处理**：提取关键帧、语音转文字、内容摘要
- **配置管理**：支持API密钥、平台设置等配置
- **错误处理**：完善的错误提示和异常处理

## 📋 系统要求

- **Python** 3.8+
- **Qt** 6.0+ (PySide6)
- **ffmpeg**（用于视频处理）
- **Git**（用于版本控制）

## 🚀 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/DreDabe/RAG-Video.git
cd RAG-Video
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装ffmpeg

- **Windows**：从[FFmpeg官网](https://ffmpeg.org/download.html)下载，解压后将`bin`目录添加到系统PATH
- **Linux**：`sudo apt-get install ffmpeg`
- **macOS**：`brew install ffmpeg`

### 4. 下载Whisper模型

首次运行时会自动下载Whisper small模型，或手动下载到`utils/whisper/`目录。

## ⚙️ 配置设置

### 1. Dify配置
- **API Key**：在Dify平台获取
- **Dataset ID**：创建的知识库ID
- **Base URL**：Dify API地址（默认：http://localhost/v1）

### 2. 视频平台配置
- **Bilibili**：需要登录后获取Cookie（用于访问收藏夹）

## 📖 使用指南

### 1. 基本聊天

1. 启动应用程序
2. 在聊天输入框中输入问题
3. 点击发送按钮或按Enter键
4. 查看AI的实时回复

### 2. 管理对话

- **新建对话**：点击左侧边栏的"+"按钮
- **删除对话**：右键点击对话列表中的对话，选择删除
- **重命名对话**：右键点击对话列表中的对话，选择重命名

### 3. 更新知识库

1. 点击右侧边栏的"更新知识库"按钮
2. 选择平台（如Bilibili）
3. 选择类型（如收藏夹）
4. 输入视频列表URL
5. 粘贴Cookie（可选，用于访问私有内容）
6. 点击"开始更新"按钮
7. 等待处理完成，查看日志输出

## 🔍 工作原理

### 视频处理流程
1. **视频扫描**：从平台URL获取视频列表
2. **视频下载**：使用yt-dlp下载视频文件
3. **语音提取**：使用ffmpeg提取音频
4. **语音转文字**：使用Whisper模型转录音频
5. **关键帧提取**：提取视频关键帧用于分析
6. **AI分析**：使用通义千问分析视频内容
7. **知识库同步**：将分析结果上传到Dify知识库

### 聊天流程
1. **用户输入**：接收用户消息
2. **对话管理**：保存用户消息到对话历史
3. **API调用**：向Dify发送查询请求
4. **流式响应**：实时显示AI回复
5. **结果保存**：将AI回复保存到对话历史

## 📁 项目结构

```
├── main.py              # 主入口文件
├── main.qml             # UI界面定义
├── conversation_manager.py  # 对话管理
├── knowledge_updater.py     # 知识库更新
├── dify_client.py           # Dify API客户端
├── config_manager.py        # 配置管理
├── markdown_formatter.py    # Markdown格式化
├── requirements.txt         # 依赖库列表
├── utils/                   # 工具目录
│   ├── ffmpeg/             # FFmpeg工具
│   └── whisper/            # Whisper模型
├── data/                    # 数据目录
│   ├── conversations.json  # 对话记录
│   └── bili_temp/          # 临时文件
└── doc/                     # 文档目录
```

## 🌐 外部服务

- **Dify**：知识库管理和AI对话平台
- **通义千问**：视频内容分析
- **Whisper**：语音转文字模型
- **yt-dlp**：视频下载工具
- **FFmpeg**：音视频处理工具

## 🤝 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 📞 联系我们

- **GitHub**：[DreDabe/RAG-Video](https://github.com/DreDabe/RAG-Video)
- **问题反馈**：[Issues](https://github.com/DreDabe/RAG-Video/issues)

## 🙏 致谢

- **Qt**：跨平台应用框架
- **OpenAI Whisper**：语音识别模型
- **yt-dlp**：视频下载工具
- **通义千问**：AI分析模型
- **Dify**：知识库管理平台

---

*"让知识像花园一样生长，让AI像朋友一样对话"* 🌱🤖