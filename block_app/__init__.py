from flask import Flask, jsonify, render_template
from block_app.routes.views import views
from block_app.routes.setup import setup
from block_app.routes.dashboard import dashboard
from block_app.routes.settings import settings
from block_app.database.database import check_start_db

# Making a function for block app creation
def make_blockway():
    # Creating Flask Instance
    block_app = Flask(__name__)

    # !!! TO ADD ENCRYPTION HERE!!!
    block_app.secret_key = 'ADD ENCRYPTED KEY HERE'

    # Defining the routes functions inside the app via flask blueprint
    block_app.register_blueprint(views)
    block_app.register_blueprint(setup)
    block_app.register_blueprint(dashboard)
    block_app.register_blueprint(settings)

    # 404 Page
    # Handling Not Found Errors Globally
    @block_app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html')

    # Starting Database
    check_start_db()
    return block_app