from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from App.Core.config import settings

DATABASE_URL = f"postgresql://leviatan_v2_user:isExx5RXtuRkJLjcAkZyRMGrF5KdvlmJ@dpg-d45540s9c44c73816nu0-a/leviatan_v2"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



