from App.Database.database import engine, Base
from App.Models.models import User, Document, Flashcard, Quiz, Question, Option

class InitDB:
    def __init__(self):
        self.create_tables()

    def create_tables(self):
        Base.metadata.create_all(bind=engine)

init = InitDB()