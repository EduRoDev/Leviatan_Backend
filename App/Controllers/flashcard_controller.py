from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.Utils.db_sessions import get_db
from App.Services.flashcard_services import FlashcardService
from App.Services.document_services import DocumentService
from App.Utils.auth_utils import get_current_user
from App.Utils.open_ai import OpenAIClient

router = APIRouter(prefix="/cards", tags=["cards"])

@router.get("/flash/{document_id}")
def get_cards(document_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    cards = FlashcardService(db).get_flashcards(document_id)
    if not cards:
        raise HTTPException(status_code=404, detail="Cards not found")
    
    return [
        {
            "id": c.id,
            "question": c.question,
            "answer": c.answer,
            "document_id": c.document_id
        }
        for c in cards
    ]
    
@router.post("/flash/create/{document_id}")
async def create_flashcards_for_document(document_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    document_services = DocumentService(db)
    flashcard_service = FlashcardService(db)
    open_ai_client = OpenAIClient()
    
    document = document_services.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    result = await open_ai_client.generate_flashcards(document.content)
    if not result or "data" not in result or "flashcards" not in result["data"]:
        raise HTTPException(status_code=500, detail="Error generating flashcards")
    
    flashcards_data = result["data"]["flashcards"]
    
    saved_flashcards = flashcard_service.save_flashcard(flashcards_data, document_id)
    if not saved_flashcards:
        raise HTTPException(status_code=500, detail="Error saving flashcards")
    
    return {
        "message": "Flashcards created successfully",
        "count": len(saved_flashcards),
        "flashcards": [
            {
                "id": fc.id,
                "question": fc.question,
                "answer": fc.answer
            }
            for fc in saved_flashcards
        ]
    }
