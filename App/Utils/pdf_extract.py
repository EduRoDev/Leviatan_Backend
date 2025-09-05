import PyPDF2
import pdfplumber
import logging
import re
from typing import Tuple, Optional, Dict, Any
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self):
        logger.info("PDFExtractor initialized")
    
    def extract_text(self, file_path: str) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
        """
        Extrae texto de un archivo PDF utilizando PyPDF2 y pdfplumber.
        
        Args:
            file_path (str): Ruta al archivo PDF.
        
        Returns:
            Tuple[texto, error, metadata]: Texto extraído, mensaje de error y metadatos.
        """
        # Verifica que el archivo existe
        if not os.path.exists(file_path):
            error_msg = f"El archivo no existe: {file_path}."
            logger.error(error_msg)
            return None, error_msg, {}
        
        # Verifica que el archivo es un PDF
        if not file_path.lower().endswith('.pdf'):
            error_msg = f"El archivo proporcionado no es un PDF: {file_path}."
            logger.error(error_msg)
            return None, error_msg, {}

        # Primero intentar con PyPDF2
        text_pypdf, error_pypdf, metadata = self._extract_with_pypdf2(file_path)
        if text_pypdf and self._is_text_quality_good(text_pypdf):
            logger.info("Texto extraído exitosamente con PyPDF2")
            return text_pypdf, None, metadata
        
        # Si PyPDF2 falla, intentar con pdfplumber
        text_plumber, error_plumber = self._extract_with_pdfplumber(file_path)
        if text_plumber and self._is_text_quality_good(text_plumber):
            logger.info("Texto extraído exitosamente con pdfplumber")
            return text_plumber, None, metadata
        
        # Si ambos fallan, retornar el mejor resultado disponible
        best_text = text_pypdf or text_plumber
        if best_text:
            logger.warning("Texto extraído pero con calidad baja")
            return best_text, "Calidad de texto baja", metadata
        
        # Si ningún método funcionó
        error_msg = error_plumber or error_pypdf or "No se pudo extraer texto del PDF"
        logger.error(f"Todos los métodos fallaron: {error_msg}")
        return None, error_msg, metadata
        
    def _extract_with_pypdf2(self, file_path: str) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
        """Extrae texto usando PyPDF2"""
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
                            text += page_text + "\n\n"
                            successful_pages += 1
                        else: 
                            logger.warning(f"No se pudo extraer texto de la página {page_num + 1}.")

                    except Exception as page_error:
                        logger.warning(f"Error extrayendo texto de la página {page_num + 1}: {page_error}")
                        continue
                
                metadata['extracted_pages'] = successful_pages
                metadata['total_pages'] = total_pages
                metadata['extraction_method'] = 'pypdf2'
                    
                if successful_pages == 0:
                    return None, "No se pudo extraer texto de ninguna página", metadata

                logger.info(f"PyPDF2 extrajo {successful_pages}/{total_pages} páginas")
                return text, None, metadata

        except PyPDF2.errors.PdfReadError as e:
            error_msg = f"Error de formato PDF: {e}"
            logger.error(error_msg)
            return None, error_msg, {}
        except Exception as e:
            error_msg = f"Error inesperado con PyPDF2: {e}"
            logger.error(error_msg)
            return None, error_msg, {}
    
    def _extract_with_pdfplumber(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Extrae texto usando pdfplumber"""
        try:
            text = ""
            total_pages = 0
            successful_pages = 0

            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages):
                    try: 
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text += page_text + "\n\n"
                            successful_pages += 1
                        else:
                            table_text = self._extract_text_from_table(page)
                            if table_text:
                                text += table_text + "\n\n"
                                successful_pages += 1
                                
                            else:
                                logger.warning(f"No se pudo extraer texto de la página {page_num + 1}.")

                    except Exception as page_error:
                        logger.warning(f"Error extrayendo texto de la página {page_num + 1}: {page_error}")
                        continue   

            if successful_pages == 0:
                return None, "No se extrajo texto de ninguna página"
            
            logger.info(f"pdfplumber extrajo {successful_pages}/{total_pages} páginas")
            return text, None
        
        except Exception as e:
            error_msg = f"Error con pdfplumber: {e}"
            logger.error(error_msg)
            return None, error_msg
        
    def _extract_text_from_table(self, page) -> Optional[str]:
        """Extrae texto de tablas en la página"""
        try:
            tables = page.extract_tables()
            if not tables:
                return None
            
            text = ""
            for table in tables:
                for row in table:
                    row_text = " ".join([str(cell) for cell in row if cell])
                    if row_text.strip():
                        text += row_text + "\n"
                text += "\n"
            return text.strip() if text else None
        except Exception as e:
            logger.warning(f"Error extrayendo texto de tabla: {e}")
            return None
        
    def _get_pdf_metadata(self, pdf_reader) -> Dict[str, Any]:
        """Obtiene metadatos del PDF"""
        metadata = {}
        try:
            if hasattr(pdf_reader, 'metadata') and pdf_reader.metadata:
                meta = pdf_reader.metadata
                metadata = {
                    'title': getattr(meta, 'title', 'Desconocido'),
                    'author': getattr(meta, 'author', 'Desconocido'),
                    'creator': getattr(meta, 'creator', 'Desconocido'),
                    'producer': getattr(meta, 'producer', 'Desconocido'),
                    'subject': getattr(meta, 'subject', 'Desconocido')
                }
        except Exception as e:
            logger.warning(f"Error obteniendo metadatos: {e}")
        
        return metadata
        
    def _is_text_quality_good(self, text: str, min_words: int = 50) -> bool:
        """Verifica si la calidad del texto extraído es aceptable"""
        if not text or not text.strip():
            return False
        
        words = re.findall(r'\b[a-zA-Záéíóúñ]{3,}\b', text, re.IGNORECASE)
        
        if len(words) < min_words:
            logger.warning(f"Texto con muy pocas palabras: {len(words)}")
            return False
        
        valid_chars = len(re.findall(r'[a-zA-Záéíóúñ0-9]', text))
        total_chars = len(text)
        
        if total_chars == 0:
            return False
        
        valid_ratio = valid_chars / total_chars
        if valid_ratio < 0.3:  
            logger.warning(f"Proporción de caracteres válidos baja: {valid_ratio:.2f}")
            return False
        
        return True
    
pdf_extractor = PDFExtractor() 