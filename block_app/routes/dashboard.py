# Importing Flask Services
from flask import Blueprint, render_template, session, abort, jsonify
from flask_login import login_required, current_user
# Importing Custom Services
from block_app.services.pihole_service import Pihole
from block_app.services.database_service import DomainDatabase
from block_app.services.dashboard_service import DashboardService
from block_app.services.log_service import logger



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
    logger.info("Current session user: " + str(session.get("user_id")))
    current_user_id = session.get("user_id")
    user["user_id"] = current_user_id



@dashboard.route("/dashboard", methods=["GET"])
def home():

    try:

        user_id = user["user_id"]

        db = DomainDatabase()

        db_user = db.get_db_user_by_id(user_id)

        if db_user is None:
            raise Exception

        if db_user.user_id is None:
            abort(404)

        if check_user_type(user_id):
            user["is_admin"] = True
            print("Getting advanced dash")
            return render_template(
                "admin_templates/dashboard_templates/admin_system_details.html",
                current_user=user,
            )

        # Initialising Dashboard Services
        dash_service = DashboardService()

        # Getting Data for Table
        table_data = dash_service.get_table_data()

        # Getting Data for Graphs
        # Getting Gfeneral Graph Information
        general_graph = dash_service.get_last_24_hours()
        general_graph_json = jsonify(general_graph)

        return render_template(
            "normal_templates/dashboard_templates/overview.html", current_user=user,
            general_graph=general_graph,
            table_data=table_data
        )

    except Exception as e:
        print("Exception occurred")
        print(f"Exception: {e}")
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
