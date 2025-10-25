from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from datetime import datetime
from typing import List, Dict, Optional
from App.Models.models import QuizAttempt, Quiz, QuizAnswer, Question, User, Option, Document

class StatisticsService:
    def __init__(self, db: Session):
        self.db = db
        
    def record_quiz_attempt(
        self,
        user_id: int,
        quiz_id: int,
        answers: List[Dict[str,str]],
        time_taken: Optional[int] = None) -> QuizAttempt:
        
        quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError(f"Quiz con ID {quiz_id} no encontrado.")
        
        questions = self.db.query(Question).filter(Question.quiz_id == quiz_id).all()
        total_questions = len(questions)
        correct_answers = 0
        
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            total_questions=total_questions,
            correct_answers=0,
            score=0.0,
            time_taken=time_taken,
            completed_at= datetime.now()
        )
        
        self.db.add(attempt)
        self.db.flush()
        
        quiz_answers = []
        for data in answers:
            question_id = data["question_id"]
            selected_option = data["selected_option"]
            
            question = next((qst for qst in questions if qst.id == question_id), None)
            if not question:
                continue
            
            is_correct = question.correct_option == selected_option
            if is_correct:
                correct_answers += 1
                
            quiz_answer = QuizAnswer(
                attempt_id=attempt.id,
                question_id=question_id,
                selected_option=selected_option,
                is_correct=is_correct
            )
            quiz_answers.append(quiz_answer)
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        attempt.correct_answers = correct_answers
        attempt.score = score
        
        self.db.add_all(quiz_answers)
        self.db.commit()
        
        return attempt
    
    def get_user_statistics(self, user_id: int) -> Dict:
        attempts = self.db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
        if not attempts:
            return {
                "total_quizzes": 0,
                "average_score": 0.0,
                "total_time": 0,
                "best_score": 0.0,
                "worst_score": 0.0,
                "recent_attempts": []
            }
            
        scores = [attempt.score for attempt in attempts]
        times = [attempt.time_taken for attempt in attempts if attempt.time_taken]
        
        return {
            "total_quizzes": len(attempts),
            "average_score": sum(scores) / len(scores),
            "total_time": sum(times) if times else 0,
            "best_score": max(scores),
            "worst_score": min(scores),
            "recent_attempts": self.__format__recent_attempts(attempts[-5:])
        }
        
    def get_user_progress_by_subject(self,user_id:int)->List[Dict]:
        query = self.db.query(
            Quiz.document_id,
            Document.subject_id,
            func.count(QuizAttempt.id).label('total_attempts'),
            func.avg(QuizAttempt.score).label('average_score'),
        ).join(QuizAttempt).join(Document, Quiz.document_id == Document.id).filter(
            QuizAttempt.user_id == user_id
        ).group_by(Quiz.document_id, Document.subject_id).all()
        
        return [
            {
                "document_id":row.document_id,
                "subject_id":row.subject_id,
                "total_attempts":row.total_attempts,
                "average_score":round(row.average_score,2)
            }
            for row in query
        ]
        
    def get_quiz_statistics(self,quiz_id:int)->Dict:
        attemps = self.db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
        if not attemps:
            return {
                "total_attempts": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
                "difficult_questions": []
            }
            
        scores = [attempt.score for attempt in attemps]
        pass_rate = len([s for s in scores if s >= 70]) / len(scores) * 100
        
        return {
            "total_attempts": len(attemps),
            "average_score": sum(scores) / len(scores),
            "pass_rate": pass_rate,
            "difficult_questions": self.__identify_difficult_questions(quiz_id)
        }
        
    def __identify_difficult_questions(self,quiz_id:int)->List[Dict]:
        query = self.db.query(
            Question.id,
            Question.question_text,
            func.count(QuizAnswer.id).label('total_answers'),
            func.sum(func.cast(QuizAnswer.is_correct, Integer)).label('correct_answers')
        ).join(QuizAnswer).filter(
            Question.quiz_id == quiz_id
        ).group_by(Question.id, Question.question_text).all()
        
        difficult_questions = []
        for row in query:
            error_rate = (row.total_answers - row.correct_answers) / row.total_answers * 100
            if error_rate > 50:
                difficult_questions.append({
                    "question_id": row.id,
                    "question_text": row.question_text[:100] + "...",
                    "error_rate": round(error_rate, 2)
                })
                
        return sorted(difficult_questions, key=lambda x: x["error_rate"], reverse=True)
    
    def __format__recent_attempts(self, attempts: List[QuizAttempt]) -> List[Dict]:
        return [
            {
                "quiz_id": attempt.quiz_id,
                "score": attempt.score,
                "time_taken": attempt.time_taken,
                "completed_at": attempt.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for attempt in attempts
        ]