from flask import Blueprint, render_template, request, redirect, session
from flask_login import login_user, logout_user, current_user

# Importing Custom Methods
from block_app.services.database_service import DomainDatabase
from block_app.services.pihole_formatter_service import PiholeFormatter
from block_app.database.database import check_admin


from block_app.services.password_service import password_hashing, password_strength

# Tracking Variables
backend_current_user = {"user_id": None, "new_user": None, "is_admin": False}

views = Blueprint(
    "views",
    __name__,
)


# Method for checking whether user was authenticated
@views.before_request
def get_id():
    if current_user.is_authenticated:
        backend_current_user["user_id"] = current_user.id
    else:
        redirect('/signin')


# Home Route - Initial Page
@views.route("/", methods=["GET"])
def home():
    return render_template(
        "unregistered_templates/home.html", current_user=backend_current_user
    )


# Route for Signup page
@views.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:

            # Get the data from the request
            request_data = request.form

            given_username = request_data.get("username")
            given_password = request_data.get("password")
            given_confirm_password = request_data.get("confirm_password")
            given_pi_address = request_data.get("address")

            # Checking if provided passwords match
            if given_password != given_confirm_password:
                return render_template(
                    "unregistered_templates/signup.html",
                    message="Passwords do not match!",
                    current_user=backend_current_user,
                )

            # 1. PASSWORD COMPLEXITY CHECK
            score = password_strength(given_password)
            if score < 5:
                return render_template(
                    "unregistered_templates/signup.html",
                    message="Password does not meet the minimum complexity",
                    current_user=backend_current_user,
                )

            # Initialing DomainDatabase class
            db = DomainDatabase()

            # Check username
            # Get username from db
            db_user = db.get_db_user_by_username(given_username)

            db_username = (
                db_user.username if db_user and db_user.username is not None else ""
            )

            if str(db_username) == str(given_username):
                print("Found User")
                return render_template(
                    "unregistered_templates/signup.html",
                    message="Use different username",
                    current_user=backend_current_user,
                )

            # 2. PASSWORD HASHING + SALTING
            print("Getting hashes")
            hashed_values = password_hashing(given_password)
            hashed_password = hashed_values["hash"]
            password_salt = hashed_values["salt"]

            db.add_db_user(given_username, hashed_password, password_salt)

            # Get User ID from db
            new_db_user = db.get_db_user_by_username(given_username)

            if new_db_user is None:
                raise Exception

            # Checking Pihole Address
            pi_formatter = PiholeFormatter()
            result = pi_formatter.check_address(str(given_pi_address))
            if result:
                # Adding Pihole address
                db.add_pihole_address(given_pi_address)
                db.create_default_schedule()
            else:
                render_template(
        "unregistered_templates/signup.html",current_user=backend_current_user, message="Please Enter URL address with a port number"
    )

            # Establishing a session
            login_user(new_db_user)

            if check_admin():
                return redirect("/setup/admin-setup")

            print("Redirecting to dashboard")
            return redirect("/dashboard")

        except Exception as e:
            print("Exception occured")
            print(f"Exception: {e}")
            return render_template(
                "unregistered_templates/signup.html",
                message="Something went wrong.Try again",
                current_user=backend_current_user,
            )

    return render_template(
        "unregistered_templates/signup.html", current_user=backend_current_user
    )


@views.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":

        try:

            # Obtain Provided Information
            request_data = request.form
            given_username = request_data.get("username")
            given_password = request_data.get("password")

            # Initialing Domain Database
            db = DomainDatabase()

            # Get Database details
            db_username = db.get_db_user_by_username(given_username)

            # Check if db has found user
            if db_username is None:
                return render_template(
                    "unregistered_templates/signup.html",
                    message="Not found",
                    current_user=backend_current_user,
                )

            # Check the passwords
            db_password = db_username.password
            db_salt = db_username.salt

            # Hash given password
            given_hashed = password_hashing(given_password, db_salt)
            given_hashed_password = given_hashed["hash"]

            # If Passwords don't match ask user to sign-in again
            if db_password != given_hashed_password:
                render_template(
                    "unregistered_templates/signin.html",
                    message="Passwords do not match",
                    current_user=backend_current_user,
                )

            login_user(db_username)

            return redirect("/dashboard")
        except Exception as e:
            print("Exception occured")
            print(f"Exception: {e}")
            return render_template(
                "unregistered_templates/signin.html",
                message="Something went wrong.Try again",
                current_user=backend_current_user,
            )

    return render_template(
        "unregistered_templates/signin.html", current_user=backend_current_user
    )


# Route for Features
@views.route("/features")
def features():
    return render_template(
        "unregistered_templates/features.html", current_user=backend_current_user
    )


# Route for About
@views.route("/about")
def about():
    return render_template(
        "unregistered_templates/about.html", current_user=backend_current_user
    )


# NORMAL REGISTERED USER PAGES


# Route for Logout
@views.route("/logout")
def logout():
    logout_user()
    return render_template(
        "unregistered_templates/home.html", current_user=backend_current_user
    )


# Method for Changing App Theme
@views.get("/change-theme")
def change_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))  # type: ignore
