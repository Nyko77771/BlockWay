from flask import Blueprint, render_template, request, redirect, session, abort
from block_app.routes.dashboard import get_user_type

settings = Blueprint(
    'settings',
    __name__,
)

user = {
    'user_id': None,
    'is_admin': False,
}

@settings.route('/settings', methods=['GET', 'POST'])
def settings_home():
    print('User id:')
    print(str(user['user_id']))
    return render_template('normal_templates/settings_templates/account_security.html', current_user=user)