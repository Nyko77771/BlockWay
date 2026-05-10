from flask import Blueprint, render_template, request, redirect, session

setup = Blueprint(
    'setup',
    __name__,
    url_prefix="/setup",
)

@setup.route('/admin-setup', methods=['GET','POST'])
def admin_setup():
    return render_template('default-admin.html')
