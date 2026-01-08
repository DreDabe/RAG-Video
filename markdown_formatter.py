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
        
        formatted = self._format_code_blocks(formatted)
        formatted = self._format_inline_code(formatted)
        formatted = self._format_bold(formatted)
        formatted = self._format_links(formatted)
        
        return formatted

    def _format_code_blocks(self, text):
        pattern = r'```([\s\S]*?)\n([\s\S]*?)```'
        
        def replace_code_block(match):
            language = match.group(1) or ''
            code = match.group(2)
            return f'<div style="background-color: #1d1d20; border-radius: 8px; padding: 12px; margin: 8px 0;"><pre style="font-family: Consolas, Monospace; font-size: 13px; color: #e4e4e7; margin: 0; white-space: pre-wrap; overflow-x: auto;"><code>{code}</code></pre></div>'
        
        return re.sub(pattern, replace_code_block, text, flags=re.MULTILINE | re.DOTALL)

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
            text = match.group(1)
            url = match.group(2)
            return f'<a href="{url}" style="color: #3b82f6; text-decoration: underline;">{text}</a>'
        
        return re.sub(pattern, replace_link, text)
