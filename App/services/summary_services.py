from sqlalchemy.orm import Session
from App.Models.models import Summary

class SummaryService:
    def __init__(self, db: Session):
        self.db = db

    def save_summary(self, content: str, document_id: int) -> Summary:
        """
        Guarda un resumen en la base de datos.
        """
        summary = Summary(content=content, document_id=document_id)
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        return summary
    
    def get_summary(self, summary_id: int) -> Summary:
        return self.db.query(Summary).filter(Summary.id == summary_id).first()