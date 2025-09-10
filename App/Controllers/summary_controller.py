from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from App.Utils.db_sessions import get_db
from App.Services.summary_services import SummaryService

router = APIRouter(prefix="/summary", tags=["summary"])

@router.get("/resumen/{document_id}")
def get_summary(document_id: int, db: Session = Depends(get_db)):
    summary = SummaryService(db).get_summary_document_id(document_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary