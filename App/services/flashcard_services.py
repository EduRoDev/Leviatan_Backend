from sqlalchemy.orm import Session
from App.Models.models import Flashcard

class FlashcardService:
    def __init__(self, db: Session):
        self.db = db
        
    def save_flashcard(self, flashcard_data: list, document_id: int) -> list[Flashcard]:
        flashcards_objects = []
        for item in flashcard_data:
            flashcard = Flashcard(
                question=item['subject'],
                answer=item['definition'],
                document_id=document_id
            )
            self.db.add(flashcard)
            flashcards_objects.append(flashcard)
        self.db.commit()
        return flashcards_objects
    
    def get_flashcards(self, document_id: int) -> list[Flashcard]:
        """
        Devuelve todas las flashcards asociadas a un documento.
        """
        return (
            self.db.query(Flashcard)
            .filter(Flashcard.document_id == document_id)
            .all()
        )