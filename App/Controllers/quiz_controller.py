from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.Utils.db_sessions import get_db
from App.Services.quiz_services import QuizService
from App.Utils.auth_utils import get_current_user

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