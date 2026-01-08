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

    def __init__(self, conversation_manager=None, config_manager=None):
        super().__init__()
        self.conversation_manager = conversation_manager or ConversationManager()
        self.config_manager = config_manager
        self.markdown_formatter = MarkdownFormatter()
        self.is_generating = False
        self.should_stop = False
        self.dify_conversation_id = None

    @Slot(str, result=str)
    def format_markdown(self, text):
        return self.markdown_formatter.format(text)

    @Slot(str)
    def send_message(self, text):
        print(f"User sent: {text}")
        
        if self.is_generating:
            return
        
        current_conv = self.conversation_manager.get_current_conversation()
        if not current_conv:
            current_conv = self.conversation_manager.create_new_conversation()
        
        conversation_id = current_conv['id']
        
        self.conversation_manager.add_message(conversation_id, "user", text)
        self.messageAdded.emit()
        
        self.is_generating = True
        self.should_stop = False
        self.generationStarted.emit()
        self.loadingStateChanged.emit(True)
        
        def generate_response():
            try:
                if self.should_stop:
                    return
                
                if not self.config_manager:
                    raise Exception("ConfigManager未初始化")
                
                api_key = self.config_manager.get_app_api()
                if not api_key:
                    raise Exception("Dify API Key未配置")
                
                dify_client = DifyClient(api_key)
                
                user_id = "digital-garden-user"
                response = dify_client.send_message(
                    query=text,
                    user=user_id,
                    conversation_id=self.dify_conversation_id,
                    response_mode="blocking"
                )
                
                if self.should_stop:
                    return
                
                answer = dify_client.get_answer(response)
                self.dify_conversation_id = dify_client.get_conversation_id(response)
                
                print(f"Dify response: {answer}")
                
                self.messageReceived.emit(answer)
                self.conversation_manager.add_message(conversation_id, "assistant", answer)
                self.messageAdded.emit()
                
                self.is_generating = False
                self.generationStopped.emit()
                self.loadingStateChanged.emit(False)
            except Exception as e:
                print(f"Error in generate_response: {e}")
                error_message = f"抱歉，发生了错误：{str(e)}"
                self.messageReceived.emit(error_message)
                self.conversation_manager.add_message(conversation_id, "assistant", error_message)
                self.messageAdded.emit()
                self.is_generating = False
                self.generationStopped.emit()
                self.loadingStateChanged.emit(False)
        
        thread = threading.Thread(target=generate_response)
        thread.daemon = True
        thread.start()

    @Slot()
    def stop_generation(self):
        print("Stopping generation...")
        self.should_stop = True


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    config_manager = ConfigManager()
    controller = ChatController()
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
