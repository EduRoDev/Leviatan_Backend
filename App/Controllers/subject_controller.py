from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from App.Utils.db_sessions import get_db
from App.Utils.auth_utils import get_current_user
from App.Services.subject_services import SubjectService

router = APIRouter(prefix="/subject", tags=["subject"])

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.post("/create")
async def create_subject(
    subject_data: SubjectCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    subject_service = SubjectService(db)
    
    try:
        new_subject = subject_service.create_subject(
            subject_data.name, 
            subject_data.description, 
            user_id
        )
        return {
            "id": new_subject.id,
            "name": new_subject.name,
            "description": new_subject.description,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/test")
def test():
    return {"message": "Subject controller is working!"}