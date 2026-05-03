from sqlalchemy import create_engine
# Importing my schema
from block_app.models.models import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = "sqlite:///./block_way.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

# Function for checking db existance
def check_db():
    if os.path.exists(DATABASE_URL):
        print("Database found.")
    else:
        print("Database not found.")

    Base.metadata.create_all(engine)

