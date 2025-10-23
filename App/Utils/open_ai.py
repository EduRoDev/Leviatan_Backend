import logging
from typing import Dict, Any, List
import time
import json
from openai import AsyncOpenAI
from openai import APIError, RateLimitError, APIConnectionError, APITimeoutError
from App.Core.config import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        if not hasattr(settings, 'OPENAI_MODEL') or not settings.OPENAI_MODEL:
            raise ValueError("OPENAI_MODEL no está configurado")
        
        client_kwargs = {
            "api_key": settings.OPENAI_API_KEY,
            "timeout": 60.0
        }
        
        if hasattr(settings, 'OPENAI_BASE_URL') and settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
            
        if settings.is_openrouter():
            extra_headers = settings.get_client_headers()
            if extra_headers:
                client_kwargs["default_headers"] = extra_headers
            
        self.client = AsyncOpenAI(**client_kwargs)
        provider = "OpenRouter" if settings.is_openrouter() else "OpenAI"
        logger.info(f"Cliente {provider} inicializado: {settings.OPENAI_MODEL}")    
        
    async def _call_openai(self, prompt: str, system_message: str) -> Dict[str, Any]:
        """Método genérico para llamadas a OpenAI con respuesta JSON"""
        try:
            start_time = time.time()
            
            logger.info(f"📤 Enviando request al modelo: {settings.OPENAI_MODEL}")
            logger.debug(f"Longitud del prompt: {len(prompt)} caracteres")
            
            # Algunos modelos gratuitos no soportan response_format, intentamos sin él
            try:
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"},
                )
            except Exception as e:
                logger.warning(f"⚠️ Error con response_format, reintentando sin él: {e}")
                # Reintentar sin response_format
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_message + " IMPORTANTE: Tu respuesta DEBE ser un JSON válido."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )
            logger.info(f"📥 Respuesta recibida del modelo")
            
            # Verificar si hay respuesta
            if not response.choices:
                logger.error("❌ No hay choices en la respuesta")
                raise ValueError("No se recibieron opciones en la respuesta del modelo")
            
            message = response.choices[0].message
            
            # DeepSeek y algunos modelos de razonamiento usan el campo 'reasoning' en lugar de 'content'
            content_str = None
            
            if message.content:
                content_str = message.content.strip()
                logger.info(f"✅ Contenido recibido en 'content': {len(content_str)} caracteres")
            elif hasattr(message, 'reasoning') and message.reasoning:
                # DeepSeek devuelve en el campo 'reasoning'
                content_str = message.reasoning.strip()
                logger.info(f"✅ Contenido recibido en 'reasoning': {len(content_str)} caracteres")
                # Limpiar tokens especiales de DeepSeek
                if '<｜begin▁of▁sentence｜>' in content_str:
                    content_str = content_str.split('<｜begin▁of▁sentence｜>')[0].strip()
            else:
                logger.error("❌ El contenido del mensaje está vacío en ambos campos")
                logger.error(f"Respuesta completa: {response}")
                raise ValueError("El modelo devolvió una respuesta vacía")
            
            logger.debug(f"Contenido raw: {content_str[:200]}...")
            
            # Limpiar markdown si existe
            if content_str.startswith('```json'):
                content_str = content_str.replace('```json', '').replace('```', '').strip()
            elif content_str.startswith('```'):
                content_str = content_str.replace('```', '').strip()
            
            content = json.loads(content_str)
            
            return {
                "data": content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "response_time": time.time() - start_time,
                "model": settings.OPENAI_MODEL
            }
            
        except (APIConnectionError, APITimeoutError, RateLimitError, APIError) as e:
            logger.error(f"Error de API: {e}")
            raise ConnectionError(f"Error de API: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON: {e}")
            raise ValueError(f"Error decodificando JSON: {e}")
        except Exception as e:
            logger.error(f"Error en llamada a OpenAI: {e}")
            raise    
        
    async def generate_summary(self, text: str) -> Dict[str, Any]:
        """
        Genera un resumen del texto
        
        Returns:
            {
                "data": {"summary": "texto del resumen"},
                "usage": {...},
                "response_time": float,
                "model": str
            }
        """
        max_length = 10000
        truncated_text = text[:max_length] + ("..." if len(text) > max_length else "")
        
        logger.info(f"🔄 Generando resumen de texto ({len(truncated_text)} caracteres)")
        
        prompt = f"""Analiza el siguiente texto y genera un resumen completo y conciso.

        FORMATO DE RESPUESTA REQUERIDO (JSON):
        {{"summary": "tu resumen aquí"}}

        TEXTO A RESUMIR:
        {truncated_text}

        Responde ÚNICAMENTE con el JSON, sin texto adicional antes o después."""
        
        system_message = """Eres un experto en resumir documentos académicos. 
        Tu respuesta DEBE ser ÚNICAMENTE un objeto JSON válido con el formato: {"summary": "texto del resumen"}
        NO incluyas explicaciones, markdown, ni texto adicional. SOLO el JSON."""
        
        try:
            result = await self._call_openai(prompt, system_message)
            
            if "summary" not in result["data"]:
                logger.error(f"❌ Falta campo 'summary'. Data recibida: {result['data']}")
                raise ValueError("Falta campo 'summary' en respuesta")
            
            logger.info(f"✅ Resumen generado exitosamente en {result['response_time']:.2f}s")
            logger.info(f"📊 Tokens usados: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen: {e}")
            raise

    async def generate_flashcards(self, text: str, count: int = 5) -> Dict[str, Any]:
        """
        Genera flashcards de estudio
        
        Args:
            text: Texto base para generar flashcards
            count: Número de flashcards a generar (default: 5)
        
        Returns:
            {
                "data": {
                    "flashcards": [
                        {"subject": "tema", "definition": "definición"},
                        ...
                    ]
                },
                "usage": {...},
                "response_time": float,
                "model": str
            }
        """
        max_length = 10000
        truncated_text = text[:max_length] + ("..." if len(text) > max_length else "")
        
        prompt = f"""
        Crea EXACTAMENTE {count} flashcards de estudio basadas en el texto.
        Devuelve SOLO un JSON con esta estructura:
        {{
            "flashcards": [
                {{"subject": "tema 1", "definition": "definición 1"}},
                {{"subject": "tema 2", "definition": "definición 2"}}
            ]
        }}
        
        TEXTO:
        {truncated_text}
        
        IMPORTANTE: Devuelve SOLO el JSON válido, sin texto adicional.
        """
        
        system_message = "Eres un experto en crear flashcards educativas. Devuelve solo JSON válido."
        
        try:
            result = await self._call_openai(prompt, system_message)
            
            if "flashcards" not in result["data"]:
                raise ValueError("Falta campo 'flashcards' en respuesta")
            
            if not isinstance(result["data"]["flashcards"], list):
                raise ValueError("'flashcards' debe ser una lista")
            
            logger.info(f"{len(result['data']['flashcards'])} flashcards generadas en {result['response_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error generando flashcards: {e}")
            raise

    async def generate_quiz(self, text: str, min_questions: int = 5) -> Dict[str, Any]:
        """
        Genera un quiz con preguntas de opción múltiple
        
        Args:
            text: Texto base para generar el quiz
            min_questions: Número mínimo de preguntas (default: 5)
        
        Returns:
            {
                "data": {
                    "quiz": {
                        "title": "título",
                        "questions": [
                            {
                                "question_text": "pregunta",
                                "options": ["A", "B", "C", "D"],
                                "correct_option": "respuesta correcta"
                            },
                            ...
                        ]
                    }
                },
                "usage": {...},
                "response_time": float,
                "model": str
            }
        """
        max_length = 10000
        truncated_text = text[:max_length] + ("..." if len(text) > max_length else "")
        
        prompt = f"""
        Crea un quiz con MÍNIMO {min_questions} preguntas basadas en el texto.
        Devuelve SOLO un JSON con esta estructura:
        {{
            "quiz": {{
                "title": "título del quiz",
                "questions": [
                    {{
                        "question_text": "pregunta 1",
                        "options": ["A", "B", "C", "D"],
                        "correct_option": "Opción correcta"
                    }}
                ]
            }}
        }}
        
        TEXTO:
        {truncated_text}
        
        IMPORTANTE: Devuelve SOLO el JSON válido, sin texto adicional.
        """
        
        system_message = "Eres un experto en crear quizzes educativos. Devuelve solo JSON válido."
        
        try:
            result = await self._call_openai(prompt, system_message)
            
            if "quiz" not in result["data"]:
                raise ValueError("Falta campo 'quiz' en respuesta")
            
            if "questions" not in result["data"]["quiz"]:
                raise ValueError("Falta campo 'questions' en quiz")
            
            if not isinstance(result["data"]["quiz"]["questions"], list):
                raise ValueError("'questions' debe ser una lista")
            
            logger.info(f"Quiz generado con {len(result['data']['quiz']['questions'])} preguntas en {result['response_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error generando quiz: {e}")
            raise

    async def chat_with_document(
        self,
        document_content: str,
        user_message: str,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Chat interactivo con el documento (retorna texto plano, no JSON)
        
        Args:
            document_content: Contenido del documento
            user_message: Mensaje del usuario
            chat_history: Historial de conversación (opcional)
        
        Returns:
            str: Respuesta del asistente
        """
        try:
            max_document_length = 8000
            truncated_content = document_content[:max_document_length] + (
                "..." if len(document_content) > max_document_length else ""
            )
            
            system_prompt = f"""
            Eres un asistente educativo experto. Responde preguntas sobre el siguiente documento.
            
            DOCUMENTO:
            {truncated_content}
            
            INSTRUCCIONES:
            - Responde ÚNICAMENTE basándote en la información del documento
            - Si la información no está en el documento, indícalo claramente
            - Sé conciso y claro en tus respuestas
            - Para resúmenes o explicaciones, menos de 150 palabras
            - Mantén un tono profesional y educativo
            - Las respuestas deben tener un limite de 300 palabras
            """
            
            messages = [{"role": "system", "content": system_prompt}]
            
            
            messages.append({"role": "user", "content": user_message})
            
            response = await self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Respuesta vacía de OpenAI")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error en chat_with_document: {e}")
            return "Lo siento, ha ocurrido un error al procesar tu solicitud."
        
    async def prueba(self):
        """Método de prueba simple"""
        try:
            prompt = "Hola como estas"
            completion = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un asistente útil."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error en prueba: {e}")
            return "Error en prueba"