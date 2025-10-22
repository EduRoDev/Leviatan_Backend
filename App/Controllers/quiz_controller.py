from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.Utils.db_sessions import get_db
from App.Services.quiz_services import QuizService
from App.Services.document_services import DocumentService
from App.Utils.auth_utils import get_current_user
from App.Utils.open_ai import OpenAIClient

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.get("/get_quiz/{document_id}")
def get_quiz(document_id:int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    quiz = QuizService(db).get_quiz(document_id)
    if not quiz:
        raise HTTPException(status_code=404, details="Quiz not found")
    
    return {
        "id": quiz.id,
        "title": quiz.title,
        "document_id": quiz.document_id,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "correct_option": q.correct_option,
                "options": [opt.text for opt in q.options]
            }
            for q in quiz.questions
        ]
    }
    

@router.post("/create/{document_id}")
async def create_quiz_for_document(document_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    document_services = DocumentService(db)
    quiz_service = QuizService(db)
    open_ai_client = OpenAIClient()
    
    document = document_services.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    result = await open_ai_client.generate_quiz(document.content)
    
    if not result or "data" not in result or "quiz" not in result["data"]:
        raise HTTPException(status_code=500, detail="Error generating quiz")
    
    quiz_data = result["data"]["quiz"]
    saved_quiz = quiz_service.save_quiz(quiz_data, document_id)
    if not saved_quiz:
        raise HTTPException(status_code=500, detail="Error saving quiz")
    
    return {
        "message": "Quiz created successfully",
        "quiz": {
            "id": saved_quiz.id,
            "title": saved_quiz.title,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "correct_option": q.correct_option,
                    "options": [opt.text for opt in q.options]
                }
                for q in saved_quiz.questions
            ]
        }
    }
    