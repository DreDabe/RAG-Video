import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: window
    width: 1100
    height: 750
    visible: true
    title: "digital-garden-chat"
    color: "#09090b" // 主背景色
    
    flags: Qt.Window | Qt.FramelessWindowHint

    property real sidebarWidth: 260
    property bool sidebarExpanded: true
    property bool windowMaximized: false

    // 动画配置
    Behavior on sidebarWidth {
        NumberAnimation { duration: 350; easing.type: Easing.InOutQuart }
    }

    // ------------------ 修复版沉浸式标题栏 ------------------
    Rectangle {
        id: titleBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 32
        color: "#0c0c0e"
        z: 1000

        MouseArea {
            id: titleBarMouseArea
            anchors.fill: parent
            
            property point startPos: Qt.point(0, 0)
            
            onPressed: function(mouse) {
                if (!window.windowMaximized) {
                    window.startSystemMove()
                } else {
                    startPos = Qt.point(mouse.x, mouse.y)
                    console.log("onPressed - startPos:", startPos.x, startPos.y)
                }
            }
            
            onPositionChanged: function(mouse) {
                if (pressed && windowMaximized) {
                    let dx = mouse.x - startPos.x
                    let dy = mouse.y - startPos.y
                    
                    console.log("onPositionChanged - startPos:", startPos.x, startPos.y)
                    console.log("onPositionChanged - dx:", dx, "dy:", dy)
                    console.log("onPositionChanged - window pos before showNormal:", window.x, window.y)
                    
                    window.showNormal()
                    window.windowMaximized = false
                    
                    console.log("onPositionChanged - window pos after showNormal:", window.x, window.y)
                    
                    window.x = window.x + dx
                    window.y = window.y + dy
                    
                    console.log("onPositionChanged - final window pos:", window.x, window.y)
                    
                    window.startSystemMove()
                }
            }
            
            onDoubleClicked: {
                if (window.windowMaximized) {
                    window.showNormal()
                    window.windowMaximized = false
                } else {
                    window.showMaximized()
                    window.windowMaximized = true
                }
            }
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 0
            spacing: 0
            
            Row {
                Layout.alignment: Qt.AlignVCenter
                spacing: 10
                Image {
                    width: 12; height: 12
                    source: "img/仓鼠.svg"
                    sourceSize.width: 12
                    sourceSize.height: 12
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: "Digital Garden Chat"
                    color: "#e4e4e7"
                    font.pixelSize: 11
                    font.weight: Font.Medium
                }
            }

            Item { Layout.fillWidth: true }

            Row {
                id: controlButtons
                height: 32
                
                component WindowBtn : Rectangle {
                    id: btnRoot
                    property string iconSource: ""
                    property string altIconSource: "" // 备用图标源
                    property color hoverColor: "#27272a"
                    property var clickAction: null
                    
                    width: 46; height: 32
                    color: btnMa.containsMouse ? hoverColor : "transparent"
                    
                    // 主图标
                    Image {
                        anchors.centerIn: parent
                        width: 12; height: 12
                        source: btnRoot.iconSource
                        sourceSize.width: 12
                        sourceSize.height: 12
                        opacity: btnRoot.altIconSource !== "" ? (window.windowMaximized ? 0.0 : (btnMa.containsMouse ? 1.0 : 0.6)) : (btnMa.containsMouse ? 1.0 : 0.6)
                        Behavior on opacity { NumberAnimation { duration: 200 } }
                    }
                    
                    // 备用图标（用于动画切换）
                    Image {
                        anchors.centerIn: parent
                        width: 12; height: 12
                        source: btnRoot.altIconSource
                        sourceSize.width: 12
                        sourceSize.height: 12
                        opacity: btnRoot.altIconSource !== "" ? (window.windowMaximized ? 1.0 : 0.0) : 0.0
                        Behavior on opacity { NumberAnimation { duration: 200 } }
                    }
                    
                    MouseArea {
                        id: btnMa; anchors.fill: parent; hoverEnabled: true
                        onClicked: if (clickAction) clickAction()
                    }
                }

                WindowBtn {
                    iconSource: "img/最小化.svg"
                    clickAction: function() { window.showMinimized() }
                }

                WindowBtn {
                    iconSource: "img/最大化.svg"
                    altIconSource: "img/小化.svg"
                    clickAction: function() { 
                        if (window.windowMaximized) {
                            window.showNormal()
                            window.windowMaximized = false
                        } else {
                            window.showMaximized()
                            window.windowMaximized = true
                        }
                    }
                }

                WindowBtn {
                    iconSource: "img/关闭.svg"
                    hoverColor: "#e81123"
                    clickAction: function() { window.close() }
                }
            }
        }
    }

    // ------------------ 侧边栏 ------------------
    Rectangle {
        id: sidebar
        width: sidebarWidth
        anchors.left: parent.left
        anchors.top: titleBar.bottom
        anchors.bottom: parent.bottom
        color: "#0c0c0e"
        
        Rectangle {
            anchors.right: parent.right
            width: 1; height: parent.height; color: "#1d1d20"
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12

            // 侧边栏按钮组件模版
            component SidebarButton : Button {
                id: control
                property string iconSource: ""
                property string labelText: ""
                property bool isAccent: false
                property string expandIconSource: "" // 展开图标
                property string collapseIconSource: "" // 收缩图标

                Layout.fillWidth: true
                Layout.preferredHeight: 40
                
                background: Rectangle {
                    color: control.pressed ? "#3f3f46" : (control.hovered ? "#1d1d20" : "transparent")
                    border.color: isAccent ? "#27272a" : "transparent"
                    radius: 8
                }

                contentItem: RowLayout {
                    anchors.fill: parent
                    spacing: 0
                    
                    Item {
                        Layout.preferredWidth: 40
                        Layout.fillHeight: true
                        
                        // 展开图标
                        Image {
                            id: expandIcon
                            anchors.centerIn: parent
                            width: 18; height: 18
                            source: control.expandIconSource
                            sourceSize.width: 18
                            sourceSize.height: 18
                            opacity: sidebarExpanded ? 1.0 : 0.0
                            Behavior on opacity { NumberAnimation { duration: 200 } }
                        }
                        
                        // 收缩图标
                        Image {
                            id: collapseIcon
                            anchors.centerIn: parent
                            width: 18; height: 18
                            source: control.collapseIconSource
                            sourceSize.width: 18
                            sourceSize.height: 18
                            opacity: sidebarExpanded ? 0.0 : 1.0
                            Behavior on opacity { NumberAnimation { duration: 200 } }
                        }
                    }

                    Text {
                        text: control.labelText
                        color: "white"
                        font.pixelSize: 14
                        Layout.fillWidth: true
                        opacity: sidebarExpanded ? 1.0 : 0.0
                        clip: true
                        Layout.preferredWidth: sidebarExpanded ? -1 : 0
                        
                        Behavior on opacity { NumberAnimation { duration: 200 } }
                    }
                }
            }

            // 1. 收缩按钮
            SidebarButton {
                iconSource: "img/收缩.svg"
                expandIconSource: "img/收缩.svg"
                collapseIconSource: "img/展开.svg"
                labelText: "收起侧栏"
                onClicked: {
                    sidebarExpanded = !sidebarExpanded
                    sidebarWidth = sidebarExpanded ? 260 : 64
                }
            }

            // 2. 新建按钮
            SidebarButton {
                iconSource: "img/新建.svg"
                expandIconSource: "img/新建.svg"
                collapseIconSource: "img/新建.svg"
                labelText: "新建对话"
                isAccent: true
            }

            // 3. 对话列表
            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: ["如何使用Dify", "数字花园简介", "检索测试"]
                delegate: ItemDelegate {
                    id: listDel
                    width: sidebar.width - 24
                    height: 40
                    contentItem: RowLayout {
                        spacing: 0
                        Item {
                            Layout.preferredWidth: 40
                            Layout.fillHeight: true
                            Text {
                                anchors.centerIn: parent
                                text: "•"
                                color: listDel.hovered ? "white" : "#3f3f46"
                                font.pixelSize: 20
                            }
                        }
                        Text {
                            text: modelData; color: listDel.hovered ? "white" : "#a1a1aa"
                            font.pixelSize: 13; elide: Text.ElideRight
                            Layout.fillWidth: true
                            opacity: sidebarExpanded ? 1.0 : 0.0
                        }
                    }
                    background: Rectangle {
                        color: listDel.hovered ? "#1d1d20" : "transparent"
                        radius: 8
                    }
                }
            }

            // 4. 设置按钮 (底部)
            SidebarButton {
                iconSource: "img/设置.svg"
                expandIconSource: "img/设置.svg"
                collapseIconSource: "img/设置.svg"
                labelText: "设置"
            }
        }
    }

    // ------------------ 主对话区 ------------------
    Item {
        id: mainArea
        anchors.left: sidebar.right
        anchors.right: parent.right
        anchors.top: titleBar.bottom
        anchors.bottom: parent.bottom

        ListView {
            id: chatList
            anchors.fill: parent
            anchors.margins: 50
            anchors.bottomMargin: 140
            spacing: 32
            model: ListModel { id: messageModel }
            clip: true

            delegate: ColumnLayout {
                width: chatList.width - 20
                spacing: 12
                Text {
                    text: role === "user" ? "You" : "Digital Garden"
                    color: role === "user" ? "#71717a" : "#3b82f6"
                    font.bold: true; font.pixelSize: 12
                }
                Text {
                    text: content; color: "#e4e4e7"
                    font.pixelSize: 15; width: parent.width
                    wrapMode: Text.WordWrap
                    lineHeight: 1.4
                }
            }
        }

        // ------------------ 仿 Ollama 输入框 ------------------
        Rectangle {
            id: inputContainer
            width: Math.min(parent.width - 120, 800)
            height: Math.min(200, Math.max(56, inputField.implicitHeight + 24))
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 40
            color: "#18181b"
            radius: 24
            border.color: inputField.activeFocus ? "#3f3f46" : "#27272a"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 12
                spacing: 10

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.topMargin: 8
                    Layout.bottomMargin: 8
                    ScrollBar.vertical.policy: ScrollBar.AsNeeded
                    
                    TextArea {
                        id: inputField
                        placeholderText: "向数字花园发送消息..."
                        placeholderTextColor: "#52525b"
                        color: "white"
                        font.pixelSize: 15
                        background: null
                        wrapMode: Text.WordWrap
                        selectByMouse: true
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                // 单一发送按钮
                RoundButton {
                    id: sendButton
                    Layout.preferredWidth: 32
                    Layout.preferredHeight: 32
                    Layout.alignment: Qt.AlignVCenter
                    
                    contentItem: Item {
                        Image {
                            anchors.centerIn: parent
                            width: 16
                            height: 16
                            source: inputField.text.length > 0 ? "img/发送.svg" : "img/发送-Empty.svg"
                            sourceSize: Qt.size(16, 16)
                            opacity: 1.0
                        }
                    }
                    
                    background: Rectangle {
                        radius: 16
                        color: inputField.text.length > 0 ? "white" : "#27272a"
                        Behavior on color { ColorAnimation { duration: 200 } }
                    }
                    
                    onClicked: {
                        if (inputField.text.trim() !== "") {
                            messageModel.append({"role": "user", "content": inputField.text})
                            chatController.send_message(inputField.text)
                            inputField.clear()
                            chatList.positionViewAtEnd()
                        }
                    }
                }
            }
        }
    }

    // 后端连接
    Connections {
        target: chatController
        function onMessageReceived(msg) {
            messageModel.append({"role": "assistant", "content": msg})
            chatList.positionViewAtEnd()
        }
    }
}
