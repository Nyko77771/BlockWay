from flask import Blueprint, render_template, request, redirect, session
import sqlite3

# Database connection setup
def db_connect():
    if sqlite3.connect('users.db'):
        print("Database connection successful.")
    else:
        print("Database connection failed.")
    return sqlite3.connect('users.db')

views = Blueprint(
    'views',
    __name__,
)

@views.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@views.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@views.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        request_data = request.form
        username = request_data.get('username')
        return redirect('/')
    return render_template('signin.html')
