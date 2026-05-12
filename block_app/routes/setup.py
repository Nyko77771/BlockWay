from flask import Blueprint, render_template, request, redirect
from block_app.database.database import engine, SessionLocal
import  block_app.models.db_models as db_models
# import hashlib

setup = Blueprint(
    'setup',
    __name__,
    url_prefix="/setup",
)

@setup.route('/admin-setup', methods=['GET','POST'])
def admin_setup():

    # Establish db connection
    db = SessionLocal()

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

        # Update database with new values

        db_admin.username = new_admin_username
        db_admin.password = new_admin_password

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


    return render_template('default-admin.html', user=user)


@setup.route('/pihole')
def setup_pihole():
    return render_template('pihole_select.html')
