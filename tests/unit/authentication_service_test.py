from tests.conftest import db_session
import block_app.models.db_models as db_models


def test_user_creation(db_session):

    user_test = db_models.User(
        username="username",
        password="password",
        salt = "salt",
        role_type=db_models.UserRoleEnum["NORMAL"].value,
    )

    db_session.add(user_test)
    db_session.commit()

    database_user = (
        db_session.query(db_models.User)
        .filter(db_models.User.username == user_test.username)
        .first()
    )

    assert user_test.id is not None
    assert user_test.username == database_user.username
    assert user_test.password == database_user.password
