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
from App.Services.quiz_services import QuizService
from App.Utils.open_ai import OpenAIClient
from App.Utils.auth_utils import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("Public").resolve()

@router.post("/uploads")
async def upload_and_analyze(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc_service = DocumentService(db)
    summary_service = SummaryService(db)
    flashcard_service = FlashcardService(db)
    quiz_service = QuizService(db)

    new_doc = doc_service.save_document(file_path, user_id)

    openai_client = OpenAIClient()
    ai_response, meta = await openai_client.analyze_text_parallel(new_doc.content)
    
    if not ai_response:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {meta.get('error', 'Unknown error')}")

    summary_obj = summary_service.save_summary(ai_response["summary"], new_doc.id)
    flashcards_objs = flashcard_service.save_flashcard(ai_response["flashcards"], new_doc.id)
    quiz_obj = quiz_service.save_quiz(ai_response["quiz"], new_doc.id)

    return {
        "document": {"id": new_doc.id, "title": new_doc.title},
        "summary": {"id": summary_obj.id, "content": summary_obj.content},
        "flashcards": [{"id": fc.id, "question": fc.question, "answer": fc.answer} for fc in flashcards_objs],
        "quiz": {
            "id": quiz_obj.id,
            "title": quiz_obj.title,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "correct_option": q.correct_option,
                    "options": [opt.text for opt in q.options]
                }
                for q in quiz_obj.questions
            ]
        },
        "meta": meta
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
def view_file(doc_id: int, db: Session = Depends(get_db)):
    document_service = DocumentService(db)
    document = document_service.get_document(doc_id)
    
    print(f"Document fetched: {document}")
    if not document or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    filename = os.path.basename(document.file_path)

    print(document)
    return FileResponse(
        path=document.file_path,
        filename=filename,
        media_type="application/pdf",
         headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{filename}"
        }
    )
    

