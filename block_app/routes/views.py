from flask import Blueprint, render_template, request, redirect, session, abort
from block_app.database.database import SessionLocal
import  block_app.models.db_models as db_models
from block_app.database.database import check_admin
from block_app.routes.user_check import check_user_type
from block_app.services.password_service import password_hashing, password_strength

# Tracking Variables
current_user = {
    "user_id": None,
    "new_user": None,
    "is_admin": False
}

views = Blueprint(
    'views',
    __name__,
)
#######################################
# To Remove
def get_user_type(user_id):
    # Opening db connection
    db = SessionLocal()
    print('Checking user type')

    db_user = db.query(db_models.User).filter(db_models.User.user_id == user_id).first()

    if db_user.role_type == "admin":
        print('Current user is admin')
        current_user['is_admin'] = True
    print('User is not admin')
    # Closing db connection
    db.close()
#########################################

# Method for checjking whether user was authenticated
@views.before_request
def get_id():
    current_user['user_id'] = session.get('user_id')

# Home Route - Initial Page
@views.route('/', methods=['GET'])
def home():
    return render_template('unregistered_templates/home.html', current_user=current_user)

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
            return render_template('unregistered_templates/signup.html', message='Passwords do not match!', current_user=current_user)


        # 1. PASSWORD COMPLEXITY CHECK
        score = password_strength(given_password)
        if score < 5:
            return render_template('unregistered_templates/signup.html', message='Password does not meet the minimum complexity', current_user=current_user)


        # Check username
        # Get username from db
        db_user = db.query(db_models.User).filter(db_models.User.username == given_username).first()

        db_username = db_user.username if db_user and db_user.username is not None else ''


        if db_username == given_username:
            return render_template('unregistered_templates/signup.html', message='Use different username', current_user=current_user)

        # 2. PASSWORD HASHING + SALTING
        hashed_values = password_hashing(given_password)
        hashed_password = hashed_values['hash']
        password_salt = hashed_values['salt']

        try:
            new_user = db_models.User(
                username = given_username,
                password = hashed_password,
                salt = password_salt,
                role_type = db_models.UserRoleEnum['NORMAL'].value,
            )


            db.add(new_user)
            db.commit()

            # Get User ID from db
            new_db_user = db.query(db_models.User).filter(db_models.User.username == given_username).first()

            # Establishing a session
            session['user_id'] = new_db_user.user_id

            if check_admin():
                return redirect('/setup/admin-setup')

            print('Closing the Database')
            db.close()

            print('Redirecting to dashboard')
            return redirect('/dashboard')

        except:
            return render_template('unregistered_templates/signup.html', message='Something went wrong.Try again', current_user=current_user)

    return render_template('unregistered_templates/signup.html', current_user=current_user)


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
            return render_template('unregistered_templates/signup.html', message='Not found', current_user=current_user)

        #Check the passwords
        db_password = db_username.password
        db_salt = db_username.salt

        # Hash given password
        given_hashed= password_hashing(given_password, db_salt)
        given_hashed_password = given_hashed['hash']

        # If Passwords don't match ask user to sign-in again
        if db_password != given_hashed_password:
            render_template('unregistered_templates/signin.html', message='Passwords do not match', current_user=current_user)

        session['user_id'] = db_username.user_id
        db.close()
        return redirect('/dashboard')


    return render_template('unregistered_templates/signin.html', current_user=current_user)

# Route for Features
@views.route('/features')
def features():
    return render_template('unregistered_templates/features.html', current_user=current_user)

# Route for About
@views.route('/about')
def about():
    return render_template('unregistered_templates/about.html', current_user=current_user)

# NORMAL REGISTERED USER PAGES

# Route for Logout
@views.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Method for Changing App Theme
@views.get('/change-theme')
def change_theme():
    current_theme = session.get('theme')
    if current_theme == 'dark':
        session['theme'] = 'light'
    else:
        session['theme'] = 'dark'

    return redirect(request.args.get('current_page'))
