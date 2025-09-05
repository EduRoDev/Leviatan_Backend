from sqlalchemy.orm import Session
from App.Models.models import Quiz, Question, Option

class QuizService:
    def __init__(self, db: Session):
        self.db = db
        
    def save_quiz(self, quiz_data: dict, document_id: int) -> Quiz:
        quiz_obj = Quiz(
            title=quiz_data["title"],
            document_id=document_id
        )
        
        self.db.add(quiz_obj)
        self.db.flush()   
               
        for q in quiz_data["questions"]:
            question = Question(
                question_text=q["question_text"],
                correct_option=q["correct_option"],
                quiz_id=quiz_obj.id
            )
            self.db.add(question)
            self.db.flush()
            for opt in q["options"]:
                option = Option(text=opt, question_id=question.id)
                self.db.add(option)
            
        self.db.commit()
        self.db.refresh(quiz_obj)
        return quiz_obj