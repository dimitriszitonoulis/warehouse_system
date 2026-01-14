from typing import Optional
from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.blueprints.names import AUTH_BP, USER_BP
from app.exceptions.exceptions import (
    UnitNotFoundByIdError,
    UserNotFoundByCredentialsError,
)
from app.model.user import User
from app.services.user_service import UserService


def create_auth_blueprint(user_service: UserService) -> Blueprint:
    auth_bp = Blueprint(AUTH_BP, __name__, template_folder="templates")


    @auth_bp.route("/login", methods=["GET", "POST"])
    def login():

        if request.method != "POST":
            return render_template(f"{AUTH_BP}/login.html")

        username = request.form["username"]
        password = request.form["password"]
        unit_id  = request.form["unit_id"]

        user: Optional[User] = None

        try:
            user = user_service.get_user(username, password, unit_id)
        except (UserNotFoundByCredentialsError, UnitNotFoundByIdError):
            return render_template(f"{AUTH_BP}/login.html", error="Invalid credentials")
        except ValueError:
            return render_template(
                f"{AUTH_BP}/login.html",
                error="The user's record in the database is missing required attributes."
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

