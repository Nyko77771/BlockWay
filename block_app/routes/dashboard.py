from flask import Blueprint, render_template, request, redirect, session, abort
from block_app.database.database import SessionLocal
import  block_app.models.db_models as db_models
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

    # Opening db connection
    db = SessionLocal()

    # Getting id from session
    print('Current session user: ' + str(session.get('user_id')))
    current_user_id = session.get('user_id')
    user['user_id'] = current_user_id

    db_user = db.query(db_models.User).filter(db_models.User.user_id == current_user_id).first()

    if db_user.user_id is None:
        abort(404)

    if check_user_type(current_user_id):
        user['is_admin'] = True
        print('Getting advanced dash')
        return render_template('admin_templates/dashboard_templates/admin_overview.html', current_user=user)

    return render_template('normal_templates/dashboard_templates/overview.html', current_user=user)

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