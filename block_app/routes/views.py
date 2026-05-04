from flask import Blueprint, render_template, request, redirect, session
import sqlite3

# Tracking Variables
current_user = {
    "authenticated": None
}
session = ""

views = Blueprint(
    'views',
    __name__,
)

def authenticate_user():
    if session is None:
        current_user["authenticated"] = False
    current_user["authenticated"] = True

@views.route('/', methods=['GET'])
def home():
    authenticate_user()
    return render_template('home.html', current_user=current_user)

@views.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@views.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        request_data = request.form
        username = request_data.get('username')
        password = request_data.get('password')
        confirm_password = request_data.get('confirm_password')
        return redirect('/')
    authenticate_user()
    return render_template('signin.html', current_user=current_user)
