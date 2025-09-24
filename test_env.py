# test_env.py
import os
from pathlib import Path

print("=== VERIFICACIÓN DE ARCHIVO .env ===")

# Verificar si el archivo existe
env_path = Path('.env')
print(f"Archivo .env existe: {env_path.exists()}")
print(f"Ubicación actual: {Path.cwd()}")
print(f"Ruta completa .env: {env_path.absolute()}")

if env_path.exists():
    print("\nContenido del archivo .env:")
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    print("\n=== CARGANDO VARIABLES ===")
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar variables específicas
    variables = ['OPENAI_API_KEY', 'OPENAI_MODEL', 'OPENAI_BASE_URL']
    for var in variables:
        value = os.getenv(var)
        if var == 'OPENAI_API_KEY' and value:
            print(f"{var}: {value[:10]}...{value[-4:]}")
        else:
            print(f"{var}: {value}")
else:
    print("❌ Archivo .env NO EXISTE")
    print("Crea el archivo .env en la raíz del proyecto")