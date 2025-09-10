# from App.Database.init_db import init
from App.Controllers import document_controller
from App.Controllers import auth_controller
from App.Controllers import summary_controller
from App.Controllers import flashcard_controller
from App.Controllers import quiz_controller
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from App.Database.database import engine, Base

app = FastAPI(
    title="Leviatan Backend",
    description="API para gestión de documentos y análisis con OpenAI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(document_controller.router)
app.include_router(auth_controller.router)
app.include_router(summary_controller.router)
app.include_router(flashcard_controller.router)
app.include_router(quiz_controller.router)


@app.get("/")
def root():
    return {"message": "Welcome to Leviatan Backend API"}
    
