# from App.Database.init_db import init
from App.Controllers import document_controller
from App.Controllers import auth_controller
from fastapi import FastAPI
from App.Database.database import engine, Base

app = FastAPI(
    title="Leviatan Backend",
    description="API para gestión de documentos y análisis con OpenAI",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)
app.include_router(document_controller.router)
app.include_router(auth_controller.router)


@app.get("/")
def root():
    return {"message": "Welcome to Leviatan Backend API"}
    
