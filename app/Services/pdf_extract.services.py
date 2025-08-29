import PyPDF2
import pdfplumber
import logging
import re
from typing import Tuple,Optional,Dict,Any
import os

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self):
        logger.info("PDFExtractor initialized")
    
    
    def extract_text(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extrae texto de un archivo PDF utilizando PyPDF2 y pdfplumber.
        
        Args:
            file_path (str): Ruta al archivo PDF.
        
        Returns:
            Tuple[Optional[str], Optional[str]]: Texto extraído con PyPDF2 y pdfplumber.
        """

        # Verifica que el archivo es un PDF
        if not file_path.lower().endswith('.pdf'):
            error_msg: str = f"El archivo proporcionado no es un PDF: {file_path}."
            logger.error(error_msg)
            return None, error_msg, {}
        
        # Verifica que el archivo existe
        if not os.path.exists(file_path):
            error_msg: str = f"El archivo no existe: {file_path}."
            logger.error(error_msg)
            return None, error_msg, {}

        text_pypdf, error_pypdf, metadata_pypdf = self._extract_with_pypdf2(file_path)
        
        
        return None, None, {}

        
    
    def _extract_with_pypdf2(self, file_path: str) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
        """Extra el texto del documento usando la libreria PyPDF2"""
        
        try:
            metadata = {}
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = self._get_pdf_metadata(pdf_reader)
                
                if pdf_reader.is_encrypted:
                    try:
                        pdf_reader.decrypt('')
                    except Exception as e:
                        error_msg = f"El PDF está cifrado y no se pudo descifrar: {e}"
                        logger.error(error_msg)
                        return None, error_msg, metadata
                    
                text = ""
                total_pages = len(pdf_reader.pages)
                successful_pages = 0
                
                for page_num in range(total_pages):
                    try: 
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        if page_text and page_text.strip():
                            text += page_text + "\n"
                            successful_pages += 1
                        else: 
                            logger.warning(f"No se pudo extraer texto de la página {page_num + 1}.")

                    except Exception as page_error:
                        logger.warning(f"Error extrayendo texto de la página {page_num + 1}: {page_error}")
                        continue
            metadata['extracted_pages'] = successful_pages
            metadata['total_pages'] = total_pages
                    
            if successful_pages == 0:
                return None, "<No se pudo extraer texto>", metadata

            logger.info(f"Texto extraído con PyPDF2: {len(text)} caracteres de {successful_pages}/{total_pages} páginas.")
            return text, None, metadata

        except PyPDF2.errors.PdfReadError as e:
            error_msg = f"Error leyendo el PDF con PyPDF2: {e}"
            logger.error(error_msg)
            return None, error_msg, {}

        except Exception as e:
            error_msg = f"Error leyendo el PDF con PyPDF2: {e}"
            logger.error(error_msg)
            return None, error_msg, {}
            
        
    def _get_pdf_metadata(self, pdf_reader) -> Dict[str, Any]:
        """Extrae los metadatos del PDF"""
        try:
            if hasattr(pdf_reader, 'metadata') and pdf_reader.metadata:
                meta = pdf_reader.metadata
                metadata = {
                    'title': getattr(meta, 'title', 'Desconocido'),
                    'author': getattr(meta, 'author', 'Desconocido'),
                    'creator': getattr(meta, 'creator', 'Desconocido'),
                    'producer': getattr(meta, 'producer', 'Desconocido'),
                    'subject': getattr(meta, 'subject', 'Desconocido'),
                    'total_pages': len(pdf_reader.pages)
                }
        except Exception as e:
            logger.warning(f"Error obteniendo metadatos: {e}")
        
        return metadata
        