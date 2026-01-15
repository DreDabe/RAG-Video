import os
import threading
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot
import subprocess
import requests
import yt_dlp
from faster_whisper import WhisperModel
from config.platform_config import get_platform_config, is_type_supported
from config.model_config import get_model_config
from cookie_parser import detect_cookie_format, normalize_cookie, get_cookie_format_name


class BasePlatformHandler:
    """平台处理器基类"""
    
    def __init__(self, config_manager, log_callback, temp_dir, archive_file, cookies_file, whisper_model):
        self.config_manager = config_manager
        self.log = log_callback
        self.temp_dir = temp_dir
        self.archive_file = archive_file
        self.cookies_file = cookies_file
        self.whisper_model = whisper_model
        self.should_stop = False
    
    def process(self, url, cookie_text):
        """处理入口方法"""
        raise NotImplementedError("子类必须实现 process 方法")

    def _log(self, message):
        """记录日志"""
        self.log(message)


class BilibiliPlaylistHandler(BasePlatformHandler):
    """Bilibili收藏夹处理器"""
    
    def process(self, url, cookie_text):
        """处理Bilibili收藏夹"""
        self._log("[*] 正在扫描播放列表...")
        
        ydl_opts = {
            'cookiefile': str(self.cookies_file) if cookie_text else None,
            'extract_flat': True,
            'quiet': True
        }
        
        if cookie_text:
            self._save_cookie(cookie_text, url)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(url, download=False)
                entries = playlist_info.get('entries', [])
            
            if not entries:
                self._log("[-] 播放列表为空")
                return
            
            self._log(f"[√] 找到 {len(entries)} 个视频")
            
            total = len(entries)
            for idx, entry in enumerate(entries, 1):
                # 检查是否应该停止
                if self.should_stop:
                    self._log("[!] 任务已停止")
                    break
                
                if not entry:
                    continue
                
                v_id = entry.get('id')
                v_url = f"https://www.bilibili.com/video/{v_id}"
                
                if self._is_processed(v_id):
                    self._log(f"[{idx}/{total}] 已处理过，跳过: {v_id}")
                    continue
                
                self._log(f"\n[{idx}/{total}] 正在处理视频 ID: {v_id}")
                self._process_single_video(v_url, v_id, cookie_text)
                
        except Exception as e:
            self._log(f"[-] 扫描播放列表失败: {e}")
    
    def _process_single_video(self, video_url, video_id, cookie_text):
        """处理单个视频"""
        try:
            # 检查是否应该停止
            if self.should_stop:
                self._log("[!] 任务已停止")
                return
            
            dl_opts = {
                'cookiefile': str(self.cookies_file) if cookie_text else None,
                'format': 'worstvideo[height<=360]+bestaudio/worst',
                'outtmpl': f'{self.temp_dir}/{video_id}.%(ext)s',
                'write_auto_subs': True,
                'sub_langs': ['zh-Hans', 'zh-CN'],
                'ignoreerrors': True
            }
            
            with yt_dlp.YoutubeDL(dl_opts) as ydl_dl:
                info_dict = ydl_dl.extract_info(video_url, download=True)
                
                if not info_dict:
                    self._log(f"[-] 无法获取视频信息，URL: {video_url}")
                    return
                
                v_title = info_dict.get('title', f"Video_{video_id}")
            
            self._log(f"[√] 成功获取标题: {v_title}")
            
            # 检查是否应该停止
            if self.should_stop:
                self._log("[!] 任务已停止")
                return
            
            v_file = self._find_video_file(video_id)
            if not v_file:
                self._log(f"[-] 未找到视频文件: {video_id}")
                return
            
            # 检查是否应该停止
            if self.should_stop:
                self._log("[!] 任务已停止")
                return
            
            raw_text = self._get_transcription(v_file, video_id)
            
            # 检查是否应该停止
            if self.should_stop:
                self._log("[!] 任务已停止")
                return
            
            f_dir = self.temp_dir / f"f_{video_id}"
            frames = self._extract_keyframes(v_file, f_dir)
            
            # 检查是否应该停止
            if self.should_stop:
                self._log("[!] 任务已停止")
                return
            
            ai_summary = self._analyze_with_ollama(v_title, video_url, raw_text, frames)
            
            # 检查是否应该停止
            if self.should_stop:
                self._log("[!] 任务已停止")
                return
            
            if ai_summary:
                final_data = f"【视频标题】：{v_title} 。【视频链接】：{video_url} 。【详细分析总结】：{ai_summary}"
            else:
                self._log("[*] 使用 Whisper 识别的文本作为回退方案...")
                final_data = f"【视频标题】：{v_title} 。【视频链接】：{video_url} 。【详细内容】：{self._smart_truncate(raw_text, 3000)}"
            
            # 检查是否应该停止
            if self.should_stop:
                self._log("[!] 任务已停止")
                return
            
            self._upload_to_dify(v_title, final_data)
            
            # 检查是否应该停止
            if self.should_stop:
                self._log("[!] 任务已停止")
                return
            
            self._cleanup_video(video_id, v_file, f_dir)
            
        except Exception as e:
            self._log(f"[-] 处理视频异常: {e}")
    
    def _find_video_file(self, video_id):
        """查找视频文件"""
        for ext in ['.mp4', '.mkv', '.webm']:
            v_file = self.temp_dir / f"{video_id}{ext}"
            if v_file.exists():
                return v_file
        return None
    
    def _get_transcription(self, video_path, video_id):
        """获取视频转录文本"""
        for f in self.temp_dir.iterdir():
            if f.name.startswith(video_id) and f.name.endswith(".vtt"):
                with open(f, 'r', encoding='utf-8') as file:
                    return " ".join([
                        l.strip() for l in file 
                        if "-->" not in l and not l.strip().isdigit() and "WEBVTT" not in l
                    ])
        
        audio_path = video_path.with_suffix('.mp3')
        self._log("[*] Whisper 正在识别长音频内容...")
        
        try:
            subprocess.run([
                'ffmpeg', '-i', str(video_path), '-ar', '16000', '-ac', '1',
                '-c:a', 'libmp3lame', '-y', str(audio_path)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            
            if self.should_stop:
                self._log("[!] 任务已停止（Whisper调用前）")
                return ""
            
            if self.whisper_model:
                import threading
                
                segments_result = []
                transcribe_complete = threading.Event()
                
                def transcribe_worker():
                    try:
                        segments, _ = self.whisper_model.transcribe(str(audio_path), beam_size=5)
                        segments_result.extend(segments)
                    except Exception as e:
                        self._log(f"[-] Whisper transcribe 异常: {e}")
                    finally:
                        transcribe_complete.set()
                
                thread = threading.Thread(target=transcribe_worker)
                thread.daemon = True
                thread.start()
                
                while thread.is_alive():
                    if self.should_stop:
                        self._log("[!] 任务已停止（Whisper执行中）")
                        break
                    thread.join(timeout=0.5)
                
                if self.should_stop:
                    transcribe_complete.set()
                    return ""
                
                transcribe_complete.wait()
                text = " ".join([s.text for s in segments_result])
            else:
                text = ""
            
            if audio_path.exists():
                audio_path.unlink()
            
            return text
        except Exception as e:
            self._log(f"[-] 语音转文字失败: {e}")
            return ""
    
    def _extract_keyframes(self, video_path, output_dir):
        """提取关键帧"""
        if self.should_stop:
            self._log("[!] 任务已停止（提取关键帧前）")
            return []
        
        output_dir.mkdir(exist_ok=True)
        self._log("[*] 提取关键帧图片...")
        
        try:
            subprocess.run([
                'ffmpeg', '-i', str(video_path), '-vf', 'fps=1/60,scale=640:-1',
                '-q:v', '5', str(output_dir / 'f_%03d.jpg'), '-y'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            
            frames = list(output_dir.glob('*.jpg'))
            return sorted(frames)
        except Exception as e:
            self._log(f"[-] 提取关键帧失败: {e}")
            return []
    
    def _analyze_with_ollama(self, title, url, text_data, frames):
        """使用AI模型进行分析"""
        self._log("[*] 正在请求 AI 进行深度详细分析...")
        
        try:
            prompt = f"""任务：请根据以下视频资料，写一份非常详细的中文笔记。
要求：
1. 包含详细的视频背景摘要（200字）。
2. 列出视频中的关键知识点或核心情节。
3. 总结视频的最终价值。

视频信息：
标题：{title}
URL：{url}
内容：{self._smart_truncate(text_data, 2000)}
"""
            
            # 直接使用通义千问模型，不依赖配置
            provider = "qwen"
            model_config = get_model_config(provider)
            
            self._log(f"[*] 使用模型供应商: {provider}")
            self._log(f"[*] 使用模型: {model_config['model_name']}")
            
            # 通义千问 API
            qwen_url = f"{model_config['base_url']}/services/aigc/text-generation/generation"
            payload = {
                "model": model_config['model_name'],
                "input": prompt,
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {model_config['api_key']}"
            }
            
            res = requests.post(qwen_url, json=payload, headers=headers, timeout=300)
            if res.status_code == 200:
                response_json = res.json()
                ai_res = response_json.get("output", {}).get("text", "").strip()
            else:
                ai_res = ""
            
            if not ai_res:
                return ""
            
            return ai_res.replace("\n", " ").replace("\r", " ").replace("  ", " ")
        except Exception as e:
            self._log(f"[-] AI 分析失败: {e}")
            return ""
    
    def _upload_to_dify(self, title, content):
        """上传到Dify知识库"""
        if not content:
            return
        
        safe_content = content[:3500]
        
        self._log(f"[*] 正在同步至 Dify... 长度: {len(safe_content)} 字符")
        
        dify_base_url = "http://localhost/v1"
        dataset_api = self.config_manager.get_dataset_api()
        dataset_id = self.config_manager.get_dataset_id()
        
        url = f"{dify_base_url}/datasets/{dataset_id}/document/create-by-text"
        headers = {
            "Authorization": f"Bearer {dataset_api}",
            "Content-Type": "application/json"
        }
        
        data = {
            "name": title,
            "text": safe_content,
            "indexing_technique": "high_quality",
            "process_rule": {
                "mode": "custom",
                "rules": {
                    "pre_processing_rules": [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": False}
                    ],
                    "segmentation": {
                        "separator": "\\n\\n",
                        "max_tokens": 4000
                    }
                }
            }
        }
        
        try:
            res = requests.post(url, headers=headers, json=data)
            if res.status_code == 200:
                self._log(f"[√] 已提交索引请求: {title}")
            else:
                self._log(f"[-] 上传失败，状态码: {res.status_code}, 原因: {res.text}")
        except Exception as e:
            self._log(f"[-] 连接 Dify 失败: {e}")
    
    def _cleanup_video(self, video_id, v_file, f_dir):
        """清理视频相关临时文件"""
        try:
            if v_file and v_file.exists():
                v_file.unlink()
            
            if f_dir.exists():
                import shutil
                shutil.rmtree(f_dir)
            
            for f in self.temp_dir.iterdir():
                if f.name.startswith(video_id):
                    f.unlink()
        except Exception as e:
            self._log(f"[-] 清理临时文件失败: {e}")
    
    def _is_processed(self, video_id):
        """检查视频是否已处理"""
        if not self.archive_file.exists():
            return False
        
        try:
            with open(self.archive_file, 'r', encoding='utf-8') as f:
                return video_id in f.read()
        except Exception:
            return False
    
    def _save_cookie(self, cookie_text, url=None):
        """保存Cookie到文件，支持多种格式自动识别和转换"""
        if not cookie_text or not cookie_text.strip():
            self._log("[-] Cookie 为空，跳过保存")
            return
        
        try:
            # 检测Cookie格式
            format_type = detect_cookie_format(cookie_text)
            format_name = get_cookie_format_name(format_type)
            self._log(f"[*] 检测到 Cookie 格式: {format_name}")
            
            # 从URL中提取域名（用于Header String格式）
            target_domain = None
            if url:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    if parsed.netloc:
                        # 提取主域名（添加点号前缀）
                        # 例如：www.bilibili.com -> .bilibili.com
                        # bilibili.com -> .bilibili.com
                        # 这样符合开闭原则，扩展新平台时无需修改代码
                        domain_parts = parsed.netloc.split('.')
                        if len(domain_parts) >= 2:
                            # 提取最后两部分作为主域名，并添加点号前缀
                            target_domain = f".{'.'.join(domain_parts[-2:])}"
                        else:
                            # 如果域名格式不正确，直接使用原域名
                            target_domain = parsed.netloc
                        self._log(f"[*] 从 URL 提取域名: {target_domain}")
                except Exception as e:
                    self._log(f"[-] 提取域名失败: {e}")
            
            # 转换为NetScape格式
            netscape_cookie = normalize_cookie(cookie_text, target_domain=target_domain)
            
            if not netscape_cookie:
                self._log("[-] Cookie 转换失败，请检查输入格式")
                return
            
            # 保存到文件
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                f.write(netscape_cookie)
            
            self._log("[√] Cookie 已保存并转换为 NetScape 格式")
        except Exception as e:
            self._log(f"[-] 保存 Cookie 失败: {e}")
    
    def _smart_truncate(self, text, max_len=3500):
        """智能截断文本"""
        if not text:
            return ""
        if len(text) <= max_len:
            return text
        return text[:max_len//2] + " [中间内容省略] " + text[-max_len//2:]


class KnowledgeUpdater(QObject):
    logUpdated = Signal(str)
    updateStarted = Signal()
    updateStopped = Signal()
    updateFinished = Signal()

    def __init__(self, config_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.is_running = False
        self.should_stop = False
        self.log_buffer = []
        self.whisper_model = None
        
        self._init_paths()
    
    def _init_paths(self):
        """初始化路径"""
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.temp_dir = self.data_dir / "bili_temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        self.archive_file = self.data_dir / "download_history.txt"
        self.cookies_file = self.data_dir / "cookies.txt"
        
        self.whisper_path = Path(__file__).parent / "utils" / "whisper"
    
    def _init_whisper(self):
        """初始化Whisper模型"""
        try:
            os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
            os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
            
            self.whisper_model = WhisperModel(
                "small",
                device="cpu",
                compute_type="int8",
                download_root=str(self.whisper_path),
                local_files_only=True
            )
            self._log("[√] Whisper 模型加载成功")
        except Exception as e:
            self._log(f"[-] Whisper 模型加载失败: {e}")
            self.whisper_model = None
    
    def _log(self, message):
        """记录日志"""
        self.log_buffer.append(message)
        self.logUpdated.emit(message)
        print(message)
    
    def _get_handler(self, platform, type_name):
        """
        根据平台和类型获取对应的处理器
        
        Args:
            platform: 平台名称
            type_name: 类型名称
        
        Returns:
            BasePlatformHandler: 处理器实例，如果不支持则返回None
        """
        if not is_type_supported(platform, type_name):
            self._log(f"[-] 暂不支持 {platform} 的 {type_name} 类型")
            return None
        
        if platform == "Bilibili" and type_name == "收藏夹":
            return BilibiliPlaylistHandler(
                self.config_manager,
                self._log,
                self.temp_dir,
                self.archive_file,
                self.cookies_file,
                self.whisper_model
            )
        
        return None
    
    @Slot()
    def start_update(self):
        """开始更新任务"""
        if self.is_running:
            self._log("[!] 更新任务已在运行中")
            return
        
        # 初始化Whisper模型
        self._init_whisper()
        
        if not self.whisper_model:
            self._log("[-] Whisper 模型未加载，无法启动更新")
            return
        
        self.is_running = True
        self.should_stop = False
        self.log_buffer = []
        self.updateStarted.emit()
        
        thread = threading.Thread(target=self._run_update)
        thread.daemon = True
        thread.start()
    
    @Slot()
    def stop_update(self):
        """停止更新任务"""
        if self.is_running:
            self.should_stop = True
            self._log("[!] 正在停止更新任务...")
    
    def _run_update(self):
        """运行更新任务（在后台线程中执行）"""
        try:
            self._log("[*] 开始更新知识库...")
            
            platform = self.config_manager.get_knowledge_platform()
            update_type = self.config_manager.get_knowledge_type()
            url = self.config_manager.get_knowledge_url()
            cookie = self.config_manager.get_knowledge_cookie()
            
            self._log(f"[*] 平台: {platform}")
            self._log(f"[*] 类型: {update_type}")
            self._log(f"[*] URL: {url}")
            
            if not url:
                self._log("[-] URL 为空，请先配置")
                self._finish_update()
                return
            
            handler = self._get_handler(platform, update_type)
            if handler:
                # 启动处理器
                thread = threading.Thread(target=self._process_with_handler, args=(handler, url, cookie))
                thread.daemon = True
                thread.start()
                # 定期检查停止标志并更新处理器
                while thread.is_alive():
                    if self.should_stop:
                        handler.should_stop = True
                        self._log("[!] 正在停止更新任务...")
                    import time
                    time.sleep(0.1)
                thread.join()
            
        except Exception as e:
            self._log(f"[-] 更新过程发生错误: {e}")
        finally:
            self._finish_update()
    
    def _process_with_handler(self, handler, url, cookie):
        """使用处理器处理任务"""
        try:
            # 处理任务
            handler.process(url, cookie)
        except Exception as e:
            self._log(f"[-] 处理器执行失败: {e}")
    
    def _finish_update(self):
        """完成更新任务"""
        self.is_running = False
        self.updateStopped.emit()
        self.updateFinished.emit()
        self._log("[*] 更新任务完成")
    
    @Slot(result=str)
    def get_log(self):
        """获取日志"""
        return "\n".join(self.log_buffer)
    
    @Slot(result=bool)
    def is_running_status(self):
        """检查是否正在运行"""
        return self.is_running
