
由于 `https://cloud.dify.ai/app/.../develop` 是 Dify 应用的内部管理界面，通常需要登录权限才能访问。作为 AI，我无法直接进入您的私有账户页面提取特定应用的私有信息。

但是，根据 Dify 平台的标准 API 文档结构（所有 Dify 应用的 API 文档在“开发”页面的结构是一致的），我为您整理了一份**标准化的 Dify API 接入指南总结**。您可以直接将其复制到 Obsidian 中使用。

---

# 📘 Dify 应用 API 接入指南 (Obsidian 模板)

> [!abstract] 简介
> 本文档基于 Dify 官方 API 标准整理，用于指导开发者将该应用（App ID: `f7b3cbae-...`）集成到外部客户端。

## 🔑 1. 认证 (Authentication)
Dify API 使用 **API Key** 进行认证。请务必在服务端调用，不要将 Key 暴露在前端代码中。

- **Header**: `Authorization: Bearer {YOUR_API_KEY}`
- **API Base URL**: `https://api.dify.ai/v1`

---

## 🚀 2. 核心 API 端点

### 2.1 发送对话消息 (Chat Messages)
用于与对话型应用进行交互。
- **POST** `/chat-messages`

**请求参数 (JSON):**
| 参数 | 类型 | 必选 | 说明 |
| :--- | :--- | :--- | :--- |
| `inputs` | object | 是 | 页面定义的变量，如 `{"name": "Dify"}` |
| `query` | string | 是 | 用户输入的具体问题 |
| `user` | string | 是 | 用户唯一标识，用于区分不同用户的对话 |
| `response_mode` | string | 否 | `streaming` (流式) 或 `blocking` (阻塞) |
| `conversation_id`| string | 否 | 继续之前的对话需传入 ID |
| `files` | array | 否 | 上传的文件列表 |

**示例代码 (cURL):**
```bash
curl -X POST 'https://api.dify.ai/v1/chat-messages' \
--header 'Authorization: Bearer {YOUR_API_KEY}' \
--header 'Content-Type: application/json' \
--data-raw '{
    "inputs": {},
    "query": "你好",
    "response_mode": "streaming",
    "conversation_id": "",
    "user": "obsidian-user-01"
}'
```

---

### 2.2 停止生成 (Stop Generation)
仅限流式模式下使用。
- **POST** `/chat-messages/:task_id/stop`

### 2.3 消息反馈 (Message Feedback)
用户对消息的点赞/点踩。
- **POST** `/messages/:message_id/feedbacks`

---

## 📁 3. 文件上传 (File Upload)
如果应用支持多模态（如识别图片），需先上传文件获取 `file_id`。
- **POST** `/files/upload`
- **Content-Type**: `multipart/form-data`

> [!warning] 限制
> 每个用户每天上传图片数量有限制，且仅支持常见图片格式（JPG, PNG, GIF等）。

---

## 🔄 4. 响应模式详解

### 🔹 流式模式 (Streaming)
服务器会持续发送 `text/event-stream` 事件。
- `event: message`: 包含回复的具体内容。
- `event: message_end`: 包含元数据（如 Token 消耗、耗时）。
- `event: error`: 出现异常时触发。

### 🔹 阻塞模式 (Blocking)
请求会保持连接直到回复生成完毕。
- 适合对实时性要求不高的自动化脚本。

---

## 🛠 5. 常见错误码

| 状态码 | 含义 | 建议 |
| :--- | :--- | :--- |
| `401` | Unauthorized | 检查 API Key 是否正确 |
| `404` | Not Found | 应用不存在或 API 地址错误 |
| `400` | Bad Request | 参数缺失或格式错误 |
| `500` | Internal Server Error | Dify 服务端异常 |

---

## 🖇 关联资源
- #Dify #API #Workflow #LLM
- [Dify 官方文档](https://docs.dify.ai)
- **App ID**: `f7b3cbae-4a86-4da7-8452-b403e3dbc0e1`

---

### 💡 Obsidian 使用技巧
1. **双向链接**: 如果你有其他关于此应用的开发日志，可以使用 `[[开发日志-2024]]` 进行关联。
2. **Dataview**: 如果你管理多个 Dify 应用，可以使用 Dataview 插件提取 `App ID` 字段。
3. **代码复制**: 点击代码块右上角即可快速复制 cURL 命令到终端测试。

---
*生成日期: 2026-01-08*

---

**建议操作：**
由于我无法看到您应用中自定义的 **`inputs` 变量**（例如您是否设置了“用户名”、“背景知识”等输入框），请您手动查看该网页左侧的 **“变量 (Variables)”** 部分，并将具体的变量名填入上述模板的 `inputs` 章节中。