from block_app.database.database import SessionLocal
import  block_app.models.db_models as db_models

class DomainDatabase:

    # User Methods
    # Method for Getting User by Username
    def get_db_user_by_username(self, username):
        db = SessionLocal()
        try:
            print('Checking user type')

            db_user = db.query(db_models.User).filter(db_models.User.username == username).first()

            return db_user

        except Exception as e:
            print('Exception occurred')
            print(f'Exception: {e}')
        finally:
            print('Closing Database')
            db.close()

    # Method for Getting User by ID
    def get_db_user_by_id(self, user_id):
        db = SessionLocal()
        try:
            print('Checking user type')

            db_user = db.query(db_models.User).filter(db_models.User.user_id == user_id).first()

            return db_user

        except Exception as e:
            print('Exception occurred')
            print(f'Exception: {e}')
        finally:
            print('Closing Database')
            db.close()

    # Method for Adding User
    def add_db_user(username, password, salt):

        db = SessionLocal()
        try:
            print('Adding User')

            new_user = db_models.User(
                    username = username,
                    password = password,
                    salt = salt,
                    role_type = db_models.UserRoleEnum['NORMAL'].value,
            )

            db.add(new_user)
            db.commit()

        except Exception as e:
            print('Exception occurred')
            print(f'Exception: {e}')
        finally:
            print('Closing Database')
            db.close()

    def get_default_admin():
        db = SessionLocal()
        try:
            db_admin = db.query(db_models.User).filter(db_models.User.username == 'admin').first()
            return db_admin
        except Exception as e:
            print('Exception occurred')
            print(f'Exception: {e}')
        finally:
            db.close()

    def update_default_admin(username, password, salt):
        db = SessionLocal()
        try:
            db_admin = db.query(db_models.User).filter(db_models.User.username == 'admin').first()
            db_admin.username = username
            db_admin.password = password
            db_admin.salt = salt
            db.commit()

        except Exception as e:
            print('Exception occurred')
            print(f'Exception: {e}')
        finally:
            db.close()

    def check_db_admin():
        pass

    def update_db_user():
        pass

    def make_db_admin():
        pass

    ##############################
    # Domain Methods
    def get_db_domains(self):
        try:

            db = SessionLocal()

            db_domains = db.query(db_models.AnalysedDomains).all()

            return db_domains

        except Exception as e:
            print('Exception has occured')
            print(f'Exception: {e}')
        finally:
            print('Closing the database')
            db.close()

    def add_db_domain():
        pass

    def update_db_domain():
        pass

    def get_db_recent_domains():
        pass

    def get_malicious_domains():
        pass

    def get_unblocked_domains():
        pass