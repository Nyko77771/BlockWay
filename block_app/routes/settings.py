from flask import Blueprint, render_template, request, redirect, session, abort

settings = Blueprint(
    'settings',
    __name__,
)

@settings.route('/', methods=['GET'])
def settings_home():
    return render_template('normal_templates/dashboard_templates/settings.html')