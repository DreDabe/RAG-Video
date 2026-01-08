import json
import uuid
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, Property


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
                    self._current_conversation_id = None
            except Exception as e:
                print(f"Error loading conversations: {e}")
                self.conversations = []
                self._current_conversation_id = None
        else:
            self.conversations = []
            self._current_conversation_id = None
        
        if not self.conversations:
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
            print(f"Error saving conversations: {e}")

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
        print(f"=== Delete Conversation Called ===")
        print(f"Conversation ID to delete (raw): {conversation_id}")
        print(f"Conversation ID type: {type(conversation_id)}")
        
        conversation_id = str(conversation_id)
        print(f"Conversation ID to delete (converted): {conversation_id}")
        print(f"Conversation ID type (converted): {type(conversation_id)}")
        
        if not conversation_id or conversation_id == "":
            print("ERROR: conversation_id is None or empty!")
            return
        
        print(f"Current conversations before delete: {len(self.conversations)}")
        for i, conv in enumerate(self.conversations):
            print(f"  Conversation {i}: ID={conv['id']}, Title={conv.get('title', 'N/A')}")
        
        self.conversations = [c for c in self.conversations if c['id'] != conversation_id]
        
        print(f"Current conversations after delete: {len(self.conversations)}")
        
        if self._current_conversation_id == conversation_id:
            if self.conversations:
                self._current_conversation_id = self.conversations[0]['id']
                print(f"New current conversation ID: {self._current_conversation_id}")
            else:
                self._current_conversation_id = None
                print("Creating new conversation because no conversations left")
                self.create_new_conversation()
        
        print("Saving conversations to file...")
        self.save_conversations()
        print("Emitting signals...")
        self.conversationListChanged.emit()
        self.currentConversationChanged.emit()
        print("=== Delete Conversation Completed ===")

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
