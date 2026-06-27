from block_app.database.database import SessionLocal
import  block_app.models.db_models as db_models

def check_user_type(user_id):
    # Opening db connection
    db = SessionLocal()
    try:
        print('Checking user type')

        db_user = db.query(db_models.User).filter(db_models.User.user_id == user_id).first()

        if db_user.role_type == "admin":
            print('Current user is admin')
            return True
        return False
        print('User is not admin')
    except Exception as e:
        print('Exception occured while checking type')
        print(f'Exception: {e}')
        return False
    finally:
        # Closing db connection
        print('Closing db connection')
        db.close()