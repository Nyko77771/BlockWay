from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from block_app.models.db_models import Base


@pytest.fixture
def db_session():

    TEMP_DB_URL = "sqlite:///:memory:"

    engine = create_engine(TEMP_DB_URL, echo=True)

    Base.metadata.create_all(bind=engine)

    SessionMemory = sessionmaker(autoflush=False, bind=engine)

    db = SessionMemory()
    yield db
    db.close()


@pytest.fixture
def pihole_url():
    return "http://192.168.9.108:8080"
