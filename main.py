import sys
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtQuickControls2 import QQuickStyle


class ChatController(QObject):
    messageReceived = Signal(str)

    @Slot(str)
    def send_message(self, text):
        print(f"User sent: {text}")
        self.messageReceived.emit(f"这是针对 '{text}' 的知识库检索结果...")


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
