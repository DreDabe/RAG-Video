import os
import re
import base64
import subprocess
import requests
import shutil
import yt_dlp
from faster_whisper import WhisperModel

# ================= 配置区域 =================
PLAYLIST_URL = "https://www.bilibili.com/medialist/play/ml387412427" 
COOKIES_FILE = "cookies.txt"        
ARCHIVE_FILE = "download_history.txt" 
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:8b"           # 使用系统中可用的模型

DIFY_BASE_URL = "http://localhost/v1"
DIFY_API_KEY = "dataset-nCFE6gRoqoLnb5Vdn3O3vPc0"
DATASET_ID = "440bcad8-f7b1-4804-bae3-2ff47e268fee"

WHISPER_DOWNLOAD_ROOT = r"D:\Program\Project\model\whisper"
TEMP_DIR = "bili_temp"
MAX_TEXT_LEN = 3500 
# ============================================

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

print(f"[*] 正在从本地加载 Whisper 模型...")
whisper_model = WhisperModel("small", device="cpu", compute_type="int8", download_root=WHISPER_DOWNLOAD_ROOT, local_files_only=True)

def sanitize_filename(filename):
    if not filename: return "video"
    return re.sub(r'[\\/:*?"<>|]', '', filename).strip()

def smart_truncate(text, max_len=3500):
    if not text: return ""
    if len(text) <= max_len: return text
    return text[:max_len//2] + " [中间内容省略] " + text[-max_len//2:]

def extract_keyframes(video_path, output_dir):
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    print(f"[*] 提取关键帧图片...")
    subprocess.run(['ffmpeg', '-i', video_path, '-vf', 'fps=1/60,scale=640:-1', '-q:v', '5', os.path.join(output_dir, 'f_%03d.jpg'), '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return [os.path.join(output_dir, f) for f in sorted(os.listdir(output_dir)) if f.endswith('.jpg')]

def get_transcription(video_path, video_id):
    # 尝试读取字幕
    for f in os.listdir(TEMP_DIR):
        if f.startswith(video_id) and f.endswith(".vtt"):
            with open(os.path.join(TEMP_DIR, f), 'r', encoding='utf-8') as file:
                return " ".join([l.strip() for l in file if "-->" not in l and not l.strip().isdigit() and "WEBVTT" not in l])
    # 语音转文字
    audio_path = video_path.replace(".mp4", ".mp3")
    print(f"[*] Whisper 正在识别长音频内容...")
    subprocess.run(['ffmpeg', '-i', video_path, '-ar', '16000', '-ac', '1', '-c:a', 'libmp3lame', '-y', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    segments, _ = whisper_model.transcribe(audio_path, beam_size=5)
    text = " ".join([s.text for s in segments])
    if os.path.exists(audio_path): os.remove(audio_path)
    return text

def analyze_with_ollama(title, url, text_data, frames):
    """
    丰富 Prompt 以获得更长的分析结果
    """
    print(f"[*] 正在请求 AI 进行深度详细分析...")
    try:
        # 允许 AI 正常思考，不要在 Prompt 里限制不换行，后面由脚本统一处理
        prompt = f"""任务：请根据以下视频资料，写一份非常详细的中文笔记。
要求：
1. 包含详细的视频背景摘要（200字）。
2. 列出视频中的关键知识点或核心情节。
3. 总结视频的最终价值。

视频信息：
标题：{title}
URL：{url}
内容：{smart_truncate(text_data, 2000)}
"""
        # 只发送文本数据，不发送图像，减少内存使用
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        
        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=300)
            if res.status_code == 200:
                try:
                    response_json = res.json()
                    ai_res = response_json.get("response", "").strip()
                except Exception:
                    ai_res = ""
            else:
                ai_res = ""
        except Exception:
            ai_res = ""
        
        if not ai_res:
            return ""
        
        # 【重要】为了不让 Dify 分段，我们在这里把换行符全部变为空格
        return ai_res.replace("\n", " ").replace("\r", " ").replace("  ", " ")
    except Exception:
        return ""

def upload_to_dify(title, content):
    """
    针对‘状态错误’优化的上传逻辑
    1. 强制限制长度在 3500 字符内（避开大多数 Embedding 模型的 4096 限制）
    2. 简化预处理规则
    """
    if not content: return

    # 1. 再次物理截断，防止 AI 话太多导致 Dify 索引崩溃
    # 3500 字符是一个非常安全的临界点
    safe_content = content[:3500] 

    print(f"[*] 正在同步至 Dify... 长度: {len(safe_content)} 字符")

    url = f"{DIFY_BASE_URL}/datasets/{DATASET_ID}/document/create-by-text"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 重新梳理的 Payload 结构，这是 Dify 官方最标准的自定义分段格式
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
                    "separator": "\\n\\n", # 使用双换行作为形式上的分隔符
                    "max_tokens": 4000      # 设为 4000 是最稳妥的
                }
            }
        }
    }
    
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            print(f"[√] 已提交索引请求: {title}")
        else:
            print(f"[-] 上传失败，状态码: {res.status_code}, 原因: {res.text}")
    except Exception as e:
        print(f"[-] 连接 Dify 失败: {e}")

def main():
    if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
    
    print("[*] 正在扫描播放列表...")
    with yt_dlp.YoutubeDL({'cookiefile': COOKIES_FILE, 'extract_flat': True, 'quiet': True}) as ydl:
        try:
            playlist_info = ydl.extract_info(PLAYLIST_URL, download=False)
            entries = playlist_info.get('entries', [])
        except Exception as e:
            print(f"[-] 扫描列表失败: {e}")
            return

    for idx, entry in enumerate(entries, 1):
        if not entry: continue
        v_id = entry.get('id')
        v_url = f"https://www.bilibili.com/video/{v_id}"

        if os.path.exists(ARCHIVE_FILE) and v_id in open(ARCHIVE_FILE, 'r', encoding='utf-8').read():
            print(f"[{idx}/{len(entries)}] 已处理过，跳过: {v_id}"); continue

        # 重点：此处可能没拿到标题，我们在下载步骤再拿一次
        print(f"\n[{idx}/{len(entries)}] 正在处理视频 ID: {v_id}")
        
        dl_opts = {
            'cookiefile': COOKIES_FILE, 
            'download_archive': ARCHIVE_FILE, 
            'format': 'worstvideo[height<=360]+bestaudio/worst', 
            'outtmpl': f'{TEMP_DIR}/{v_id}.%(ext)s', 
            'write_auto_subs': True, 
            'sub_langs': ['zh-Hans', 'zh-CN'], 
            'ignoreerrors': True
        }
        
        try:
            # A. 下载并获取完整元数据（包含中文标题）
            with yt_dlp.YoutubeDL(dl_opts) as ydl_dl:
                info_dict = ydl_dl.extract_info(v_url, download=True)
                v_title_chinese = info_dict.get('title', f"Video_{v_id}") # 这里拿到的就是中文标题
            
            print(f"[√] 成功获取标题: {v_title_chinese}")

            # 寻找下载的文件
            v_file = next((os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR) if f.startswith(v_id) and f.endswith(('.mp4','.mkv','.webm'))), None)
            if not v_file: continue

            # B. 文本识别
            raw_text = get_transcription(v_file, v_id)
            
            # C. 截图分析
            f_dir = os.path.join(TEMP_DIR, f"f_{v_id}")
            frames = extract_keyframes(v_file, f_dir)
            
            # D. AI 分析（此时要求它详细写）
            ai_summary = analyze_with_ollama(v_title_chinese, v_url, raw_text, frames)
            
            # E. 组装数据
            # 把标题和链接拼在最前面，后面跟着详细的总结
            if ai_summary:
                final_data = f"【视频标题】：{v_title_chinese} 。【视频链接】：{v_url} 。【详细分析总结】：{ai_summary}"
            else:
                # 回退方案：直接使用 Whisper 识别的文本
                print(f"[*] 使用 Whisper 识别的文本作为回退方案...")
                final_data = f"【视频标题】：{v_title_chinese} 。【视频链接】：{v_url} 。【详细内容】：{smart_truncate(raw_text, 3000)}"
            
            # F. 上传 Dify，将 v_title_chinese 传给 name 参数
            upload_to_dify(v_title_chinese, final_data)

        except Exception as e:
            print(f"[-] 处理异常: {e}")
        finally:
            if 'v_file' in locals() and v_file and os.path.exists(v_file): os.remove(v_file)
            if os.path.exists(os.path.join(TEMP_DIR, f"f_{v_id}")): shutil.rmtree(os.path.join(TEMP_DIR, f"f_{v_id}"))
            for f in os.listdir(TEMP_DIR):
                if f.startswith(v_id): os.remove(os.path.join(TEMP_DIR, f))

if __name__ == "__main__":
    main()