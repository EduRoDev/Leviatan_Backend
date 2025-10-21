from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from App.Utils.db_sessions import get_db
from App.Utils.auth_utils import get_current_user
from App.Utils.open_ai import OpenAIClient
from App.Services.chat_services import ChatService
from App.Services.document_services import DocumentService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class MessageRequest(BaseModel):
    document_id: int
    message: str
    
class MessageResponse(BaseModel):
    id: int
    message: str
    response: str
    timestamp: str
    
class HistoryResponse(BaseModel):
    history: List[MessageResponse]
    document_title: Optional[str] = None
    
async def send_message(
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = current_user["id"]
        chat_service = ChatService(db)
        document_service = DocumentService(db)
        
        document = document_service.get_document(user_id, request.document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        history_entries = chat_service.get_chat_history(user_id, request.document_id, limit=10)
        chat_history = []
        for entry in reversed(history_entries):
            chat_history.append({"role": "user", "content": entry.message})
            chat_history.append({"role": "assistant", "content": entry.response})
            
        openai_client = OpenAIClient()
        response = await openai_client.chat_with_document(
            document_content=document.content,
            user_message=request.message,
            chat_history=chat_history
        )    
        
        chat_entry = chat_service.save_message(
            user_id=user_id,
            document_id=request.document_id,
            message=request.message,
            response=response
        )
        
        return MessageResponse(
            id=chat_entry.id,
            message=chat_entry.message,
            response=chat_entry.response,
            timestamp=chat_entry.timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")