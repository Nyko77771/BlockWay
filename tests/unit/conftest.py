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
    try:
        yield db
    except Exception as e:
        print(f"Exception in temporal db session. Exception: {e}")
    finally:
        db.close()
