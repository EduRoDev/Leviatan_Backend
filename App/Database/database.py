from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from App.Core.config import settings

DATABASE_URL = f"postgresql://leviatan_user:DUHx0MorTz4LzTtauZNYeGlzlOs8xl4Y@dpg-d3uk8mje5dus739oocj0-a/leviatan"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



