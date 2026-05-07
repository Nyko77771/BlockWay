from flask import Blueprint, render_template, request, redirect, session
from backend_server.block_app.database.database import engine, SessionLocal
import  block_app.models.models as models


# Tracking Variables
current_user = {
    "authenticated": None,
    "new_user": None
}

views = Blueprint(
    'views',
    __name__,
)


def authenticate_user():
    if not session.get('name'):
        current_user["authenticated"] = False
    current_user["authenticated"] = True

@views.route('/', methods=['GET'])
def home():
    authenticate_user()
    return render_template('home.html', current_user=current_user)

@views.route('/signup', methods=['GET'])
def signup():
    authenticate_user()
    return render_template('signup.html', current_user=current_user)

@views.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Establishing db connection
        db = SessionLocal()

        # Obtain Provided Information
        request_data = request.form
        given_username = request_data.get('username')
        given_password = request_data.get('password')

        # Get Database details
        db_username = db.query(models.User).filter(models.User.username == given_username).first()

        # Check if db has found user
        if db_username is None:
            return render_template('/signup', message='Not found')

        #Check the passwords
        db_password = db_username.password

        if db_password != given_password:
            render_template('/signup', message='Passwords do not match')

        session['user'] = db_username.user_id

        return redirect('/dashboard')



    authenticate_user()
    return render_template('signin.html', current_user=current_user)
