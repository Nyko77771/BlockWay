from block_app.services.database_service import DomainDatabase


def check_user_type(user_id):
    try:
        print("Checking user type")

        db = DomainDatabase()

        db_user = db.get_db_user_by_id(user_id)

        if db_user.role_type == "admin":
            print("Current user is admin")
            return True
        return False
    except Exception as e:
        print("Exception occured while checking type")
        print(f"Exception: {e}")
        return False
