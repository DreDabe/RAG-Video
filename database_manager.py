import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from logger_config import get_logger

logger = get_logger('database_manager')


class DatabaseManager:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.db_path = self.data_dir / "conversations.db"
        self.json_file = self.data_dir / "conversations.json"
        
        self._connection = None
        self._initialize_database()
    
    def _get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def _initialize_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                dify_conversation_id TEXT,
                is_deleted INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
            ON conversations(updated_at DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversations_is_deleted 
            ON conversations(is_deleted)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
            ON messages(conversation_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
            ON messages(timestamp)
        ''')
        
        conn.commit()
        logger.info(f"数据库初始化完成: {self.db_path}")
        
        self._check_and_migrate_data()
    
    def _check_and_migrate_data(self):
        if self.json_file.exists():
            cursor = self._get_connection().cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.info("检测到旧版JSON数据，开始迁移...")
                self._migrate_from_json()
    
    def _migrate_from_json(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            conversations = data.get('conversations', [])
            current_conversation_id = data.get('current_conversation_id', '')
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for conv in conversations:
                conv_id = conv.get('id', str(uuid.uuid4()))
                title = conv.get('title', '')
                created_at = conv.get('created_at', datetime.now().isoformat())
                updated_at = conv.get('updated_at', datetime.now().isoformat())
                
                cursor.execute('''
                    INSERT OR REPLACE INTO conversations 
                    (id, title, created_at, updated_at, is_deleted)
                    VALUES (?, ?, ?, ?, 0)
                ''', (conv_id, title, created_at, updated_at))
                
                messages = conv.get('messages', [])
                for msg in messages:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    timestamp = msg.get('timestamp', datetime.now().isoformat())
                    
                    cursor.execute('''
                        INSERT INTO messages (conversation_id, role, content, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (conv_id, role, content, timestamp))
            
            cursor.execute('''
                INSERT OR REPLACE INTO app_settings (key, value)
                VALUES ('current_conversation_id', ?)
            ''', (current_conversation_id,))
            
            conn.commit()
            
            backup_file = self.json_file.with_suffix('.json.backup')
            self.json_file.rename(backup_file)
            
            logger.info(f"数据迁移完成，已备份到: {backup_file}")
            logger.info(f"迁移了 {len(conversations)} 个对话")
            
        except Exception as e:
            logger.error(f"数据迁移失败: {e}")
            raise
    
    def create_conversation(self, title: str = '') -> str:
        conv_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (id, title, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, 0)
        ''', (conv_id, title, now, now))
        
        conn.commit()
        logger.debug(f"创建对话: {conv_id}")
        
        return conv_id
    
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at, updated_at, dify_conversation_id, is_deleted
            FROM conversations
            WHERE id = ? AND is_deleted = 0
        ''', (conv_id,))
        
        row = cursor.fetchone()
        if row:
            messages = self.get_messages(conv_id)
            return {
                'id': row['id'],
                'title': row['title'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'dify_conversation_id': row['dify_conversation_id'],
                'is_deleted': row['is_deleted'],
                'messages': messages
            }
        return None
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at, updated_at, dify_conversation_id, is_deleted
            FROM conversations
            WHERE is_deleted = 0
            ORDER BY updated_at DESC
        ''')
        
        return [
            {
                'id': row['id'],
                'title': row['title'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'dify_conversation_id': row['dify_conversation_id'],
                'is_deleted': row['is_deleted'],
                'messages': self.get_messages(row['id'])
            }
            for row in cursor.fetchall()
        ]
    
    def get_conversation_list(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, updated_at
            FROM conversations
            WHERE is_deleted = 0 AND title != ''
            ORDER BY updated_at DESC
        ''')
        
        return [
            {
                'id': row['id'],
                'title': row['title'],
                'updated_at': row['updated_at']
            }
            for row in cursor.fetchall()
        ]
    
    def update_conversation_title(self, conv_id: str, title: str) -> bool:
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE id = ? AND is_deleted = 0
        ''', (title, now, conv_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        
        if success:
            logger.debug(f"更新对话标题: {conv_id}")
        
        return success
    
    def delete_conversation(self, conv_id: str) -> bool:
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations
            SET is_deleted = 1, updated_at = ?
            WHERE id = ?
        ''', (now, conv_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        
        if success:
            logger.debug(f"删除对话: {conv_id}")
        
        return success
    
    def add_message(self, conv_id: str, role: str, content: str) -> int:
        timestamp = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ? AND is_deleted = 0
        ''', (timestamp, conv_id))
        
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (conv_id, role, content, timestamp))
        
        conn.commit()
        msg_id = cursor.lastrowid
        
        logger.debug(f"添加消息到对话 {conv_id}: {role}")
        
        return msg_id
    
    def get_messages(self, conv_id: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, role, content, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        ''', (conv_id,))
        
        return [
            {
                'id': row['id'],
                'role': row['role'],
                'content': row['content'],
                'timestamp': row['timestamp']
            }
            for row in cursor.fetchall()
        ]
    
    def update_dify_conversation_id(self, conv_id: str, dify_conv_id: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations
            SET dify_conversation_id = ?
            WHERE id = ? AND is_deleted = 0
        ''', (dify_conv_id, conv_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        
        if success:
            logger.debug(f"更新Dify对话ID: {conv_id} -> {dify_conv_id}")
        
        return success
    
    def get_dify_conversation_id(self, conv_id: str) -> Optional[str]:
        conv = self.get_conversation(conv_id)
        return conv['dify_conversation_id'] if conv else None
    
    def get_current_conversation_id(self) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT value FROM app_settings WHERE key = 'current_conversation_id'
        ''')
        
        row = cursor.fetchone()
        return row['value'] if row else ''
    
    def set_current_conversation_id(self, conv_id: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO app_settings (key, value)
            VALUES ('current_conversation_id', ?)
        ''', (conv_id,))
        
        conn.commit()
        logger.debug(f"设置当前对话ID: {conv_id}")
    
    def has_empty_title_conversation(self) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM conversations
            WHERE is_deleted = 0 AND (title = '' OR title IS NULL)
        ''')
        
        count = cursor.fetchone()[0]
        return count > 0
    
    def get_empty_title_conversation_id(self) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM conversations
            WHERE is_deleted = 0 AND (title = '' OR title IS NULL)
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        return row['id'] if row else ''
    
    def get_conversation_count(self) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM conversations WHERE is_deleted = 0
        ''')
        
        return cursor.fetchone()[0]
    
    def get_message_count(self, conv_id: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM messages WHERE conversation_id = ?
        ''', (conv_id,))
        
        return cursor.fetchone()[0]
