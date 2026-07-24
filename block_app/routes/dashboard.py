# Importing threading module
import threading

# Importing Flask Services
from flask import Blueprint, render_template, session, abort, jsonify
from flask_login import login_required, current_user

# Importing Custom Services
from block_app.services.pihole_service import Pihole
from block_app.services.database_service import DomainDatabase
from block_app.services.dashboard_service import DashboardService
from block_app.services.log_service import logger
# Importing ML Generating Method
from block_app.services.run_ml_start_service import start_scheduler

import traceback

from block_app.routes.user_check import check_user_type

dashboard = Blueprint(
    "dashboard",
    __name__,
)

user = {"user_id": None, "is_admin": False}


@dashboard.before_request
@login_required
def dash_checks():

    # Checking if Pihole Address is Present
    logger.info("Checking Pihole Address")
    pihole = Pihole()
    if not pihole.contains_address():
        logger.error('No Pihole Address Found')#
        message = 'Address Could not be reached. Try Again'
        return render_template('/normal_templates/pihole_add.html', message=message)

    # Getting id from session
    if current_user.is_authenticated:
        logger.info("Current session user: " + str(current_user.id))
        user["user_id"] = current_user.id

    # Checking Pihole Connection
    if not pihole.connectionn_checker.is_connected():
        logger.error('Cant Establish Pihole Connection')
        message = 'Pihole address could not be reached'
        return render_template('/normal_templates/pihole_add.html', message=message)

@dashboard.route("/dashboard", methods=["GET"])
def home():

    try:

        user_id = user["user_id"]

        db = DomainDatabase()

        db_user = db.get_db_user_by_id(user_id)

        if db_user is None:
            raise Exception

        if db_user.id is None:
            abort(404)

        if check_user_type(user_id):
            user["is_admin"] = True
            print("Getting advanced dash")
            return render_template(
                "admin_templates/dashboard_templates/admin_system_details.html",
                current_user=user,
            )

        # Performing ML Analyses
        # Using Threadding to run ML scan concurrently
        thread = threading.Thread(target=start_scheduler, daemon=True)
        thread.start()
        logger.info("Starting ML Thread")
        logger.info(f'Active Threads: {threading.active_count()}')

        # Initialising Dashboard Services
        dash_service = DashboardService()

        # Getting general Statistical Information
        basic_stats = dash_service.get_stats()

        # Getting Data for Table
        table_data = dash_service.get_table_data(True)

        # Getting Data for Graphs

        # 1. Getting General Graph Information
        activity_graph = dash_service.get_last_24_hours()

        # 2. Getting Information for Chart Graph
        chart_graph = dash_service.get_blocked_allowed_totals()

        return render_template(
            "normal_templates/dashboard_templates/overview.html", current_user=user,
            basic_stats=basic_stats,
            activity_graph=activity_graph,
            chart_graph=chart_graph,
            table_data=table_data
        )

    except Exception as e:
        print("EXCEPTION in DASH")
        traceback.print_exc()
        message = "Something Went Wrong. Please Log In Again"
        user["user_id"] = None
        session.clear()
        return render_template(
            "unregistered_templates/home.html", current_user=user, message=message
        )


##################################################################
# TO DO:

# Normal Users


@dashboard.route("/threats", methods=["GET"])
def threats():
    return render_template(
        "normal_templates/dashboard_templates/threats.html", current_user=user
    )


@dashboard.route("/system", methods=["GET"])
def system():
    return render_template("normal_templates/dashboard_templates/system.html", current_user=user)


@dashboard.route("/settings", methods=["GET"])
def settings():
    return render_template("normal_templates/dashboard_templates/settings.html", current_user=user)


# Advanced Users


@dashboard.route("/configurations", methods=["GET"])
def configurations():
    return render_template(
        "normal_templates/dashboard_templates/admin_configurations.html"
    )


@dashboard.route("/logs", methods=["GET"])
def logs():
    return render_template("normal_templates/dashboard_templates/admin_logs.html")


@dashboard.route("/users", methods=["GET"])
def users():
    return render_template("normal_templates/dashboard_templates/admin_users.html")


@dashboard.route("/ml", methods=["GET"])
def ml():
    return render_template("normal_templates/dashboard_templates/admin_ml.html")
