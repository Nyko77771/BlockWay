from flask import Blueprint, render_template, request, redirect
from block_app.services.database_service import DomainDatabase
from block_app.services.password_service import password_hashing, password_strength
from block_app.services.log_service import logger
from block_app.services.pihole_formatter_service import PiholeFormatter
from block_app.services.setup_service import NetworkScan

import traceback

setup = Blueprint(
    "setup",
    __name__,
    url_prefix="/setup",
)

# For Pihole Address Redirection
request_count = 0

@setup.route("/admin-setup", methods=["GET", "POST"])
def admin_setup():

    generic_user = {
        "username": "Not Found",
        "password": "Not Given"
    }

    try:

        db = DomainDatabase()
        # Get default admin details
        db_admin = db.get_default_admin()

        if db_admin is None:
            message = 'Please Create an Admin Account'
            return render_template("/setup/new-admin-setup", message=message)

        user = {"username": db_admin.username, "password": db_admin.password}

        if request.method == "POST":

            # Get the form information from request
            admin_request = request.form

            # Get the Username from form
            new_admin_username = admin_request.get("username")
            # Get the Password from form
            new_admin_password = admin_request.get("password")

            # Password Strength Evaluation
            score = password_strength(new_admin_password)
            if score < 5:
                message = "Password does not meet the minimum complexity"
                return render_template(
                    "normal_templates/default-admin.html", message=message, user=user
                )

            #  ADD SALT
            # ADD HASHED PASSWORD
            hashed_values = password_hashing(new_admin_password)

            # Update database with new values
            db.update_default_admin(
                new_admin_username, hashed_values["hash"], hashed_values["salt"]
            )

            db_pihole_address = db.get_pihole_address()

            if db_pihole_address is None:
                return redirect("/setup/pihole")

            return redirect('/dashboard')

    except Exception:
        logger.exception("Exception occurred")
        traceback.print_exc
        message = "Please try again"
        return render_template(
            "normal_templates/default-admin.html", message=message, user=generic_user
        )

    return render_template("normal_templates/default-admin.html", user=user)


@setup.route("/new-admin-setup", methods=["GET", "POST"])
def new_admin_setup():

    return render_template("normal_templates/default-admin-set.html")

@setup.route("/add-pihole", methods=["GET", "POST"])
def add_pihole():
    try:
        if request.method == "POST":

            response = request.form

            given_address = response.get('pihole_address')

            if given_address is None:
                raise Exception

            db = DomainDatabase()
            pihole_formatter = PiholeFormatter()

            if pihole_formatter.check_address(given_address):
                db_pi_address = db.get_pihole_address().__str__
                if db_pi_address:
                    if db_pi_address == given_address:
                        logger.info("Updating Pihole Address")
                        db.update_pihole_address(given_address)


                logger.info("Pihole Address Added")
                db.add_pihole_address(given_address)
                db.create_default_schedule()
                return redirect("/dashboard")
            else:
                message = 'Incorrect Address Format'
                return render_template(
            "normal_templates/pihole_add.html", message=message
        )

    except Exception:
        logger.exception("Exception occurred")
        message = "Please try adding address again"
        return render_template(
            "normal_templates/pihole_add.html", message=message
        )
    return render_template("normal_templates/pihole_add.html")

@setup.route("/pihole", methods=["GET", "POST"])
def setup_pihole():
        try:
            global request_count

            if request.method == "POST":

                if request_count > 3:
                    return render_template("normal_templates/not_found.html")

                response = request.form

                given_address = response.get('manual_add_password')

                if given_address is None:
                    request_count += 1
                    raise NameError

                db = DomainDatabase()
                pihole_formatter = PiholeFormatter()

                if pihole_formatter.check_address(given_address):
                    logger.info("Pihole Address Added")
                    db.add_pihole_address(given_address)
                    db.create_default_schedule()
                    return redirect("/dashboard")
                else:
                    logger.info("Pihole Address is Incorrect")
                    message = 'Incorrect Address Format'
                    return render_template(
                "normal_templates/pihole_add.html", message=message
            )

        except NameError:
            logger.exception("Pihole Address not Found")
            message = 'No Address Provided'
            return render_template(
                            "normal_templates/pihole_add.html", message=message
                        )
        except Exception:
            logger.exception("An Exception was Raised")
            message = 'Something Went Wrong'
            return render_template(
                "normal_templates/pihole_add.html", message=message
            )
        return render_template("normal_templates/pihole_select.html")

@setup.route("/pihole/scan", methods=["GET", "POST"])
def setup_scan():
    try:
        if request.method == "POST":
            net_scan = NetworkScan()

    except Exception:
        logger.exception("An Exception was Raised")
        message = 'Try Adding Pihole Address Again'
        return render_template(
            "normal_templates/pihole_add.html", message=message
        )
    return render_template("normal_templates/pihole_select.html")