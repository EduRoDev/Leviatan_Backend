from openai import OpenAI
import time
from dotenv import load_dotenv
import os

# from gtts import gTTS

# Esta es una prueba de la libreria gTTs de google 
# texto: str = "hola como estas"
# tts = gTTS(text=texto, lang='es')
# tts.save("output.mp3")
# print("Audio guardado como output.mp3")


load_dotenv()

API_KEY: str = os.getenv("API_KEY")

client = OpenAI(    
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

start_time = time.time()
message = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3.1:free",
    messages=[
        {
            "role": "system",
            "content": "Eres un asistente útil."
        },
        {
            "role": "user",
            "content": "Hola, como te puedo mandar un contenido o json a traves de tu API?"
        }
    ]
)
end_time = time.time()

print(message.choices[0].message.content)
print(f"Tiempo de respuesta del modelo: {end_time - start_time:.4f} segundos")
