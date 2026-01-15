import re
from PySide6.QtCore import QObject, Slot


class MarkdownFormatter(QObject):
    def __init__(self):
        super().__init__()

    @Slot(str, result=str)
    def format(self, text):
        if not text:
            return ""
        
        formatted = text
        
        # 格式化顺序很重要，先处理复杂的，再处理简单的
        formatted = self._format_code_blocks(formatted)
        formatted = self._format_horizontal_rules(formatted)
        formatted = self._format_inline_code(formatted)
        formatted = self._format_bold(formatted)
        formatted = self._format_italic(formatted)
        formatted = self._format_headings(formatted)
        formatted = self._format_lists(formatted)
        formatted = self._format_links(formatted)
        formatted = self._format_auto_links(formatted)
        formatted = self._format_newlines(formatted)
        
        return formatted

    def _format_italic(self, text):
        pattern = r'\*([^*]+)\*'
        
        def replace_italic(match):
            content = match.group(1)
            return f'<span style="font-style: italic;">{content}</span>'
        
        return re.sub(pattern, replace_italic, text)

    def _format_headings(self, text):
        # 支持 # 到 ###### 的标题，处理标题前可能的空格
        for i in range(6, 0, -1):
            pattern = rf'^\s*{"#" * i} (.*)$'
            
            def replace_heading(match):
                content = match.group(1)
                font_size = 24 - (i - 1) * 3  # 标题1: 24px, 标题2: 21px, ..., 标题6: 9px
                return f'<div style="font-size: {font_size}px; font-weight: bold; color: #e4e4e7; margin: 16px 0 8px 0;">{content}</div>'
            
            text = re.sub(pattern, replace_heading, text, flags=re.MULTILINE)
        
        return text

    def _format_lists(self, text):
        # 无序列表 - 支持 -, *, + 作为列表标记
        pattern = r'^\s*[-*+] (.*)$'
        
        def replace_unordered_list(match):
            content = match.group(1)
            return f'<div style="margin: 4px 0; padding-left: 24px;">• {content}</div>'
        
        text = re.sub(pattern, replace_unordered_list, text, flags=re.MULTILINE)
        
        # 有序列表 - 支持数字. 格式
        pattern = r'^\s*\d+\. (.*)$'
        
        def replace_ordered_list(match):
            content = match.group(1)
            return f'<div style="margin: 4px 0; padding-left: 24px;">{match.group(0).split(" ")[0]} {content}</div>'
        
        text = re.sub(pattern, replace_ordered_list, text, flags=re.MULTILINE)
        
        return text

    def _format_newlines(self, text):
        # 替换换行符为<br>标签
        return text.replace('\n', '<br>')

    def _format_code_blocks(self, text):
        pattern = r'```([\s\S]*?)\n([\s\S]*?)```'
        
        def replace_code_block(match):
            language = match.group(1) or ''
            code = match.group(2)
            return f'<div style="background-color: #1d1d20; border-radius: 8px; padding: 12px; margin: 8px 0;"><pre style="font-family: Consolas, Monospace; font-size: 13px; color: #e4e4e7; margin: 0; white-space: pre-wrap; overflow-x: auto;"><code>{code}</code></pre></div>'
        
        return re.sub(pattern, replace_code_block, text, flags=re.MULTILINE | re.DOTALL)
    
    def _format_horizontal_rules(self, text):
        # 支持 ---, ***, ___ 三种水平线格式
        # 匹配单独一行的 ---, ***, 或 ___（前后可以有空白）
        pattern = r'^\s*([-*_]{3,})\s*$'
        
        def replace_hr(match):
            return '<hr style="border: none; border-top: 1px solid #27272a; margin: 16px 0;">'
        
        return re.sub(pattern, replace_hr, text, flags=re.MULTILINE)

    def _format_inline_code(self, text):
        pattern = r'`([^`]+)`'
        
        def replace_inline_code(match):
            code = match.group(1)
            return f'<span style="background-color: #27272a; color: #e4e4e7; font-family: Consolas, Monospace; font-size: 13px; padding: 2px 6px; border-radius: 4px;">{code}</span>'
        
        return re.sub(pattern, replace_inline_code, text)

    def _format_bold(self, text):
        pattern = r'\*\*([^*]+)\*\*'
        
        def replace_bold(match):
            content = match.group(1)
            return f'<span style="font-weight: bold;">{content}</span>'
        
        return re.sub(pattern, replace_bold, text)

    def _format_links(self, text):
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            link_text = match.group(1)
            url = match.group(2)
            return f'<a href="{url}" style="color: #3b82f6; text-decoration: underline;">{link_text}</a>'
        
        return re.sub(pattern, replace_link, text)
    
    def _format_auto_links(self, text):
        # 自动检测并格式化裸露的 URL（不在 Markdown 链接语法中的 URL）
        # 匹配 http:// 或 https:// 开头的 URL
        pattern = r'(?<!\])(https?://[^\s<>"{}|\\^`\[\]]+)'
        
        def replace_auto_link(match):
            url = match.group(1)
            # 限制显示的 URL 长度，避免太长
            display_url = url if len(url) <= 50 else url[:47] + "..."
            return f'<a href="{url}" style="color: #3b82f6; text-decoration: underline;">{display_url}</a>'
        
        return re.sub(pattern, replace_auto_link, text)