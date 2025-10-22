from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import os
from App.Utils.db_sessions import get_db
from App.Services.document_services import DocumentService
from App.Services.summary_services import SummaryService
from App.Services.flashcard_services import FlashcardService
from App.Services.subject_services import SubjectService
from App.Services.quiz_services import QuizService
from App.Utils.open_ai import OpenAIClient
from App.Utils.auth_utils import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("Public").resolve()

@router.post("/uploads/{subject_id}")
async def upload_and_analyze(
    subject_id: int,
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subject_service = SubjectService(db)
    doc_service = DocumentService(db)

    subject = subject_service.get_subject_by_id(subject_id)
    if not subject or subject.user_id != user_id:
        raise HTTPException(status_code=404, detail="Subject not found or access denied")
    
    new_doc = doc_service.save_document(file_path, subject_id)
    if not new_doc:
        raise HTTPException(status_code=500, detail="Error saving document")
    
    response = {
        "id": new_doc.id,
        "title": new_doc.title,
    }
    return {        
        **response,
        "message": "Document uploaded and saved successfully"
    }
    
    
@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
        document_service = DocumentService(db)
        document = document_service.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "file_path": document.file_path
        }
                
@router.get("/download/{doc_id}")
def download_file_by_id(doc_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    document_service = DocumentService(db)
    document = document_service.get_document(doc_id)
    if not document or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    filename = os.path.basename(document.file_path)
    return FileResponse(
        path=document.file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
    
@router.get("/view/{doc_id}")
def view_file(doc_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    document_service = DocumentService(db)
    document = document_service.get_document(doc_id)
    
    print(f"Document fetched: {document}")
    if not document or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    filename = os.path.basename(document.file_path)

    print(document)
    return FileResponse(
        path=document.file_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{filename}"
        }
    )
    
@router.get("/doc/prueba")
async def prueba():
    openai_client = OpenAIClient()
    response = await openai_client.prueba()
    return response

