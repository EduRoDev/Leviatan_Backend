from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from App.Services.stadistics_services import StatisticsService
from App.Utils.db_sessions import get_db
from App.Utils.auth_utils import get_current_user
from typing import List, Dict, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/statistics", tags=["Statistics"])

class QuizAnswerRequest(BaseModel):
    question_id: int
    selected_option: str
    
class RecordQuizAttemptRequest(BaseModel):
    quiz_id: int
    user_id: int
    answers: List[QuizAnswerRequest]
    time_taken: Optional[int] = None
    
class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    total_questions: int
    correct_answers: int
    score: float
    time_taken: Optional[int]
    completed_at: str
    
class UserStatisticsResponse(BaseModel):
    total_quizzes: int
    average_score: float
    total_time: int
    best_score: float
    worst_score: float
    recent_attempts: List[Dict]
    
class ProgressBySubjectResponse(BaseModel):
    document_id: int
    total_attempts: int
    average_score: float
    
class QuizStatisticsResponse(BaseModel):
    total_attempts: int
    average_score: float
    pass_rate: float
    difficult_questions: List[Dict]
 
@router.post("/record_attempt", response_model=Dict, status_code=status.HTTP_201_CREATED)   
async def record_quiz_attempt(
    request: RecordQuizAttemptRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["id"] != request.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Has not permission to register this attempt.")
    
    try:
        statistics_service = StatisticsService(db)
        answers_dict = [
            {
                "question_id": ans.question_id,
                "selected_option": ans.selected_option
            }
            for ans in request.answers
        ]
        
        attempt = statistics_service.record_quiz_attempt(
            user_id=request.user_id,
            quiz_id=request.quiz_id,
            answers=answers_dict,
            time_taken=request.time_taken
        )
        
        return {
            "message": "Intento registrado exitosamente.",
            "attempt_id": attempt.id,
            "score": attempt.score,
            "correct_answers": attempt.correct_answers,
            "total_questions": attempt.total_questions
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
@router.get("/user_statistics", response_model=UserStatisticsResponse)
async def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado.")
    try:
        statistics_service = StatisticsService(db)
        stats = statistics_service.get_user_statistics(current_user["id"])
        return UserStatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )