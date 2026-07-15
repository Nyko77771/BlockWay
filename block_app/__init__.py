from flask import Flask, render_template
from flask_talisman import Talisman
from block_app.routes.views import views
from block_app.routes.setup import setup
from block_app.routes.dashboard import dashboard
from block_app.database.database import check_start_db
from block_app.cli.administrator import admin_reset
import os
import dotenv

# Loading the enviromental variables
dotenv.load_dotenv()

# Making a function for block app creation
def make_blockway():
    # Creating Flask Instance

    block_app = Flask(__name__)

    # Adding HTTPS and Secure Headers
    talisman = Talisman(block_app)

    # HTTP Strict Transport Security Header
    hsts = {
        'max-age': 31536000,
        'includeSubDomains': True
    }

    csp = {
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": ["'self'", "data:"],
    }

    talisman.x_xss_protection = True
    talisman.strict_transport_security = hsts
    talisman.content_security_policy = csp

    # !!! TO ADD ENCRYPTION HERE!!!
    block_app.secret_key = os.getenv("SECRET")

    # Defining the routes functions inside the app via flask blueprint
    block_app.register_blueprint(views)
    block_app.register_blueprint(setup)
    block_app.register_blueprint(dashboard)
    # CLI Commands
    block_app.cli.add_command(admin_reset)

    # 404 Page
    # Handling Not Found Errors Globally
    @block_app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # Starting Database
    check_start_db()
    return block_app
