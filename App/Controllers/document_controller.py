from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import os

from App.Database.database import get_db
from App.Services.document_services import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("Public").resolve()

    
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
        try:
            temp_file_path = os.path.join(UPLOAD_DIR, file.filename)
            
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            document_service = DocumentService(db)
            document = document_service.save_document(temp_file_path)
            return {
                "status": "success",
                "message": "File uploaded and processed successfully",
                "document_id": document.id,
                "title": document.title,
                "file_path": document.file_path
                
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
        document_service = DocumentService(db)
        document = document_service.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "file_path": document.file_path
        }
        
@router.get("/download/{doc_id}")
def download_file_by_id(doc_id: int, db: Session = Depends(get_db)):
    document_service = DocumentService(db)
    document = document_service.get_document(doc_id)
    if not document or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    filename = os.path.basename(document.file_path)
    return FileResponse(
        path=document.file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
    
@router.get("/view/{filename}")
def view_file(filename: str):
    safe_path = (UPLOAD_DIR / filename).resolve()

    if not safe_path.exists() or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    if not str(safe_path).startswith(str(UPLOAD_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")

    return FileResponse(
        path=safe_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={safe_path.name}"}
    )

