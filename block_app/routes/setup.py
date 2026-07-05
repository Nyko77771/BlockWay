from flask import Blueprint, render_template, request, redirect
from block_app.services.database_service import DomainDatabase
from block_app.services.password_service import password_hashing, password_strength

setup = Blueprint(
    'setup',
    __name__,
    url_prefix="/setup",
)

@setup.route('/admin-setup', methods=['GET','POST'])
def admin_setup():

    try:
        # Get default admin details
        db_admin = DomainDatabase.get_default_admin()

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

            # Password Strength Evaluation
            score = password_strength(new_admin_password)
            if score < 5:
                message = 'Password does not meet the minimum complexity'
                return render_template('normal_templates/default-admin.html', message = message, user=user)

            #  ADD SALT
            # ADD HASHED PASSWORD
            hashed_values = password_hashing(new_admin_password)

            # Update database with new values
            DomainDatabase.update_default_admin(new_admin_username, hashed_values['hash'], hashed_values['salt'])

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
