# from App.Database.init_db import init
from App.Controllers import document_controller
from fastapi import FastAPI

app = FastAPI(
    title="Leviatan Backend",
    description="API para gestión de documentos y análisis con OpenAI",
    version="1.0.0"
)

app.include_router(document_controller.router)

#def db_init():
    #init.create_tables()
@app.get("/")
def root():
     return {"message": "Welcome to Leviatan Backend API"}
    
# if __name__ == "__main__":
    # db_init()
    # main()
    #test_save_document()