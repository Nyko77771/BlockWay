from flask import Blueprint, render_template, request, redirect, session, abort
from block_app.services.database_service import DomainDatabase

from block_app.routes.user_check import check_user_type

dashboard = Blueprint(
    'dashboard',
    __name__,
)

user = {
    "user_id": None,
    "is_admin": False
}

@dashboard.route('/dashboard', methods=['GET'])
def home():

    try:

        # Getting id from session
        print('Current session user: ' + str(session.get('user_id')))
        current_user_id = session.get('user_id')
        user['user_id'] = current_user_id

        db_user = DomainDatabase.get_db_user_by_id(current_user_id)

        if db_user.user_id is None:
            abort(404)

        if check_user_type(current_user_id):
            user['is_admin'] = True
            print('Getting advanced dash')
            return render_template('admin_templates/dashboard_templates/admin_overview.html', current_user=user)

        return render_template('normal_templates/dashboard_templates/overview.html', current_user=user)
    
    except Exception as e:
        print('Exception occurred')
        print(f'Exception: {e}')
        message='Something Went Wrong. Please Log In Again'
        session.clear()
        return render_template('unregistered_templates/home.html', current_user=user, message = message)
    finally:
        print('Closing db connection')
        db.close()


##################################################################
# TO DO:

@dashboard.route('/threats', methods=['GET'])
def threats():
    return render_template('normal_templates/dashboard_templates/threats.html')

@dashboard.route('/rules', methods=['GET'])
def rules():
    return render_template('normal_templates/dashboard_templates/rules.html')

@dashboard.route('/system', methods=['GET'])
def system():
    return render_template('normal_templates/dashboard_templates/system.html')