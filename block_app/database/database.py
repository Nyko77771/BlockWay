from sqlalchemy import create_engine

# Importing my schema
from block_app.models.db_models import Base, User
from block_app.services.password_service import password_hashing
from sqlalchemy.orm import sessionmaker
import secrets
import string
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


# Function for checking default admin
# Also creates default admin if none are found
def check_admin():
    db = SessionLocal()

    try:

        # Check if admin exists
        print("Checking if admin")
        db_admin = db.query(User).filter(User.role_type == "admin").first()

        if not db_admin:

            # Generate random password
            letters_digits = string.ascii_letters + string.digits + "!@~£%$"
            random_password = "".join(secrets.choice(letters_digits) for i in range(10))

            # Password Hashing
            hashed_values = password_hashing(random_password)
            salt = hashed_values["salt"]

            # Create default admin
            default_admin = User(
                username="admin", password=random_password, salt=salt, role_type="admin"
            )

            db.add(default_admin)
            db.commit()

            print("Created default admin account")
            print("Default passwords needs to be changed")
            return True

        print("Already contains admin account")
        return False
    except Exception as e:
        print("Exception occured")
        print(f"Exception: {e}")
        return False
    finally:
        # Closing db connection
        print("Closing Connection")
        db.close()
