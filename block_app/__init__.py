"""This module creates the block_way app"""

import os
import dotenv

# Importing Flask Methods and Objects
from flask_login import LoginManager
from flask import Flask, render_template
from flask_talisman import Talisman
from flask_wtf import CSRFProtect

# Importing Blueprints
from block_app.routes.views import views
from block_app.routes.setup import setup
from block_app.routes.dashboard import dashboard

# Importing Database Method
from block_app.database.database import check_start_db

# Importing Custom CLI Command
from block_app.cli.administrator import admin_reset

# Importing Custom Services
from block_app.services.database_service import DomainDatabase
from block_app.services.log_service import logger
from block_app.services.pihole_service import Pihole

# Import MLThreadManager
from block_app.services.thread_service import MLThreadManager

# Importing Dashboard Services
from block_app.services.dashboard_service import DashboardService

# Importing Start Service
from block_app.services.start_service import StartService

# Loading the enviromental variables
dotenv.load_dotenv()


# Making a function for block app creation
def make_blockway():
    """Defines Flask App"""
    logger.info("Creating Block_App")

    # Creating Flask Instance
    block_app = Flask(__name__)

    # Adding HTTPS and Secure Headers

    csp = {
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": ["'self'", "data:"],
    }

    Talisman(
        block_app,
        content_security_policy=csp,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        strict_transport_security_include_subdomains=True,
    )

    # !!! TO ADD ENCRYPTION HERE!!!
    block_app.secret_key = os.getenv("SECRET")

    # CSRF
    # Adding Anti-CSRF header
    csrf = CSRFProtect()
    csrf.init_app(block_app)

    login_manager = LoginManager()
    login_manager.init_app(block_app)
    login_manager.login_view = "views.signin"  # type: ignore
    login_manager.login_message = "Login to access page."

    @login_manager.user_loader
    def load_user(user_id):
        db = DomainDatabase()
        return db.get_db_user_by_id(user_id)

    # Starting Database
    check_start_db()

    # Initialisn Pihole and adding to pihole_service
    pihole_service = Pihole()

    start_service = StartService(pihole_service)

    block_app.extensions["pihole_service"] = pihole_service

    block_app.extensions["dashboard_service"] = DashboardService(
        block_app.extensions["pihole_service"]
    )

    block_app.extensions["start_service"] = start_service

    # Defining the routes functions inside the app via flask blueprint
    block_app.register_blueprint(views)
    block_app.register_blueprint(setup)
    block_app.register_blueprint(dashboard)
    # CLI Commands
    block_app.cli.add_command(admin_reset)

    # 404 Page
    # Handling Not Found Errors Globally
    @block_app.errorhandler(404)
    def page_not_found(error):
        logger.error("Error: %s", error)
        return render_template("404.html"), 404

    # Starting The ML Scanning Thread using class method
    MLThreadManager.start(start_service)

    return block_app
