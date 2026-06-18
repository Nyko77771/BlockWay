from sqlalchemy import create_engine
# Importing my schema
from block_app.models.db_models import Base, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
import secrets, string
import os

DATABASE_URL = "sqlite:///./block_app/database/block_way.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

# Function for checking db existance
def check_start_db():
    if os.path.exists(DATABASE_URL):
        print("Database found.")
    else:
        print("Database not found.")
        print("Creating Database...")

    Base.metadata.create_all(bind=engine)

def check_admin():
    db =  SessionLocal()

    # Check if admin exists
    db_admin = db.query(User).filter(User.role_type == 'admin').first()

    if not db_admin:

        # Generate random password
        letters_digits = string.ascii_letters + string.digits
        for i in range(0, 15):
            random_password = ''.join(secrets.choice(letters_digits))

        # Create default admin
        default_admin = User(
            username = 'admin',
            password = random_password,
            role_type = 'admin'
        )

        db.add(default_admin)
        db.commit()

        print("Created default admin account")
        print('Default passwords needs to be changed')
        return True

    print('Contains admin account')
    return False
    # Closing db connection
    db.close()

