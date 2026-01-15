import json
import uuid
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, Property
from logger_config import get_logger

logger = get_logger('conversation_manager')


class ConversationManager(QObject):
    conversationListChanged = Signal()
    currentConversationChanged = Signal()

    def __init__(self, data_dir=None):
        super().__init__()
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.conversations_file = self.data_dir / "conversations.json"
        self.conversations = []
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
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations = data.get('conversations', [])
                    # 清理空对话，只保留一个空对话
                    empty_conversations = [c for c in self.conversations if not c.get('title') or c['title'].strip() == '']
                    if len(empty_conversations) > 1:
                        # 保留最新的空对话，删除其他空对话
                        latest_empty = empty_conversations[0]
                        self.conversations = [c for c in self.conversations if c.get('title') and c['title'].strip() != ''] + [latest_empty]
                    
                    # 如果没有对话，创建一个新对话
                    if not self.conversations:
                        self.create_new_conversation()
                    
                    # 设置当前对话ID
                    saved_current_id = data.get('current_conversation_id')
                    if saved_current_id:
                        # 检查保存的对话ID是否仍然存在
                        if any(c['id'] == saved_current_id for c in self.conversations):
                            self._current_conversation_id = saved_current_id
                        else:
                            # 如果保存的对话不存在，使用第一个对话
                            self._current_conversation_id = self.conversations[0]['id'] if self.conversations else None
                    else:
                        self._current_conversation_id = self.conversations[0]['id'] if self.conversations else None
            except Exception as e:
                logger.error(f"加载对话失败: {e}")
                self.conversations = []
                self._current_conversation_id = None
                self.create_new_conversation()
        else:
            self.conversations = []
            self._current_conversation_id = None
            self.create_new_conversation()
        
        self.conversationListChanged.emit()

    def save_conversations(self):
        try:
            data = {
                'conversations': self.conversations,
                'current_conversation_id': self.current_conversation_id
            }
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存对话失败: {e}")

    @Slot(result=str)
    def create_new_conversation(self):
        conversation_id = str(uuid.uuid4())
        new_conversation = {
            'id': conversation_id,
            'title': '',
            'messages': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.conversations.insert(0, new_conversation)
        self._current_conversation_id = conversation_id
        self.save_conversations()
        self.conversationListChanged.emit()
        self.currentConversationChanged.emit()
        
        return conversation_id

    @Slot(str, str, str)
    def add_message(self, conversation_id, role, content):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            conversation['messages'].append(message)
            
            if not conversation['title'] and role == 'user':
                conversation['title'] = content
            
            conversation['updated_at'] = datetime.now().isoformat()
            
            self._sort_conversations()
            self.save_conversations()
            self.conversationListChanged.emit()

    @Slot(str, str)
    def update_title(self, conversation_id, title):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation['title'] = title
            conversation['updated_at'] = datetime.now().isoformat()
            
            self._sort_conversations()
            self.save_conversations()
            self.conversationListChanged.emit()

    @Slot(str)
    def load_conversation(self, conversation_id):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self._current_conversation_id = conversation_id
            self.currentConversationChanged.emit()
            
            return conversation
        return None

    @Slot(str)
    def delete_conversation(self, conversation_id):
        logger.debug(f"删除对话: {conversation_id}")
        
        conversation_id = str(conversation_id)
        
        if not conversation_id or conversation_id == "":
            logger.error("conversation_id 为空或None")
            return
        
        logger.debug(f"删除前对话数量: {len(self.conversations)}")
        for i, conv in enumerate(self.conversations):
            logger.debug(f"  对话 {i}: ID={conv['id']}, Title={conv.get('title', 'N/A')}")
        
        self.conversations = [c for c in self.conversations if c['id'] != conversation_id]
        
        logger.debug(f"删除后对话数量: {len(self.conversations)}")
        
        if self._current_conversation_id == conversation_id:
            if self.conversations:
                self._current_conversation_id = self.conversations[0]['id']
                logger.debug(f"新当前对话ID: {self._current_conversation_id}")
            else:
                self._current_conversation_id = None
                logger.info("没有剩余对话，创建新对话")
                self.create_new_conversation()
        
        logger.debug("保存对话到文件...")
        self.save_conversations()
        logger.debug("发送信号...")
        self.conversationListChanged.emit()
        self.currentConversationChanged.emit()

    @Slot(str, str)
    def rename_conversation(self, conversation_id, new_title):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation['title'] = new_title
            conversation['updated_at'] = datetime.now().isoformat()
            
            self._sort_conversations()
            self.save_conversations()
            self.conversationListChanged.emit()

    def get_conversation(self, conversation_id):
        for conversation in self.conversations:
            if conversation['id'] == conversation_id:
                return conversation
        return None

    def get_current_conversation(self):
        if self.current_conversation_id:
            return self.get_conversation(self.current_conversation_id)
        return None

    def _sort_conversations(self):
        self.conversations.sort(
            key=lambda x: x['updated_at'],
            reverse=True
        )

    @Slot(result=list)
    def get_conversation_list(self):
        return [
            {
                'id': c['id'],
                'title': c['title'],
                'updated_at': c['updated_at']
            }
            for c in self.conversations
            if c.get('title') and c['title'].strip() != ''
        ]

    @Slot(result=list)
    def get_current_messages(self):
        conversation = self.get_current_conversation()
        if conversation:
            return conversation['messages']
        return []
    
    @Slot(result=bool)
    def has_messages(self):
        return False
    
    @Slot(result=bool)
    def has_empty_title_conversation(self):
        for conv in self.conversations:
            if not conv.get('title') or conv['title'].strip() == '':
                return True
        return False
    
    @Slot(result=str)
    def get_empty_title_conversation_id(self):
        for conv in self.conversations:
            if not conv.get('title') or conv['title'].strip() == '':
                return conv['id']
        return ""
