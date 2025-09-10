from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from App.Utils.db_sessions import get_db
from App.Services.flashcard_services import FlashcardService

router = APIRouter(prefix="/cards", tags=["cards"])

@router.get("/flash/{document_id}")
def get_cards(document_id: int, db: Session = Depends(get_db)):
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