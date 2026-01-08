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


class ChatController(QObject):
    messageReceived = Signal(str)
    generationStarted = Signal()
    generationStopped = Signal()
    loadingStateChanged = Signal(bool)
    messageAdded = Signal()

    def __init__(self, conversation_manager=None):
        super().__init__()
        self.conversation_manager = conversation_manager or ConversationManager()
        self.markdown_formatter = MarkdownFormatter()
        self.is_generating = False
        self.should_stop = False

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
                time.sleep(0.5)
                
                if self.should_stop:
                    return
                
                self.messageReceived.emit("1")
                
                time.sleep(0.3)
                
                if self.should_stop:
                    return
                
                self.conversation_manager.add_message(conversation_id, "assistant", "1")
                self.messageAdded.emit()
                
                self.is_generating = False
                self.generationStopped.emit()
                self.loadingStateChanged.emit(False)
            except Exception as e:
                print(f"Error in generate_response: {e}")
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
