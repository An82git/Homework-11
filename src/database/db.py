from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.conf.config import settings
from src.database.models import Base


engine = create_engine(settings.sqlalchemy_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
