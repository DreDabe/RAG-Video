import sys
import time
import threading
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtQuickControls2 import QQuickStyle
from conversation_manager import ConversationManager
from config_manager import ConfigManager
from markdown_formatter import MarkdownFormatter
from knowledge_updater import KnowledgeUpdater
from dify_client import DifyClient


class ChatController(QObject):
    messageReceived = Signal(str)
    generationStarted = Signal()
    generationStopped = Signal()
    loadingStateChanged = Signal(bool)
    messageAdded = Signal()
    messageChunkReceived = Signal(str)

    def __init__(self, conversation_manager=None, config_manager=None):
        super().__init__()
        self.conversation_manager = conversation_manager or ConversationManager()
        self.config_manager = config_manager
        self.markdown_formatter = MarkdownFormatter()
        self.is_generating = False
        self.should_stop = False
        self.dify_conversation_id = None
        self.dify_client = None
        self.current_answer = ""

    @Slot(str, result=str)
    def format_markdown(self, text):
        return self.markdown_formatter.format(text)

    @Slot(str)
    def send_message(self, text):
        print(f"[ChatController] ========== 开始发送消息 ==========")
        print(f"[ChatController] 用户消息: {text}")
        print(f"[ChatController] 当前生成状态: {self.is_generating}")
        
        if self.is_generating:
            print("[ChatController] 正在生成中，忽略新消息")
            return
        
        current_conv = self.conversation_manager.get_current_conversation()
        if not current_conv:
            print("[ChatController] 当前没有对话，创建新对话")
            current_conv = self.conversation_manager.create_new_conversation()
        
        conversation_id = current_conv['id']
        print(f"[ChatController] 对话ID: {conversation_id}")
        
        self.conversation_manager.add_message(conversation_id, "user", text)
        self.messageAdded.emit()
        
        self.is_generating = True
        self.should_stop = False
        self.current_answer = ""
        self.generationStarted.emit()
        self.loadingStateChanged.emit(True)
        
        def generate_response():
            try:
                print("[ChatController] ========== 开始生成响应 ==========")
                
                if self.should_stop:
                    print("[ChatController] 用户请求停止生成")
                    return
                
                if not self.config_manager:
                    print("[ChatController] 错误: ConfigManager未初始化")
                    raise Exception("ConfigManager未初始化")
                
                print("[ChatController] 获取Dify API Key...")
                api_key = self.config_manager.get_app_api()
                print(f"[ChatController] API Key: {api_key[:10] if api_key else 'None'}...")
                
                if not api_key:
                    print("[ChatController] 错误: Dify API Key未配置")
                    raise Exception("Dify API Key未配置，请在设置中配置API Key")
                
                print("[ChatController] 获取Dify Base URL...")
                base_url = self.config_manager.get_app_url()
                print(f"[ChatController] Base URL: {base_url}")
                
                if not base_url:
                    print("[ChatController] 使用默认Base URL")
                    base_url = "https://api.dify.ai/v1"
                
                print("[ChatController] 创建DifyClient...")
                self.dify_client = DifyClient(api_key, base_url)
                
                user_id = "digital-garden-user"
                print(f"[ChatController] 发送消息到Dify...")
                print(f"[ChatController] User ID: {user_id}")
                print(f"[ChatController] Dify Conversation ID: {self.dify_conversation_id}")
                
                def on_message_chunk(chunk):
                    print(f"[ChatController] 收到消息片段: {chunk[:50]}...")
                    self.current_answer += chunk
                    self.messageChunkReceived.emit(chunk)
                
                def on_finished():
                    print("[ChatController] ========== 响应生成完成 ==========")
                    print(f"[ChatController] 完整答案: {self.current_answer[:100]}...")
                    
                    self.dify_conversation_id = self.dify_client.get_conversation_id({})
                    print(f"[ChatController] Dify Conversation ID: {self.dify_conversation_id}")
                    
                    print("[ChatController] 发送消息到UI...")
                    self.messageReceived.emit(self.current_answer)
                    self.conversation_manager.add_message(conversation_id, "assistant", self.current_answer)
                    self.messageAdded.emit()
                    
                    self.is_generating = False
                    self.generationStopped.emit()
                    self.loadingStateChanged.emit(False)
                    self.current_answer = ""
                
                def on_error(error_msg):
                    print(f"[ChatController] ========== 生成响应失败 ==========")
                    print(f"[ChatController] 错误信息: {error_msg}")
                    
                    error_message = f"抱歉，发生了错误：{error_msg}"
                    self.messageReceived.emit(error_message)
                    self.conversation_manager.add_message(conversation_id, "assistant", error_message)
                    self.messageAdded.emit()
                    
                    self.is_generating = False
                    self.generationStopped.emit()
                    self.loadingStateChanged.emit(False)
                    self.current_answer = ""
                
                response = self.dify_client.send_message(
                    query=text,
                    user=user_id,
                    conversation_id=self.dify_conversation_id,
                    response_mode="streaming",
                    on_message=on_message_chunk,
                    on_finished=on_finished,
                    on_error=on_error
                )
                
                if self.should_stop:
                    print("[ChatController] 用户请求停止生成")
                    return
                
            except Exception as e:
                print(f"[ChatController] ========== 生成响应失败 ==========")
                print(f"[ChatController] 错误类型: {type(e).__name__}")
                print(f"[ChatController] 错误信息: {str(e)}")
                import traceback
                print(f"[ChatController] 堆栈跟踪:\n{traceback.format_exc()}")
                
                error_message = f"抱歉，发生了错误：{str(e)}"
                self.messageReceived.emit(error_message)
                self.conversation_manager.add_message(conversation_id, "assistant", error_message)
                self.messageAdded.emit()
                self.is_generating = False
                self.generationStopped.emit()
                self.loadingStateChanged.emit(False)
                self.current_answer = ""
        
        print("[ChatController] 启动生成线程...")
        thread = threading.Thread(target=generate_response)
        thread.daemon = True
        thread.start()
        print("[ChatController] 线程已启动")

    @Slot()
    def stop_generation(self):
        print("[ChatController] ========== 停止生成 ==========")
        
        if not self.is_generating:
            print("[ChatController] 当前没有正在进行的生成")
            return
        
        self.should_stop = True
        print("[ChatController] 已设置停止标志")
        
        if self.dify_client:
            print("[ChatController] 调用Dify停止API...")
            success = self.dify_client.stop_generation()
            if success:
                print("[ChatController] Dify停止API调用成功")
            else:
                print("[ChatController] Dify停止API调用失败，但本地已停止")
        
        print("[ChatController] ========== 停止完成 ==========")


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    config_manager = ConfigManager()
    controller = ChatController(config_manager=config_manager)
    knowledge_updater = KnowledgeUpdater(config_manager)
    engine.rootContext().setContextProperty("chatController", controller)
    engine.rootContext().setContextProperty("conversationManager", controller.conversation_manager)
    engine.rootContext().setContextProperty("configManager", config_manager)
    engine.rootContext().setContextProperty("knowledgeUpdater", knowledge_updater)
    engine.rootContext().setContextProperty("markdownFormatter", controller.markdown_formatter)

    qml_file = Path(__file__).parent / "main.qml"
    engine.load(str(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
