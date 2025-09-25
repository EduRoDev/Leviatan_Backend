from typing import Optional, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from App.Database.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    #* Relacion uno a muchos (Usuario a Materias [1:N])
    subjects: Mapped[List["Subject"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
   

class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  # <- ASEGURATE QUE ESTÉ AQUÍ
    
    #* Relacion inversa con User
    user: Mapped["User"] = relationship(back_populates="subjects")
    
     #* Relacion uno a muchos (Materia a Documentos [1:N])
    documents: Mapped[List["Document"]] = relationship(
        back_populates="subject", cascade="all, delete-orphan"
    )

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)  # <- CORREGIDO
    
    #* Relacion inversa con Subject
    subject: Mapped["Subject"] = relationship(back_populates="documents")

    
    #! Relacion uno a uno (Documento a Resumenes[1:1])
    summaries: Mapped[List["Summary"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    #! Relacion uno a muchos (Documento a Flashcards[1:N])
    flashcards: Mapped[List["Flashcard"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    #! Relacion uno a muchos (Documento a Quizzes[1:N])
    quizzes: Mapped[List["Quiz"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    
    
class Summary(Base):
    __tablename__ = "summaries"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)

    #* Relacion inversa con Documento
    document: Mapped["Document"] = relationship(back_populates="summaries")

class Flashcard(Base):
    __tablename__ = "flashcards"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)

    #* Relacion inversa con Documento
    document: Mapped["Document"] = relationship(back_populates="flashcards")

class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)

    #* Relacion inversa con Documento
    document: Mapped["Document"] = relationship(back_populates="quizzes")

    #! Relacion uno a muchos (Quiz a Pregunta[1:N])
    questions: Mapped[List["Question"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_text: Mapped[str] = mapped_column(String, nullable=False)
    correct_option: Mapped[str] = mapped_column(String, nullable=False)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)

    #* Relacion inversa con Quiz
    quiz: Mapped["Quiz"] = relationship(back_populates="questions")

    #! Relacion uno a muchos (Question a Options[1:N])
    options: Mapped[List["Option"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class Option(Base):
    __tablename__ = "options"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)

    #* Relacion inversa con Question
    question: Mapped["Question"] = relationship(back_populates="options")