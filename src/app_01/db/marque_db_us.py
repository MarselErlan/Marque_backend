from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from typing import Generator
from dotenv import load_dotenv

load_dotenv()   

# Database URL - you can set this as an environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "os.getenv('postgresql://postgres:YgyDmMbYyzPKvSsNyDRShLJqehXtTdJx@metro.proxy.rlwy.net:45504/railway')")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
