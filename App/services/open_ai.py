import logging
from typing import Dict, Any, Optional, Tuple
import time
from openai import OpenAI
from App.Core.config import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        logger.info("Cliente inicizalizado con OpenAI")

    def analyze_text(self, text: str, metadata: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Analiza el texto utilizando el modelo de OpenAI para generar un resumen, flashcards
        y un quiz basado en el contenido del texto.
        """
        try:
            prompt = self._create_analysis_prompt(text, metadata)
            logger.info("Enviando solicitud al modelo de OpenAI")
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto y util que ayuda a analizar y resumir documentos, crear flashcards de estudio y quizzes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.5,
            )

            end_time = time.time()
            content= response.choices[0].message.content
            usage = response.usage
            logger.info(f"Análisis completado en {end_time - start_time:.2f}s")
            
            return content,{
                "model": settings.OPENAI_MODEL,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "response_time": end_time - start_time
            }
        except Exception as e:
            logger.error(f"Error al analizar el texto: {e}")
            return None, {"error": str(e)}


    def _create_analysis_prompt(self, text: str, metadata: Dict[str, Any]) -> str:
        max_length = 10000
        truncated_text = text[:max_length] + "..." if len(text) > max_length else text
        return f""""
        eres un asistente de IA que ayuda a analizar y resumir documentos, realizar flashcards de estudio y quizes que propociona:

        1. RESUMEN: Proporciona un resumen ejecutivo donde expliques todo lo que se pueda aprender del texto.
        2. FLASHCARDS: Crea 5 flashcards de estudio en formato JSON con la estructura:
            [
                {{
                    "question": "Pregunta",
                    "answer": "Respuesta"
                }},
                ...
            ]
        3. QUIZ: Crea un quiz de 5 preguntas en formato JSON con la estructura:
            [
                {{
                    "question": "Pregunta",
                    "options": ["Opción 1", "Opción 2", "Opción 3", "Opción 4"],
                    "correct_option": "Opción correcta"
                }},
                ...
            ]
        
        Información del documento:
        - Páginas: {metadata.get('extracted_pages', 'N/A')}/{metadata.get('total_pages', 'N/A')}
        - Método: {metadata.get('extraction_method', 'N/A')}

        CONTENIDO:
        {truncated_text}
        RESPONDE EN ESPAÑOL.    
        """
        
openai_client = OpenAIClient()