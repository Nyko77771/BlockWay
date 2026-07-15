from flask import Blueprint, render_template, session, abort
from block_app.services.database_service import DomainDatabase

from block_app.routes.user_check import check_user_type

dashboard = Blueprint(
    "dashboard",
    __name__,
)

user = {"user_id": None, "is_admin": False}


@dashboard.before_request
def get_id():
    # Getting id from session
    print("Current session user: " + str(session.get("user_id")))
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

        return render_template(
            "normal_templates/dashboard_templates/overview.html", current_user=user
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
    return render_template("normal_templates/dashboard_templates/system.html")


@dashboard.route("/settings", methods=["GET"])
def settings():
    return render_template("normal_templates/dashboard_templates/settings.html")


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
