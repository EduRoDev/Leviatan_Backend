from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path
from App.Models.models import Document
from App.Services.pdf_extract import pdf_extractor
import logging

class DocumentService():
    def __init__(self, db: Session):
        self.db = db
        
    def save_document(self, file_path: str, upload_dir="Public") -> Document:
        """
        Guarda el archivo en el sistema de archivos y registra la información en la base de datos.
        """
        
        file_path = str(file_path)
                
        err = os.makedirs(upload_dir, exist_ok=True)
        if not err:
            logging.info(f"Directorio {upload_dir} creado o ya existía.")

        file_name = Path(file_path).name
        dest_path = os.path.join(upload_dir, file_name)
        shutil.copy(file_path,dest_path)
        
        text, error, metadata = pdf_extractor.extract_text(file_path)
        if error:
            raise ValueError(f"Error al extraer el texto {error}")
        
        doc = Document(
            title= metadata.get("title", Path(file_path).stem),
            content=text,
            file_path=dest_path
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


    
