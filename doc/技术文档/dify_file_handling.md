# Dify 代码执行块文件处理指南

## 1. Dify 环境限制说明

### 1.1 沙箱环境限制
Dify 的代码执行块运行在**沙箱环境**中，具有以下限制：
- 无法直接访问本地文件系统
- 无法持久化存储文件（执行完成后沙箱会被销毁）
- 文件大小限制（通常 < 100MB）
- 执行时间限制（通常 < 1小时）

### 1.2 可用的文件处理方式

| 方式 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| Base64 编码返回 | 小文件 (< 10MB) | 直接返回文件内容，无需外部存储 | 文件大小受限，编码耗时 |
| 上传到云存储 | 大文件 (> 10MB) | 支持大文件，持久化存储 | 需要配置云存储账号，额外成本 |
| 生成下载链接 | 所有文件 | 无需本地存储，直接访问 | 依赖外部服务，链接有有效期 |
| 发送到 Webhook | 实时处理 | 实时推送文件到指定服务 | 需要接收端服务支持 |

## 2. testv3.py 功能说明

### 2.1 新增功能
- 支持临时目录保存视频
- 支持 Base64 编码返回视频内容
- 支持文件大小检查和限制
- 支持返回视频元数据

### 2.2 输入参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| url | 字符串 | - | 要下载的B站视频或收藏夹URL |
| save_path | 字符串 | None | 视频保存路径（None时使用临时目录） |
| return_file | 布尔值 | False | 是否返回Base64编码的视频内容 |

### 2.3 输出结果

| 输出字段 | 类型 | 说明 |
|----------|------|------|
| success | 布尔值 | 下载是否成功 |
| message | 字符串 | 执行结果消息 |
| url | 字符串 | 下载的视频URL |
| save_path | 字符串 | 实际保存路径 |
| video_title | 字符串 | 视频标题 |
| video_ext | 字符串 | 视频扩展名 |
| video_filename | 字符串 | 视频文件名 |
| video_content_base64 | 字符串 | Base64编码的视频内容（仅当return_file=True时） |
| file_size | 整数 | 文件大小（字节） |
| file_too_large | 布尔值 | 文件是否过大 |
| file_error | 字符串 | 文件处理错误信息 |

## 3. 配置步骤

### 3.1 基本配置
1. 将 `testv3.py` 中的完整代码复制到 Dify 代码执行块中
2. 在依赖部分添加：
   ```
   yt-dlp
   ```
3. 设置超时时间：3600秒（1小时）
4. 设置内存限制：512MB 或更高

### 3.2 小文件处理配置（Base64 返回）

#### 3.2.1 输入配置
| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| url | 字符串 | - | 要下载的B站视频URL |
| return_file | 布尔值 | True | 返回Base64编码的视频内容 |

#### 3.2.2 输出配置
设置输出格式为 JSON，用于接收 Base64 编码的视频内容：

| 输出字段 | 类型 | 说明 |
|----------|------|------|
| success | 布尔值 | 下载是否成功 |
| message | 字符串 | 执行结果消息 |
| video_title | 字符串 | 视频标题 |
| video_ext | 字符串 | 视频扩展名 |
| video_content_base64 | 字符串 | Base64编码的视频内容 |

#### 3.2.3 前端处理代码
```javascript
// 假设从Dify API获取到的结果为response
const result = response.data;
if (result.success && result.video_content_base64) {
    // 将Base64字符串转换为Blob对象
    const binaryString = atob(result.video_content_base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: `video/${result.video_ext}` });
    
    // 创建下载链接
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${result.video_title}.${result.video_ext}`;
    document.body.appendChild(a);
    a.click();
    
    // 清理
    setTimeout(() => {
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }, 100);
}
```

### 3.3 大文件处理配置（云存储上传）

#### 3.3.1 支持的云存储服务
- **腾讯云 COS**
- **阿里云 OSS**
- **AWS S3**
- **七牛云**
- **GitHub Releases**

#### 3.3.2 腾讯云 COS 配置示例

1. **安装依赖**
在代码执行块的依赖部分添加：
```
cos-python-sdk-v5
yt-dlp
```

2. **修改代码**
在 `testv3.py` 中添加 COS 上传功能：

```python
# 添加COS上传功能
def upload_to_cos(file_path, bucket, region, secret_id, secret_key):
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client
    
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    
    # 上传文件
    file_name = os.path.basename(file_path)
    response = client.upload_file(
        Bucket=bucket,
        LocalFilePath=file_path,
        Key=file_name,
        PartSize=1,
        MAXThread=10,
        EnableMD5=False
    )
    
    # 生成下载链接（有效期1小时）
    download_url = client.get_presigned_download_url(
        Bucket=bucket,
        Key=file_name,
        Expired=3600
    )
    
    return download_url
```

3. **输入配置**
| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| url | 字符串 | - | 要下载的B站视频URL |
| cos_bucket | 字符串 | - | COS存储桶名称 |
| cos_region | 字符串 | - | COS区域（如ap-beijing） |
| cos_secret_id | 字符串 | - | COS SecretId |
| cos_secret_key | 字符串 | - | COS SecretKey |

### 3.4 生成下载链接配置

#### 3.4.1 使用 transfer.sh 服务

```python
# 添加transfer.sh上传功能
def upload_to_transfer_sh(file_path):
    import requests
    
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://transfer.sh/',
            files={'file': f}
        )
    
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception(f"上传失败: {response.text}")
```

## 4. 本地保存视频的完整流程

### 4.1 方案一：使用 Base64 编码返回（推荐）

1. **配置 Dify 代码执行块**
   - 代码：使用 `testv3.py` 完整代码
   - 依赖：`yt-dlp`
   - 输入：`url`, `return_file=True`
   - 输出：JSON 格式，包含 `video_content_base64`

2. **创建前端应用**
   - 使用 Dify API 调用代码执行块
   - 接收 Base64 编码的视频内容
   - 将 Base64 转换为 Blob 对象
   - 创建下载链接，触发浏览器下载

3. **示例前端代码**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>B站视频下载工具</title>
</head>
<body>
    <h1>B站视频下载工具</h1>
    <input type="text" id="videoUrl" placeholder="输入B站视频URL">
    <button onclick="downloadVideo()">下载视频</button>
    <div id="result"></div>
    
    <script>
        async function downloadVideo() {
            const url = document.getElementById('videoUrl').value;
            const resultDiv = document.getElementById('result');
            
            resultDiv.innerHTML = '正在下载...';
            
            try {
                // 调用Dify API
                const response = await fetch('https://api.dify.ai/v1/workflows/run', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer YOUR_DIFY_API_KEY'
                    },
                    body: JSON.stringify({
                        workflow_id: 'YOUR_WORKFLOW_ID',
                        inputs: {
                            url: url,
                            return_file: true
                        }
                    })
                });
                
                const data = await response.json();
                const result = data.data.outputs;
                
                if (result.success) {
                    resultDiv.innerHTML = '下载成功，正在处理文件...';
                    
                    // 将Base64转换为Blob并下载
                    const binaryString = atob(result.video_content_base64);
                    const bytes = new Uint8Array(binaryString.length);
                    for (let i = 0; i < binaryString.length; i++) {
                        bytes[i] = binaryString.charCodeAt(i);
                    }
                    const blob = new Blob([bytes], { type: `video/${result.video_ext}` });
                    
                    const downloadUrl = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = downloadUrl;
                    a.download = `${result.video_title}.${result.video_ext}`;
                    document.body.appendChild(a);
                    a.click();
                    
                    setTimeout(() => {
                        URL.revokeObjectURL(downloadUrl);
                        document.body.removeChild(a);
                        resultDiv.innerHTML = '视频已下载完成！';
                    }, 100);
                } else {
                    resultDiv.innerHTML = `下载失败：${result.message}`;
                }
            } catch (error) {
                resultDiv.innerHTML = `请求失败：${error.message}`;
            }
        }
    </script>
</body>
</html>
```

### 4.2 方案二：使用云存储中转

1. **配置云存储**
   - 注册云存储服务（如腾讯云COS、阿里云OSS）
   - 创建存储桶，设置公共读权限
   - 获取API密钥

2. **修改代码**
   - 在 `testv3.py` 中添加云存储上传功能
   - 配置云存储参数
   - 执行完成后返回下载链接

3. **用户下载流程**
   - 用户输入视频URL
   - Dify代码执行块下载视频
   - 上传到云存储
   - 返回云存储下载链接
   - 用户点击链接下载到本地

## 5. 最佳实践

### 5.1 文件大小优化
- 使用最低画质下载（已在代码中配置）
- 限制单个视频大小（建议 < 50MB）
- 对大文件使用云存储方案

### 5.2 性能优化
- 使用异步下载和上传
- 合理设置超时时间
- 优化Base64编码过程

### 5.3 错误处理
- 添加详细的日志输出
- 处理网络超时情况
- 处理文件上传失败情况
- 提供清晰的错误信息

### 5.4 安全建议
- 不要在代码中硬编码API密钥
- 使用环境变量存储敏感信息
- 限制云存储的访问权限
- 定期轮换API密钥

## 6. 常见问题排查

### 6.1 视频下载失败
- 检查URL是否正确
- 检查B站Cookies是否有效
- 检查网络连接

### 6.2 Base64编码过大
- 降低视频画质
- 分割大文件
- 改用云存储方案

### 6.3 云存储上传失败
- 检查API密钥是否正确
- 检查存储桶权限设置
- 检查网络连接

### 6.4 前端下载失败
- 检查浏览器兼容性
- 检查文件大小限制
- 检查Base64编码是否完整

## 7. 示例工作流

1. **用户输入**：用户发送B站视频URL
2. **变量提取**：从消息中提取视频URL
3. **代码执行块**：
   - 下载B站视频
   - 转换为Base64编码
   - 返回视频内容和元数据
4. **结果处理**：生成下载链接或直接返回文件
5. **返回给用户**：将下载链接或文件提供给用户

## 8. 总结

在Dify环境中处理文件需要考虑沙箱限制，根据文件大小选择合适的处理方式：
- 小文件：使用Base64编码直接返回
- 大文件：使用云存储中转
- 所有文件：生成临时下载链接

通过合理配置和优化，可以在Dify环境中实现高效的视频下载和文件处理功能。