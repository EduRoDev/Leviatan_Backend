from sqlalchemy.orm import Session
from App.Models.models import Subject

class SubjectService():
    def __init__(self, db: Session):
        self.db = db
        
    def create_subject(self, name: str, description:str, user_id: int) -> Subject:
        existing_subject = self.db.query(Subject).filter(Subject.name == name).first()
        if existing_subject:
            raise ValueError("Subject name already exists")
        
        new_subject = Subject(
            name=name,
            description=description,
            user_id=user_id
        )
        
        self.db.add(new_subject)
        self.db.commit()
        self.db.refresh(new_subject)
        return new_subject
    
    def get_subjects_by_user(self, user_id: int) -> list[Subject]:
        subjects = self.db.query(Subject).filter(Subject.user_id == user_id).all()
        return subjects
    
    def get_subject_by_id(self, subject_id: int) -> Subject:
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        return subject
    
    def edit_subject(self, subject_id: int, name: str, description: str) -> Subject:
        subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise ValueError("Subject not found")
        
        if name and name != subject.name:
            existing_subject = self.db.query(Subject).filter(Subject.name == name).first()
            if existing_subject:
                raise ValueError("Subject name already exists")
            subject.name = name
            
        if description is not None:
            subject.description = description
        
        self.db.commit()
        self.db.refresh(subject)
        return subject
    
