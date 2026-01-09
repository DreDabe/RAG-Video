---
tags: [software/tool, yt-dlp, downloader, cli]
status: ongoing
created: {{date}}
---

# yt-dlp 命令行选项全解

## 核心命令格式
`yt-dlp [OPTIONS] URL [URL...]`

## 选项索引（按功能分类）
> **说明**：以下每个部分均可独立展开。如需查看某类别的**全部选项**，请在终端中运行对应的 `yt-dlp --help` 过滤命令。

### 1. 通用选项 (General Options)
控制程序基本行为。

| 选项 | 说明 |
| :--- | :--- |
| `-h`, `--help` | 打印此帮助文本并退出 |
| `--version` | 显示程序版本并退出 |
| `-U`, `--update` | 将程序更新到最新版 |
| `--no-update` | 即使版本过旧也不检查更新 |
| `-i`, `--ignore-errors` | 遇到下载错误时跳过，继续处理列表中的其他文件 |
| `--no-abort-on-error` | 发生错误时继续下一个下载（用于播放列表） |
| `--dump-user-agent` | 显示当前使用的 User-Agent |
| `--list-extractors` | 列出所有支持的网站（提取器） |
| `--extractor-descriptions` | 输出所有支持的网站描述 |
| … | *（此处可放置“通用选项”的完整列表，使用下方命令生成）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/General Options:/,/^[A-Z]/p' | head -n -1
```

### 2. 网络选项 (Network Options)
代理、超时、并发等设置。

| 选项 | 说明 |
| :--- | :--- |
| `--proxy URL` | 使用指定的 HTTP/HTTPS/SOCKS 代理 |
| `--socket-timeout SECONDS` | 放弃前等待数据的时间（秒） |
| `--source-address IP` | 绑定到的客户端 IP 地址 |
| `-4`, `--force-ipv4` | 所有连接强制使用 IPv4 |
| `-6`, `--force-ipv6` | 所有连接强制使用 IPv6 |
| `--enable-file-urls` | 允许下载 file:// 开头的本地文件（默认禁止） |
| … | *（此处可放置“网络选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Network Options:/,/^[A-Z]/p' | head -n -1
```

### 3. 地理限制选项 (Geo-restriction)
绕过区域封锁。

| 选项 | 说明 |
| :--- | :--- |
| `--geo-verification-proxy URL` | 用于地址验证的代理（某些网站需要） |
| `--geo-bypass` | 绕过地理限制（默认） |
| `--no-geo-bypass` | 不绕过地理限制 |
| `--geo-bypass-country CODE` | 强制假设客户端位于指定国家（两个字母的 ISO 3166-2 国家代码） |
| `--geo-bypass-ip-block IP_BLOCK` | 强制使用指定的 IP 块进行客户端 IP 验证 |
| … | *（此处可放置“地理限制选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Geo-restriction:/,/^[A-Z]/p' | head -n -1
```

### 4. 视频选择选项 (Video Selection)
从播放列表、频道中筛选视频。

| 选项 | 说明 |
| :--- | :--- |
| `--playlist-start NUMBER` | 播放列表起始序号（默认为 1） |
| `--playlist-end NUMBER` | 播放列表结束序号（默认为最后） |
| `--playlist-items ITEM_SPEC` | 下载指定序号或范围的视频（如 `1,3,5-7`） |
| `--match-title REGEX` | 仅下载标题匹配正则表达式的视频 |
| `--reject-title REGEX` | 跳过标题匹配正则表达式的视频 |
| `--min-filesize SIZE` | 跳过小于指定大小的视频（如 `50k`, `44.6M`） |
| `--max-filesize SIZE` | 跳过大干指定大小的视频 |
| … | *（此处可放置“视频选择选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Video Selection:/,/^[A-Z]/p' | head -n -1
```

### 5. 下载选项 (Download Options)
控制下载过程。

| 选项 | 说明 |
| :--- | :--- |
| `-N`, `--concurrent-fragments N` | 同时下载的视频片段数（默认为 1） |
| `-r`, `--limit-rate RATE` | 最大下载速率（如 `50K` 或 `4.2M`） |
| `-R`, `--retries RETRIES` | 重试次数（默认为 10），或 `infinite` |
| `--file-access-retries RETRIES` | 文件访问错误重试次数（默认为 3） |
| `--fragment-retries RETRIES` | 片段下载重试次数（默认为 10） |
| `--skip-unavailable-fragments` | 跳过无法下载的片段（仅对 DASH/HLS/m3u8 有效） |
| `--abort-on-unavailable-fragment` | 当某个片段无法下载时放弃整个视频 |
| `--keep-fragments` | 下载完成后保留片段文件在磁盘上 |
| … | *（此处可放置“下载选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Download Options:/,/^[A-Z]/p' | head -n -1
```

### 6. 文件系统选项 (Filesystem Options)
输出文件、路径、缓存管理。

| 选项 | 说明 |
| :--- | :--- |
| `-a`, `--batch-file FILE` | 从文件中读取 URL（每行一个），`-` 表示 stdin |
| `--no-batch-file` | 禁止从批处理文件中读取 URL |
| `-o`, `--output TEMPLATE` | **核心选项**：输出文件名模板，支持大量变量 |
| `-P`, `--paths TYPE:PATH` | 指定不同类型文件的存放路径（如 `home:~/yt-dlp`， `temp:/tmp`） |
| `--output-na-placeholder TEXT` | 模板变量不可用时的占位符（默认为 `NA`） |
| `--restrict-filenames` | 将文件名限制为 ASCII 字符，避免空格和`&$`等符号 |
| `--windows-filenames` | 确保文件名兼容 Windows（避免 `<>:"/\|?*`） |
| … | *（此处可放置“文件系统选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Filesystem Options:/,/^[A-Z]/p' | head -n -1
```

### 7. 缩略图选项 (Thumbnail Options)
| 选项 | 说明 |
| :--- | :--- |
| `--write-thumbnail` | 将缩略图写入磁盘 |
| `--write-all-thumbnails` | 下载所有可用格式的缩略图 |
| `--list-thumbnails` | 在模拟模式下列出可用缩略图 |
| … | *（此处可放置“缩略图选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Thumbnail Options:/,/^[A-Z]/p' | head -n -1
```

### 8. 详细信息和模拟选项 (Verbosity and Simulation)
调试、模拟、日志记录。

| 选项 | 说明 |
| :--- | :--- |
| `-q`, `--quiet` | 激活安静模式，抑制控制台输出 |
| `-s`, `--simulate` | **重要**：模拟下载，不实际下载任何文件 |
| `--no-simulate` | 即使之前有 `--simulate` 也强制下载 |
| `--ignore-no-formats-error` | 当未找到格式时不报错（用于测试） |
| `--skip-download` | 不下载视频/音频，但可能仍会写入元数据等 |
| `-v`, `--verbose` | 打印各种调试信息 |
| `--dump-pages` | 打印下载的页面（可能包含敏感数据） |
| `--write-pages` | 将下载的页面写入当前目录的文件中 |
| … | *（此处可放置“详细信息和模拟选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Verbosity and Simulation Options:/,/^[A-Z]/p' | head -n -1
```

### 9. 视频格式选项 (Video Format Options)
**最核心的选项之一**，控制下载何种质量、编码的视频/音频流。

| 选项 | 说明 |
| :--- | :--- |
| `-f`, `--format FORMAT` | **核心**：视频格式选择器，语法复杂而强大 |
| `-S`, `--format-sort SORTORDER` | 根据指定字段对可用格式进行排序（如 `+size`, `+br`） |
| `--format-sort-force` | 强制使用用户指定的排序规则，忽略所有其他偏好 |
| `--no-format-sort-force` | 不强制使用用户指定的排序规则（默认） |
| `--video-multistreams` | 允许多个视频流被合并到同一个文件中 |
| `--audio-multistreams` | 允许多个音频流被合并到同一个文件中 |
| `--prefer-free-formats` | 优先选择非 DASH 的免费格式（默认） |
| `--check-formats` | 在下载前检查所选格式是否实际可用 |
| … | *（此处可放置“视频格式选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Video Format Options:/,/^[A-Z]/p' | head -n -1
```

### 10. 字幕选项 (Subtitle Options)
| 选项 | 说明 |
| :--- | :--- |
| `--write-subs` | 下载字幕文件 |
| `--write-auto-subs` | 下载自动生成的字幕 |
| `--all-subs` | 下载所有可用字幕 |
| `--list-subs` | 列出所有可用字幕 |
| `--sub-format FORMAT` | 字幕格式偏好，如 `srt`/`best` |
| `--sub-langs LANGS` | 指定要下载的字幕语言（逗号分隔），`all` 表示所有 |
| … | *（此处可放置“字幕选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Subtitle Options:/,/^[A-Z]/p' | head -n -1
```

### 11. 后处理选项 (Post-processing Options)
下载后的转码、合并、嵌入等操作。

| 选项 | 说明 |
| :--- | :--- |
| `-x`, `--extract-audio` | 将视频文件转换为纯音频文件 |
| `--audio-format FORMAT` | 指定音频格式（使用 `-x` 时），如 `mp3`, `aac`, `flac` |
| `--audio-quality QUALITY` | 指定音频质量，`0`（最佳）到 `9`（最差），或比特率如 `128K` |
| `--remux-video FORMAT` | 在可能的情况下将视频重新混流到另一种容器格式（如 `mp4` -> `mkv`） |
| `--recode-video FORMAT` | 将视频重新编码为指定格式（如 `mp4`, `flv`, `avi`） |
| `--postprocessor-args NAME:ARGS` | 给后处理器传递额外参数（需要 `ffmpeg`） |
| `--embed-subs` | 将字幕嵌入视频文件（仅支持 mp4, webm, mkv） |
| `--embed-thumbnail` | 将缩略图嵌入为音频文件的封面 |
| `--embed-metadata` | 将元数据嵌入文件（默认） |
| `--embed-chapters` | 将章节信息嵌入文件（默认） |
| … | *（此处可放置“后处理选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Post-processing Options:/,/^[A-Z]/p' | head -n -1
```

### 12. 赞助区块选项 (SponsorBlock Options)
使用社区标记自动跳过视频中的赞助、 intro 等片段。

| 选项 | 说明 |
| :--- | :--- |
| `--sponsorblock-mark CATS` | 根据 SponsorBlock 信息在时间轴上标记指定类别的片段 |
| `--sponsorblock-remove CATS` | 从文件中完全移除指定类别的片段 |
| `--sponsorblock-chapter-title TITLE` | 为 SponsorBlock 章节使用的标题模板 |
| `--no-sponsorblock` | 禁用 SponsorBlock |
| `--sponsorblock-api URL` | SponsorBlock API 地址（默认为 `https://sponsor.ajay.app`） |
| … | *（此处可放置“SponsorBlock 选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/SponsorBlock Options:/,/^[A-Z]/p' | head -n -1
```

### 13. 认证选项 (Authentication Options)
| 选项 | 说明 |
| :--- | :--- |
| `-u`, `--username USERNAME` | 登录账号用户名 |
| `-p`, `--password PASSWORD` | 登录账号密码 |
| `-2`, `--twofactor TWOFACTOR` | 双重认证代码 |
| `-n`, `--netrc` | 从 `.netrc` 文件读取登录信息 |
| `--netrc-location PATH` | `.netrc` 文件路径 |
| `--video-password PASSWORD` | 视频密码（用于加密视频） |
| `--ap-mso MSO` | Adobe Pass 多系统运营商标识符 |
| `--ap-username USERNAME` | Adobe Pass 用户名 |
| `--ap-password PASSWORD` | Adobe Pass 密码 |
| … | *（此处可放置“认证选项”的完整列表）* |

**获取此类完整列表：**
```bash
yt-dlp --help | sed -n '/Authentication Options:/,/^[A-Z]/p' | head -n -1
```

### 14. 预设别名 (Preset Aliases)
将一组常用选项组合成一个短别名。

| 别名 | 等效于 |
| :--- | :--- |
| `-vU` | `--verbose --update` |
| … | *（完整列表请参考帮助文档，此处不常改动）* |

## 如何查询与使用

1.  **获取全部原始帮助**：
    ```bash
    yt-dlp --help > yt-dlp-full-help.txt
    ```

2.  **查找特定选项的精确解释**：
    ```bash
    yt-dlp --help | grep -A2 -- '--your-option'
    ```

3.  **在 Obsidian 中维护**：
    *   将本文档作为索引。
    *   当你需要深入研究某个类别（如复杂的 `-f` 格式选择器语法）时，可以创建一个新的笔记（如 `yt-dlp 格式选择详解.md`），并使用双链 `[[#^9-视频格式选项]]` 进行关联。

## 常用组合示例
- **下载最佳视频+音频并合并**：`yt-dlp -f "bestvideo+bestaudio" --merge-output-format mkv <URL>`
- **仅下载音频（MP3格式）**：`yt-dlp -x --audio-format mp3 <URL>`
- **下载播放列表并嵌入元数据**：`yt-dlp -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" --embed-metadata <PLAYLIST_URL>`



```

### **下一步建议**

这个框架是你的知识库核心。要填充任一章节的完整选项列表，只需在终端运行对应部分提供的 `sed` 命令，将输出结果粘贴到对应章节的表格下方即可。例如，要完善“通用选项”，只需执行命令，然后将结果复制到 `### 1. 通用选项` 部分。

如果你对某个特定类别（例如极其强大但也复杂的 **`-f` 格式选择器** 或 **`-o` 输出模板变量**）的详细语法和用例感兴趣，我可以为你单独生成一份更深入的解析笔记。