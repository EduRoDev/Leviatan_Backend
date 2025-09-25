from sqlalchemy.orm import Session
import os
from App.Models.models import Document
from App.Utils.pdf_extract import pdf_extractor

class DocumentService():
    def __init__(self, db: Session):
        self.db = db

    def save_document(self, file_path: str, subject_id: int) -> Document:
        """
        Procesa un archivo PDF ya guardado en disco y lo registra en la base de datos.
        """
        if not os.path.exists(file_path):
            raise ValueError(f"El archivo no existe: {file_path}")

        text, error, metadata = pdf_extractor.extract_text(file_path)
        if error or not text:
            raise ValueError(f"Error al extraer el texto del PDF: {error}")
        
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0]
        
        doc = Document(
            title= title,
            content=text,
            file_path=file_path,
            subject_id=subject_id
        )
        
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        
        return doc

    def get_document(self, doc_id: int) -> Document:
        """
        Recupera un documento de la base de datos por su ID.
        """
        return self.db.query(Document).filter(Document.id == doc_id).first()
    
    def get_document_with_path(self, file_path: str) -> Document:
        """
        Recupera un documento de la base de datos por su ruta de archivo.
        """
        return self.db.query(Document).filter(Document.file_path == file_path).first()


    
