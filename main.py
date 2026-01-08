import sys
import time
import threading
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtQuickControls2 import QQuickStyle


class ChatController(QObject):
    messageReceived = Signal(str)
    generationStarted = Signal()
    generationStopped = Signal()
    loadingStateChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self.is_generating = False
        self.should_stop = False

    @Slot(str)
    def send_message(self, text):
        print(f"User sent: {text}")
        
        if self.is_generating:
            return
        
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

    controller = ChatController()
    engine.rootContext().setContextProperty("chatController", controller)

    qml_file = Path(__file__).parent / "main.qml"
    engine.load(str(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
