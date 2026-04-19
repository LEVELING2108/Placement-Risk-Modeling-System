from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import json

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    json_serializer=lambda obj: json.dumps(obj, default=str),
    json_deserializer=lambda obj: json.loads(obj)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
