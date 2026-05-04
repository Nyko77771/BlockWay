from flask import Flask, jsonify;
from block_app.routes.views import views
from block_app.database.database import check_start_db

# Making a function for block app creation
def make_blockway():
    # Creating Flask Instance
    block_app = Flask(__name__)
    # Defining the routes functions inside the app via flask blueprint
    block_app.register_blueprint(views)
    # Starting Database
    check_start_db()
    return block_app