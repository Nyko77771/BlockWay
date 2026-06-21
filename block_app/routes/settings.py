from flask import Blueprint, render_template, request, redirect, session, abort
from block_app.routes.dashboard import check_user_type

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
    print('User id:')
    print(str(user['user_id']))
    return render_template('normal_templates/settings_templates/account_security.html', current_user=user)

@settings.route('/email', methods=['GET'])
def email():
    print('User id:')
    print(str(user['user_id']))
    return render_template('normal_templates/settings_templates/account_security.html', current_user=user)