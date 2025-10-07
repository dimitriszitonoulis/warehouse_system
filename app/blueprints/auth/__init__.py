from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.blueprints.names import ADMIN_BP, AUTH_BP, EMPLOYEE_BP, SUPERVISOR_BP, USER_BP
from app.exceptions.exceptions import (
    UnitNotFoundByIdError,
    UserNotFoundByCredentialsError,
)
from app.model import employee
from app.model.admin import Admin
from app.model.supervisor import Supervisor
from app.model.user import User
from app.services.user_service import UserService


def create_auth_blueprint(user_service: UserService) -> Blueprint:
    auth_bp = Blueprint(AUTH_BP, __name__, template_folder="templates")


    @auth_bp.route("/login", methods=["GET", "POST"])
    def login():
        error = None


        """
        TODO UNCOMMENT THESE
        THEY ARE ONLY COMMENTED FOR TESTING
        """

        # if request.method != "POST":
        #     return render_template("auth/login.html")
        #
        # username = request.form["username"]
        # password = request.form["password"]
        # unit_id  = request.form["unit_id"]
        # username = "js" # employee
        username = "bw" # supervisor
        password = "12"
        unit_id = "u1"

        user: User

        try:
            user = user_service.get_user(username, password, unit_id)
        except (UserNotFoundByCredentialsError, UnitNotFoundByIdError):
            return render_template(f"{AUTH_BP}/login.html", error="Invalid credentials")
        except ValueError:
            return render_template(
                f"{AUTH_BP}/login.html",
                error="The user's record in the database is missing required attributes.",
            )

        session["user_id"] = user.id
        session["unit_id"] = user.unit_id
        session["role"]    = user.role

        return redirect(url_for(f"{USER_BP}.dashboard"))


    @auth_bp.route("/logout", methods=["GET"])
    def logout():
        session.clear()
        return redirect(url_for(f"{AUTH_BP}.login"))


    @auth_bp.route("/permissions", methods=["GET"])
    def missing_permissions():
        return render_template(f"{AUTH_BP}/missing_permissions.html")

    return auth_bp

