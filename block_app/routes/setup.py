from flask import Blueprint, render_template, request, redirect
from block_app.database.database import engine, SessionLocal
import  block_app.models.db_models as db_models
from block_app.services.password_service import password_hashing, password_strength

setup = Blueprint(
    'setup',
    __name__,
    url_prefix="/setup",
)

@setup.route('/admin-setup', methods=['GET','POST'])
def admin_setup():

    # Establish db connection
    db = SessionLocal()
    try:
        # Get default admin details
        db_admin = db.query(db_models.User).filter(db_models.User.username == 'admin').first()
        user = {
            'username': db_admin.username,
            'password': db_admin.password
        }

        if request.method == 'POST':

            # Get the form information from request
            admin_request = request.form

            # Get the Username from form
            new_admin_username = admin_request.get('username')
            # Get the Password from form
            new_admin_password = admin_request.get('password')

            # TO BE DELETED
            # Checking values
            print('New User is:')
            print(str(new_admin_username))
            print('##############')
            print('New password is:')
            # TO BE DELETED

            # Password Strength Evaluation
            score = password_strength(new_admin_password)
            if score < 0:
                message = 'Password does not meet the minimum complexity'
                return render_template('normal_templates/default-admin.html', message = message, user=user)

            #  ADD SALT
            # ADD HASHED PASSWORD
            hashed_values = password_hashing(new_admin_password)

            # Update database with new values
            db_admin.username = new_admin_username
            db_admin.password = hashed_values['hash']
            db_admin.salt = new_admin_password['salt']


            db.commit()

            # TO DELETE
            # CHECK
            db_admin_check = db.query(db_models.User).filter(db_models.User.role_type == 'admin').first()

            print('New username:')
            print(str(db_admin_check.username))
            print('New password:')
            print(str(db_admin_check.password))


            # Close Database
            db.close()

            return redirect('/pihole')
    except Exception as e:
        print('Exception occurred')
        print(f'Exception: {e}')
        message = 'Please try again'
        return render_template('normal_templates/default-admin.html', message = message, user=user)


    return render_template('normal_templates/default-admin.html', user=user)


@setup.route('/pihole')
def setup_pihole():
    return render_template('normal_templates/pihole_select.html')
