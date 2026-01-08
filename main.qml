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
    property bool settingsVisible: false
    property string activeView: "chat"

    function loadConversations() {
        console.log("Loading conversations...")
        conversationModel.clear()
        var list = conversationManager.get_conversation_list()
        console.log("Conversation list:", list.length, "items")
        for (var i = 0; i < list.length; i++) {
            console.log("Adding conversation:", list[i].title)
            conversationModel.append(list[i])
        }
    }

    function loadMessages() {
        console.log("Loading messages for conversation:", conversationManager.current_conversation_id)
        messageModel.clear()
        var messages = conversationManager.get_current_messages()
        console.log("Messages count:", messages.length)
        for (var i = 0; i < messages.length; i++) {
            console.log("Adding message:", messages[i].role, messages[i].content.substring(0, 20))
            messageModel.append(messages[i])
        }
        chatList.positionViewAtEnd()
    }

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
                property string viewTarget: "" // 目标视图

                Layout.fillWidth: true
                Layout.preferredHeight: 40
                
                background: Rectangle {
                    color: control.pressed ? "#3f3f46" : (control.hovered || (control.viewTarget !== "" && window.activeView === control.viewTarget) ? "#1d1d20" : "transparent")
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
                viewTarget: "chat"
                onClicked: {
                    if (!conversationManager.has_messages()) {
                        conversationManager.create_new_conversation()
                        window.activeView = "chat"
                        loadMessages()
                    }
                }
            }

            // 3. 对话列表
            ListView {
                id: conversationList
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: ListModel { id: conversationModel }
                
                Component.onCompleted: {
                    loadConversations()
                }
                
                Connections {
                    target: conversationManager
                    function onConversationListChanged() {
                        loadConversations()
                    }
                }
                
                delegate: ItemDelegate {
                    id: listDel
                    width: sidebar.width - 24
                    height: 40
                    hoverEnabled: true
                    
                    property bool isEditing: false
                    
                    onClicked: {
                        if (!isEditing) {
                            console.log("Clicked conversation:", model.id, model.title)
                            conversationManager.load_conversation(model.id)
                            loadMessages()
                        }
                    }
                    
                    background: Rectangle {
                        color: (listDel.hovered || String(model.id) === String(conversationManager.current_conversation_id)) ? "#1d1d20" : "transparent"
                        radius: 8
                    }
                    
                    contentItem: RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 10
                        anchors.rightMargin: 8
                        spacing: 0
                        
                        Item {
                            Layout.preferredWidth: 40
                            Layout.fillHeight: true
                            Text {
                                anchors.centerIn: parent
                                text: "•"
                                color: (listDel.hovered || String(model.id) === String(conversationManager.current_conversation_id)) ? "white" : "#3f3f46"
                                font.pixelSize: 20
                                visible: sidebarExpanded
                            }
                        }
                        
                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            visible: sidebarExpanded
                            
                            Text {
                                id: titleText
                                anchors.fill: parent
                                anchors.verticalCenter: parent.verticalCenter
                                text: model.title
                                color: (listDel.hovered || String(model.id) === String(conversationManager.current_conversation_id)) ? "white" : "#a1a1aa"
                                font.pixelSize: 13
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                                visible: !isEditing
                            }
                            
                            TextField {
                                id: editField
                                anchors.fill: parent
                                text: model.title
                                visible: isEditing
                                color: "white"
                                font.pixelSize: 13
                                selectionColor: "#3b82f6"
                                background: Rectangle {
                                    color: "#09090b"
                                    radius: 4
                                    border.color: "#3b82f6"
                                    border.width: 1
                                }
                                
                                Component.onCompleted: {
                                    if (visible) forceActiveFocus()
                                }
                                
                                onAccepted: {
                                    if (text.trim() !== "") {
                                        conversationManager.rename_conversation(model.id, text.trim())
                                    }
                                    isEditing = false
                                }
                                
                                Keys.onEscapePressed: {
                                    text = model.title
                                    isEditing = false
                                }
                            }
                        }
                        
                        Button {
                            id: moreBtn
                            Layout.preferredWidth: 24
                            Layout.fillHeight: true
                            visible: sidebarExpanded && listDel.hovered && !isEditing
                            opacity: 0.7
                            
                            background: null
                            
                            contentItem: Text {
                                text: "..."
                                color: (listDel.hovered || String(model.id) === String(conversationManager.current_conversation_id)) ? "white" : "#a1a1aa"
                                font.pixelSize: 16
                            }
                            
                            onClicked: {
                                conversationToDelete = model.id
                                actionMenu.open()
                            }
                            
                            Menu {
                                id: actionMenu
                                y: moreBtn.height
                                x: -width + moreBtn.width
                                
                                background: Rectangle {
                                    implicitWidth: 120
                                    color: "#1e1e20"
                                    border.color: "#2d2d30"
                                    radius: 8
                                }
                                
                                MenuItem {
                                    text: "重命名"
                                    contentItem: RowLayout {
                                        spacing: 10
                                        Image { source: "img/重命名.svg"; sourceSize: Qt.size(14, 14) }
                                        Text { text: "重命名"; color: "white"; font.pixelSize: 12 }
                                    }
                                    onTriggered: {
                                        isEditing = true
                                        editField.forceActiveFocus()
                                        editField.selectAll()
                                    }
                                    background: Rectangle {
                                        color: parent.highlighted ? "#27272a" : "transparent"
                                        radius: 4
                                    }
                                }
                                
                                MenuItem {
                                    text: "删除"
                                    contentItem: RowLayout {
                                        spacing: 10
                                        Image { source: "img/删除.svg"; sourceSize: Qt.size(14, 14) }
                                        Text { text: "删除记录"; color: "#ef4444"; font.pixelSize: 12 }
                                    }
                                    onTriggered: {
                                        deleteConfirmPopup.open()
                                    }
                                    background: Rectangle {
                                        color: parent.highlighted ? "#27272a" : "transparent"
                                        radius: 4
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // 3. 更新知识库按钮
            SidebarButton {
                iconSource: "img/更新.svg"
                expandIconSource: "img/更新.svg"
                collapseIconSource: "img/更新.svg"
                labelText: "更新知识库"
                viewTarget: "update"
                onClicked: {
                    window.activeView = "update"
                }
            }

            // 4. 设置按钮 (底部)
            SidebarButton {
                iconSource: "img/设置.svg"
                expandIconSource: "img/设置.svg"
                collapseIconSource: "img/设置.svg"
                labelText: "设置"
                viewTarget: "settings"
                onClicked: {
                    window.activeView = "settings"
                }
            }
        }
    }

    // --- 删除确认弹窗 ---
    Popup {
        id: deleteConfirmPopup
        anchors.centerIn: parent
        width: 300
        height: 150
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        
        property string conversationToDelete: ""
        
        background: Rectangle {
            color: "#18181b"
            border.color: "#27272a"
            radius: 12
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15
            
            Text {
                text: "确定要删除这段对话吗？"
                color: "white"
                font.pixelSize: 15
                font.weight: Font.Medium
                Layout.alignment: Qt.AlignHCenter
            }
            Text {
                text: "此操作不可撤销。"
                color: "#71717a"
                font.pixelSize: 12
                Layout.alignment: Qt.AlignHCenter
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 10
                spacing: 12
                
                Button {
                    Layout.fillWidth: true
                    text: "取消"
                    onClicked: deleteConfirmPopup.close()
                    
                    background: Rectangle { 
                        color: "#27272a"
                        radius: 8
                    }
                    
                    contentItem: Text {
                        text: "取消"
                        color: "white"
                        font.pixelSize: 14
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "删除"
                    onClicked: {
                        conversationManager.delete_conversation(conversationToDelete)
                        deleteConfirmPopup.close()
                    }
                    
                    background: Rectangle { 
                        color: "#ef4444"
                        radius: 8
                    }
                    
                    contentItem: Text {
                        text: "删除"
                        color: "white"
                        font.pixelSize: 14
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
    }

    // --- 主对话区 ---
    Item {
        id: mainArea
        anchors.left: sidebar.right
        anchors.right: parent.right
        anchors.top: titleBar.bottom
        anchors.bottom: parent.bottom
        
        ListModel { id: messageModel }

        // ================== 视图 1: 聊天界面 ==================
        Item {
            id: chatView
            anchors.fill: parent
            visible: activeView === "chat"

            property bool isGenerating: false
            property string currentTitle: ""

            Connections {
                target: chatController
                function onGenerationStarted() {
                    chatView.isGenerating = true
                }
                function onGenerationStopped() {
                    chatView.isGenerating = false
                }
            }
            
            Connections {
                target: conversationManager
                function onCurrentConversationChanged() {
                    loadMessages()
                }
            }
            
            Connections {
                target: chatController
                function onMessageAdded() {
                    loadMessages()
                }
                function onMessageReceived(msg) {
                    console.log("Message received:", msg)
                }
            }

            ListView {
                id: chatList
                anchors.fill: parent
                anchors.margins: 50
                anchors.bottomMargin: 140
                spacing: 32
                model: messageModel
                clip: true

                delegate: Item {
                    width: chatList.width - 20
                    height: messageColumn.implicitHeight

                    ColumnLayout {
                        id: messageColumn
                        anchors.fill: parent
                        spacing: 12

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12
                            layoutDirection: role === "user" ? Qt.RightToLeft : Qt.LeftToRight

                            Text {
                                text: role === "user" ? "You" : "Digital Garden"
                                color: role === "user" ? "#71717a" : "#3b82f6"
                                font.bold: true
                                font.pixelSize: 12
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 1
                            color: "#1d1d20"
                            visible: index > 0
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12
                            layoutDirection: role === "user" ? Qt.RightToLeft : Qt.LeftToRight

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredWidth: role === "user" ? 0.7 : 1.0
                                color: role === "user" ? "#27272a" : "transparent"
                                radius: 12
                                implicitHeight: messageText.implicitHeight + 20

                                Text {
                                    id: messageText
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    text: role === "assistant" ? chatController.format_markdown(content) : content
                                    textFormat: role === "assistant" ? Text.RichText : Text.PlainText
                                    color: "#e4e4e7"
                                    font.pixelSize: 15
                                    wrapMode: Text.WordWrap
                                    lineHeight: 1.4
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                        }
                    }
                }
            }

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
                            
                            Keys.onPressed: function(event) {
                                if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                    if (event.modifiers & Qt.ShiftModifier) {
                                        inputField.insert(inputField.cursorPosition, "\n")
                                    } else {
                                        if (inputField.text.trim() !== "" && !chatView.isGenerating) {
                                            chatController.send_message(inputField.text)
                                            inputField.clear()
                                        }
                                    }
                                    event.accepted = true
                                }
                            }
                        }
                    }

                    RoundButton {
                        id: sendButton
                        Layout.preferredWidth: 32
                        Layout.preferredHeight: 32
                        Layout.alignment: Qt.AlignVCenter
                        enabled: inputField.text.length > 0 || chatView.isGenerating
                        
                        contentItem: Item {
                            Image {
                                id: sendIcon
                                anchors.centerIn: parent
                                width: 16
                                height: 16
                                source: chatView.isGenerating ? "img/停止.svg" : (inputField.text.length > 0 ? "img/发送.svg" : "img/发送-Empty.svg")
                                sourceSize: Qt.size(16, 16)
                                opacity: 1.0
                            }
                            
                            BusyIndicator {
                                id: loadingIndicator
                                anchors.centerIn: parent
                                width: 16
                                height: 16
                                running: chatView.isGenerating
                                visible: chatView.isGenerating
                            }
                        }
                        
                        background: Rectangle {
                            radius: 16
                            color: (chatView.isGenerating || inputField.text.length > 0) ? "white" : "#27272a"
                            Behavior on color { ColorAnimation { duration: 200 } }
                        }
                        
                        onClicked: {
                            if (chatView.isGenerating) {
                                chatController.stop_generation()
                            } else if (inputField.text.trim() !== "") {
                                chatController.send_message(inputField.text)
                                inputField.clear()
                                chatList.positionViewAtEnd()
                            }
                        }
                    }
                }
            }
        }

        // ================== 视图 2: 设置界面 ==================
        Item {
            id: settingsView
            anchors.fill: parent
            visible: activeView === "settings"
            
            Component.onCompleted: {
                Qt.callLater(function() {
                    datasetApiField.fieldText = configManager.get_dataset_api()
                    datasetIdField.fieldText = configManager.get_dataset_id()
                    appUrlField.fieldText = configManager.get_app_url()
                    appApiField.fieldText = configManager.get_app_api()
                    languageCombo.currentIndex = languageCombo.find(configManager.get_language())
                })
            }
            
            Connections {
                target: configManager
                function onConfigChanged() {
                    Qt.callLater(function() {
                        datasetApiField.fieldText = configManager.get_dataset_api()
                        datasetIdField.fieldText = configManager.get_dataset_id()
                        appUrlField.fieldText = configManager.get_app_url()
                        appApiField.fieldText = configManager.get_app_api()
                        languageCombo.currentIndex = languageCombo.find(configManager.get_language())
                    })
                }
            }
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 40
                spacing: 24

                Text { text: "应用设置"; color: "white"; font.pixelSize: 24; font.weight: Font.Bold }

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    ScrollBar.vertical.policy: ScrollBar.AsNeeded

                    ColumnLayout {
                        width: settingsView.width - 80
                        spacing: 20
                        
                        component SettingInput : ColumnLayout {
                            property string label: ""
                            property string configKey: ""
                            property string configType: "dify"
                            property alias fieldText: settingField.text
                            Layout.fillWidth: true
                            spacing: 8
                            Text { text: label; color: "#a1a1aa"; font.pixelSize: 12 }
                            TextField {
                                id: settingField
                                Layout.fillWidth: true
                                color: "white"
                                font.pixelSize: 13
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 12
                                rightPadding: 12
                                onTextChanged: {
                                    if (configType === "dify") {
                                        if (configKey === "dataset_api") configManager.set_dataset_api(text)
                                        if (configKey === "dataset_id") configManager.set_dataset_id(text)
                                        if (configKey === "app_url") configManager.set_app_url(text)
                                        if (configKey === "app_api") configManager.set_app_api(text)
                                    } else if (configType === "general") {
                                        if (configKey === "language") configManager.set_language(text)
                                    }
                                }
                                background: Rectangle {
                                    color: "#09090b"
                                    radius: 8
                                    border.color: parent.activeFocus ? "#3b82f6" : "#27272a"
                                    border.width: parent.activeFocus ? 2 : 1
                                }
                            }
                        }

                        SettingInput { 
                            label: "知识库 API (Dataset)"; 
                            configKey: "dataset_api"
                            configType: "dify"
                            id: datasetApiField
                        }
                        SettingInput { 
                            label: "知识库 ID"; 
                            configKey: "dataset_id"
                            configType: "dify"
                            id: datasetIdField
                        }
                        SettingInput { 
                            label: "Dify 应用 URL"; 
                            configKey: "app_url"
                            configType: "dify"
                            id: appUrlField
                        }
                        SettingInput { 
                            label: "Dify 应用 API (App Key)"; 
                            configKey: "app_api"
                            configType: "dify"
                            id: appApiField
                        }

                        Text { text: "通用"; color: "#3b82f6"; font.pixelSize: 14; Layout.topMargin: 20 }
                        RowLayout {
                            Text { text: "语言设置"; color: "#a1a1aa"; Layout.fillWidth: true }
                            ComboBox { 
                                id: languageCombo
                                model: ["简体中文", "English"]
                                Layout.preferredWidth: 150
                                onActivated: {
                                    configManager.set_language(currentText)
                                }
                                delegate: ItemDelegate {
                                    width: languageCombo.width
                                    contentItem: Text { text: modelData; color: "white"; verticalAlignment: Text.AlignVCenter }
                                    background: Rectangle { color: hovered ? "#27272a" : "#18181b" }
                                }
                                contentItem: Text { text: languageCombo.displayText; color: "white"; leftPadding: 12; verticalAlignment: Text.AlignVCenter }
                                background: Rectangle { color: "#09090b"; radius: 8; border.color: "#27272a" }
                            }
                        }
                    }
                }
            }
        }

        // ================== 视图 3: 更新知识库界面 (优化版) ==================
        Item {
            id: updateView
            anchors.fill: parent
            visible: activeView === "update"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 40
                anchors.topMargin: 30
                spacing: 16

                Text { 
                    text: "更新知识库"; 
                    color: "white"; 
                    font.pixelSize: 24; 
                    font.weight: Font.Bold;
                    Layout.bottomMargin: 10
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 20
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        spacing: 8
                        Text { text: "视频平台"; color: "#a1a1aa"; font.pixelSize: 12 }
                        ComboBox { 
                            id: platformCombo
                            model: ["Bilibili"]
                            Layout.fillWidth: true
                            Layout.preferredHeight: 40
                            delegate: ItemDelegate {
                                width: platformCombo.width
                                contentItem: Text { text: modelData; color: "white"; verticalAlignment: Text.AlignVCenter }
                                background: Rectangle { color: hovered ? "#27272a" : "#18181b" }
                            }
                            contentItem: Text { text: platformCombo.displayText; color: "white"; leftPadding: 12; verticalAlignment: Text.AlignVCenter }
                            background: Rectangle { color: "#09090b"; radius: 8; border.color: "#27272a" }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        spacing: 8
                        Text { text: "类型"; color: "#a1a1aa"; font.pixelSize: 12 }
                        ComboBox { 
                            id: typeCombo
                            model: ["视频", "收藏夹"]
                            Layout.fillWidth: true
                            Layout.preferredHeight: 40
                            delegate: ItemDelegate {
                                width: typeCombo.width
                                contentItem: Text { text: modelData; color: "white"; verticalAlignment: Text.AlignVCenter }
                                background: Rectangle { color: hovered ? "#27272a" : "#18181b" }
                            }
                            contentItem: Text { text: typeCombo.displayText; color: "white"; leftPadding: 12; verticalAlignment: Text.AlignVCenter }
                            background: Rectangle { color: "#09090b"; radius: 8; border.color: "#27272a" }
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Text { text: "地址（URL）"; color: "#a1a1aa"; font.pixelSize: 12 }
                    TextField { 
                        text: "https://www.bilibili.com/medialist/play/ml387412427"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: "white"
                        font.pixelSize: 13
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 12
                        background: Rectangle {
                            color: "#09090b"
                            radius: 8
                            border.color: parent.activeFocus ? "#3b82f6" : "#27272a"
                            border.width: parent.activeFocus ? 2 : 1
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 8
                    Text { text: "Cookie (用于平台授权)"; color: "#a1a1aa"; font.pixelSize: 12 }
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        ScrollBar.vertical.policy: ScrollBar.AsNeeded
                        TextArea {
                            placeholderText: "粘贴视频平台 Cookie 于此..."
                            color: "white"
                            font.family: "Consolas, Monospace"
                            font.pixelSize: 13
                            background: Rectangle { color: "#18181b"; radius: 8; border.color: "#27272a" }
                            wrapMode: TextArea.Wrap
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 8
                    Text { text: "运行日志"; color: "#a1a1aa"; font.pixelSize: 12 }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#000000"
                        radius: 8
                        border.color: "#1d1d20"
                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 10
                            ScrollBar.vertical.policy: ScrollBar.AsNeeded
                            TextArea {
                                readOnly: true
                                text: "> 等待任务启动...\n> 准备更新知识库..."
                                color: "#10b981"
                                font.family: "Consolas, Monospace"
                                font.pixelSize: 12
                                background: null
                            }
                        }
                    }
                }

                Button {
                    id: runUpdateBtn
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: 260
                    Layout.preferredHeight: 45
                    Layout.topMargin: 10
                    Layout.bottomMargin: 10

                    contentItem: Text {
                        text: "开始更新知识库"
                        color: "white"
                        font.weight: Font.Medium
                        font.pixelSize: 16
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: runUpdateBtn.hovered ? "#3f3f46" : "#27272a"
                        radius: 8
                        border.color: "#3f3f46"
                        border.width: 1
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                }
            }
        }
    }
}
