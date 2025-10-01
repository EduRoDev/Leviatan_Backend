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
        
        if not new_subject:
            raise HTTPException(status_code=400, detail="Subject could not be created")
        
        return {
            "id": new_subject.id,
            "name": new_subject.name,
            "description": new_subject.description,
        }
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user")
async def get_subjects_by_user(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    subject_service = SubjectService(db)
    
    try:
        subjects = subject_service.get_subjects_by_user(user_id)
        if not subjects:
            raise HTTPException(status_code=404, detail="No subjects found for this user")
        
        return [
            {
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
            } for subject in subjects
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
@router.get("/{subject_id}/documents")
async def get_documents_by_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
): 
    subject_service = SubjectService(db)
    try:
        subject = subject_service.get_subject_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")

        return subject.documents
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/test")
def test():
    return {"message": "Subject controller is working!"}