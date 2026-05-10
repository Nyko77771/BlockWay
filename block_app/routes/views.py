from flask import Blueprint, render_template, request, redirect, session
from block_app.database.database import engine, SessionLocal
import  block_app.models.db_models as db_models
from block_app.database.database import check_admin


# Tracking Variables
current_user = {
    "user_id": None,
    "new_user": None
}

views = Blueprint(
    'views',
    __name__,
)

# Method for checjking whether user was authenticated

@views.before_request
def get_id():
    current_user['user_id'] = session.get('user_id')

@views.route('/', methods=['GET'])
def home():
    return render_template('home.html', current_user=current_user)

# Route for Signup page
@views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get database connection (db)
        db = SessionLocal()

        # Get the data from the request
        request_data = request.form

        given_username = request_data.get('username')
        given_password = request_data.get('password')
        given_confirm_password = request_data.get('confirm_password')

        # Checking if provided passwords match
        if given_password != given_confirm_password:
            return render_template('/signup', message='Passwords do not match!')

        # TO ADD:
        # 1. PASSWORD COMPLEXITY CHECK
        # 2. PASSWORD HASHING + SALTING

        # Check username
        # Get username from db
        db_user = db.query(db_models.User).filter(db_models.User.username == given_username).first()

        db_username = db_user.username if db_user and db_user.username is not None else ''

        # TO ADD
        # PASSWORD DECTRYPTION

        if db_username == given_username:
            return render_template('signup.html', message='Use different username', current_user=current_user)

        try:
            new_user = db_models.User(
                username = given_username,
                password = given_password,
                role_type = db_models.UserRoleEnum['NORMAL'].value,
            )

            if check_admin():
                session['user_id'] = new_user.user_id
                return redirect('/setup/admin-setup')

            db.add(new_user)
            db.commit()
            print('Closing the Database')
            db.close()

            print('Redirecting to dashboard')
            return render_template('dashboard.html')

        except:
            authenticate_user()
            return render_template('signup.html', message='Something went wrong.Try again', current_user=current_user)





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
        db_username = db.query(db_models.User).filter(db_models.User.username == given_username).first()

        # Check if db has found user
        if db_username is None:
            authenticate_user()
            return render_template('signup.html', message='Not found', current_user=current_user)

        #Check the passwords
        db_password = db_username.password

        # TO ADD:
        # SECURE PASSWORD
        # PASSWORD DECRYPTION

        if db_password != given_password:
            authenticate_user()
            render_template('signup.html', message='Passwords do not match', current_user=current_user)

        session['user_id'] = db_username.user_id
        db.close()
        return redirect('/dashboard')



    authenticate_user()
    return render_template('signin.html', current_user=current_user)

# Route for Dashboard
@views.route('/dashboard')
def dashboard():
    print('Current session user: ' + str(session['user_id']))
    authenticate_user()
    return render_template('dashboard.html', current_user=current_user)

# Route for Logout
@views.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Route for Settings
@views.route('/settings')
def settings():
    return render_template('/settings', current_user=current_user)