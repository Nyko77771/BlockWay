from flask import Blueprint, render_template, request, redirect, session, abort
from block_app.routes.dashboard import check_user_type
from block_app.services.database_service import DomainDatabase

settings = Blueprint(
    'settings',
    __name__,
)

user = {
    'user_id': None,
    'is_admin': False,
}

@settings.route('/settings', methods=['GET', 'POST'])
def home():

    print('Current session user: ' + str(session.get('user_id')))
    current_user_id = session.get('user_id')
    user['user_id'] = current_user_id
    print('User id:')
    print(str(user['user_id']))

    db_user = DomainDatabase.get_db_user_by_id(current_user_id)

    if db_user.user_id is None:
        abort(404)

    if check_user_type(current_user_id):
        user['is_admin'] = True
        print('Getting advanced settings')
        return render_template('admin_templates/settings_templates/admin_settings.html', current_user=user)

    return render_template('normal_templates/settings_templates/account_settings.html', current_user=user)

# TO DO:

@settings.route('/email', methods=['GET'])
def email():
    print('User id:')
    print(str(user['user_id']))
    return render_template('normal_templates/settings_templates/email_settings.html', current_user=user)

@settings.route('/theme', methods=['GET'])
def theme():
    print('User id:')
    print(str(user['user_id']))
    return render_template('normal_templates/settings_templates/theme_settings.html', current_user=user)