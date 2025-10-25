from sqlalchemy.orm import Session
from App.Models.models import ChatHistory, Document
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ChatService: 
    def __init__(self, db: Session):
        self.db = db
        
    def save_message(self, user_id: int, document_id: int, message: str, response: str) -> ChatHistory:
        try:
            chat_entry = ChatHistory(
                user_id=user_id,
                document_id=document_id,
                message=message,
                response=response
            )
            
            self.db.add(chat_entry)
            self.db.commit()
            self.db.refresh(chat_entry)
            return chat_entry
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving message: {e}")
            raise
        
    def get_chat_history(self, user_id:int, document_id:int, limit: int = 20) -> List[ChatHistory]:
        try:
            chat_history = self.db.query(ChatHistory).filter(
                ChatHistory.document_id == document_id,
                ChatHistory.user_id == user_id
            ).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
            
            return chat_history
        
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            raise
        
    def clear_chat_history(self, user_id:int, document_id:int) -> bool:
        try:
            self.db.query(ChatHistory).filter(
                ChatHistory.document_id == document_id,
                ChatHistory.user_id == user_id
            ).delete()
            self.db.commit()
            return True
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error clearing chat history: {e}")
            return False    
        
            
            
                