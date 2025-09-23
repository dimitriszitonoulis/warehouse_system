from typing import Optional, Union
from flask import Blueprint, redirect, request, session, render_template, flash
from app.blueprints.names import EMPLOYEE_BP, USER_BP
from app.exceptions.exceptions import UnitNotFoundByIdError, UserNotFoundByIdError
from app.model.admin import Admin
from app.model.employee import Employee
from app.model.supervisor import Supervisor
from app.model.user import User
from app.services.employee_service import EmployeeService
from app.services.user_service import UserService
from app.types import UserOrSubclass
from app.utils.auth_utils import login_required, required_role
from app.services.user_service import UserService


def create_user_blueprint(user_service: UserService):
    user_bp = Blueprint(USER_BP, __name__, template_folder="templates")


    @user_bp.route("/", methods=["GET"])
    @login_required
    def dashboard():
        return render_template("user/dashboard.html", role=session["role"])



    def _try_get_user(user_id: str) -> Union[Employee, Supervisor, Admin, str]:
        try:
            # return emp_service.get_employee_by_id(employee_id)
            return user_service.get_user_by_id(user_id)
        except (UserNotFoundByIdError, UnitNotFoundByIdError):
            return "Could not find user"
        except ValueError:
            return "The user's record in the database is missing required attributes."


    @user_bp.route("/profile", methods=["GET"])
    @login_required
    @required_role("employee")
    def show_profile():
        show_profile_page = "user/profile.html"
        employee_id: str = session["user_id"]

        user: User

        result = _try_get_user(employee_id)

        if isinstance(result, str):
            return render_template(show_profile_page, error=result)

        user = result
        return render_template(
            show_profile_page,
            name      = user.name,
            surname   = user.surname,
            username  = user.username,
            unit_id   = user.unit_id,
            unit_name = user.unit_name
        )


    @user_bp.route("/change-password", methods=["GET", "POST"])
    @login_required
    @required_role("employee")
    def change_password():
        change_password_page = "user/change-password.html"
        user_id = session["user_id"]
        user: User
        is_password_changed: bool

        if request.method != "POST":
            return render_template(change_password_page)

        # the old password is used for verification
        password_old = request.form.get("password_old")
        password_new = request.form.get("password_new")

        if not password_old or not password_new:
            return render_template(
                change_password_page, error="Both fields are required."
            )

        if password_old == password_new:
            return render_template(
                change_password_page,
                error="Previous password cannot be the same as new password.",
            )

        result = _try_get_user(user_id)

        if isinstance(result, str):
            return render_template(change_password_page, error=result)

        user = result

        if user.password != password_old:
            return render_template(
                change_password_page, error="Previous password is incorrect."
            )

        is_password_changed = user_service.change_password(user_id, password_new)

        if is_password_changed is False:
            return render_template(
                change_password_page, error="Could not change password."
            )

        flash("Password successfully changed!", "success")
        # return redirect(render_template("employee/change-password.html"))
        return render_template(change_password_page)


    return user_bp
