from .config import DB

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = f"postgresql://{DB['USERNAME']}:{DB['PASSWORD']}@localhost:5432/{DB['DATABASE']}"

engine = create_engine(url=DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
