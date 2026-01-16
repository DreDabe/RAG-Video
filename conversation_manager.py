import uuid
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, Property
from database_manager import DatabaseManager
from logger_config import get_logger

logger = get_logger('conversation_manager')


class ConversationManager(QObject):
    conversationListChanged = Signal()
    currentConversationChanged = Signal()

    def __init__(self, data_dir=None):
        super().__init__()
        self.db = DatabaseManager(data_dir)
        self._current_conversation_id = None
        
        self.load_conversations()
    
    @Property(str, notify=currentConversationChanged)
    def current_conversation_id(self):
        return self._current_conversation_id
    
    @current_conversation_id.setter
    def current_conversation_id(self, value):
        if self._current_conversation_id != value:
            self._current_conversation_id = value
            self.currentConversationChanged.emit()

    def load_conversations(self):
        try:
            saved_current_id = self.db.get_current_conversation_id()
            
            if self.db.get_conversation_count() == 0:
                logger.info("没有找到对话，创建新对话")
                self.create_new_conversation()
            else:
                if saved_current_id and self.db.get_conversation(saved_current_id):
                    self._current_conversation_id = saved_current_id
                else:
                    first_conv = self.db.get_all_conversations()
                    if first_conv:
                        self._current_conversation_id = first_conv[0]['id']
                    else:
                        self.create_new_conversation()
            
            self.conversationListChanged.emit()
            
        except Exception as e:
            logger.error(f"加载对话失败: {e}")
            self._current_conversation_id = None
            self.create_new_conversation()

    @Slot(result=str)
    def create_new_conversation(self):
        conversation_id = self.db.create_conversation('')
        self._current_conversation_id = conversation_id
        self.db.set_current_conversation_id(conversation_id)
        self.conversationListChanged.emit()
        self.currentConversationChanged.emit()
        
        logger.debug(f"创建新对话: {conversation_id}")
        
        return conversation_id

    @Slot(str, str, str)
    def add_message(self, conversation_id, role, content):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self.db.add_message(conversation_id, role, content)
            
            if not conversation['title'] and role == 'user':
                self.db.update_conversation_title(conversation_id, content)
            
            self.conversationListChanged.emit()
            logger.debug(f"添加消息到对话 {conversation_id}: {role}")

    @Slot(str, str)
    def update_title(self, conversation_id, title):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self.db.update_conversation_title(conversation_id, title)
            self.conversationListChanged.emit()
            logger.debug(f"更新对话标题: {conversation_id} -> {title}")

    @Slot(str)
    def load_conversation(self, conversation_id):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self._current_conversation_id = conversation_id
            self.db.set_current_conversation_id(conversation_id)
            self.currentConversationChanged.emit()
            
            return conversation
        return None

    @Slot(str)
    def delete_conversation(self, conversation_id):
        logger.debug(f"删除对话: {conversation_id}")
        
        conversation_id = str(conversation_id)
        
        if not conversation_id or conversation_id == "":
            logger.error("conversation_id为空")
            return
        
        self.db.delete_conversation(conversation_id)
        
        if self._current_conversation_id == conversation_id:
            first_conv = self.db.get_all_conversations()
            if first_conv:
                self._current_conversation_id = first_conv[0]['id']
                self.db.set_current_conversation_id(self._current_conversation_id)
                logger.debug(f"切换到新对话: {self._current_conversation_id}")
            else:
                self._current_conversation_id = None
                logger.debug("没有对话了，创建新对话")
                self.create_new_conversation()
        
        self.conversationListChanged.emit()
        self.currentConversationChanged.emit()

    @Slot(str, str)
    def rename_conversation(self, conversation_id, new_title):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self.db.update_conversation_title(conversation_id, new_title)
            self.conversationListChanged.emit()
            logger.debug(f"重命名对话: {conversation_id} -> {new_title}")

    def get_conversation(self, conversation_id):
        return self.db.get_conversation(conversation_id)

    def get_current_conversation(self):
        if self.current_conversation_id:
            return self.get_conversation(self.current_conversation_id)
        return None

    def _sort_conversations(self):
        pass

    @Slot(result=list)
    def get_conversation_list(self):
        return self.db.get_conversation_list()

    @Slot(result=list)
    def get_current_messages(self):
        conversation = self.get_current_conversation()
        if conversation:
            return conversation.get('messages', [])
        return []
    
    @Slot(result=bool)
    def has_messages(self):
        return False
    
    @Slot(result=bool)
    def has_empty_title_conversation(self):
        return self.db.has_empty_title_conversation()
    
    @Slot(result=str)
    def get_empty_title_conversation_id(self):
        return self.db.get_empty_title_conversation_id()
    
    def update_dify_conversation_id(self, conversation_id, dify_conversation_id):
        self.db.update_dify_conversation_id(conversation_id, dify_conversation_id)
        logger.debug(f"更新Dify对话ID: {conversation_id} -> {dify_conversation_id}")
    
    def get_dify_conversation_id(self, conversation_id):
        return self.db.get_dify_conversation_id(conversation_id)
