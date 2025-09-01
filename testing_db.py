from App.Database.database import engine
from sqlalchemy.exc import OperationalError

try:
    with engine.connect() as connection:
        print("Conexión exitosa a la base de datos.")
except OperationalError as e:
    print(f"Error al conectar a la base de datos: {e}")