from typing import List, Optional

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from pymongo.errors import DuplicateKeyError

from app.blueprints.names import USER_BP
from app.exceptions.exceptions import UnitNotFoundByIdError, UserNotFoundByIdError
from app.model.employee import Employee
from app.model.user import User
from app.services.employee_service import EmployeeService
from app.services.user_service import UserService
from app.utils.auth_utils import login_required, required_role


def create_user_blueprint(
    user_service: UserService,
    employee_service: EmployeeService
    ):
    user_bp = Blueprint(USER_BP, __name__, template_folder="templates")

    @user_bp.errorhandler(UserNotFoundByIdError)
    def user_not_found_by_id_error(e):
        return render_template(
            "user/error.html",
            error     = "Could not find user.",
            prev_page = request.referrer,
            endpoint  = request.endpoint,
        )

    @user_bp.errorhandler(UserNotFoundByIdError)
    def user_not_found_by_credentials_error(e):
        return render_template(
            "user/error.html",
            error     = "Could not find user.",
            prev_page = request.referrer,
            endpoint  = request.endpoint,
        )


    @user_bp.errorhandler(UnitNotFoundByIdError)
    def unit_not_found_by_id_error(e):
        return render_template(
            "user/error.html",
            error     = "Could not find your unit.",
            prev_page = request.referrer,
            endpoint  = request.endpoint,
        )


    @user_bp.errorhandler(DuplicateKeyError)
    def duplicate_key_error(e):
        return render_template(
            "user/error.html",
            error     = "A user with the same username already exists in the unit.",
            prev_page = request.referrer,
            endpoint  = request.endpoint,
        )


    @user_bp.errorhandler(ValueError)
    def value_error(e):
        return render_template(
            "user/error.html",
            error     = "The user's record in the database is missing required attributes.",
            prev_page = request.referrer,
            endpoint  = request.endpoint,
        )


    @user_bp.route("/error", methods=["GET", "POST"])
    def error():
        error_page = "user/error.html"
        error = request.args.get("error")
        prev_page = request.args.get("prev_page")
        return render_template(error_page, error=error, prev_page=prev_page)


    @user_bp.route("/", methods=["GET"])
    @login_required
    def dashboard():
        return render_template(
            "user/dashboard.html", role=session["role"], user_id=session["user_id"]
        )


    @user_bp.route("/profile", methods=["GET"])
    @login_required
    @required_role("employee")
    def show_profile():
        # TODO change employee_id to user id

        show_profile_page = "user/profile.html"
        employee_id: str = session["user_id"]
        user: User

        # result = _try_get_user(employee_id)
        #
        # if isinstance(result, str):
        #     return render_template(show_profile_page, error=result)
        # result = user_service.get_user_by_id(employee_id)
        #
        # user = result

        user = user_service.get_user_by_id(employee_id)
        return render_template(
            show_profile_page,
            user = user
        )


    @user_bp.route("/<user_id>/change-password", methods=["GET", "POST"])
    @login_required
    @required_role("employee")
    def change_password(user_id: Optional[str] = None):
        change_password_page = "user/change-password.html"
        user_id = session["user_id"]
        user: User
        is_password_changed: bool
        # if entered as employee from the 1st route
        if not user_id:
            return redirect(url_for("user.change_password", user_id = user_id))

        if request.method != "POST":
            return render_template(change_password_page, user_id = user_id)

        # the old password is used for verification
        password_old = request.form.get("password_old")
        password_new = request.form.get("password_new")

        if not password_old or not password_new:
            return render_template(
                change_password_page, user_id=user_id, error="Both fields are required."
            )

        if password_old == password_new:
            return render_template(
                change_password_page,
                user_id=user_id,
                error="Previous password cannot be the same as new password.",
            )

        user = user_service.get_user_by_id(user_id)

        if user.password != password_old:
            return render_template(
                change_password_page,
                user_id=user_id,
                error="Previous password is incorrect.",
            )

        is_password_changed = user_service.change_password(user_id, password_new)

        if is_password_changed is False:
            return render_template(
                change_password_page,
                user_id=user_id,
                error="Could not change password.",
            )

        flash("Password successfully changed!", "success")
        return redirect(url_for("user.change_password", user_id=user_id))


    @user_bp.route("/employee/create", methods=["GET", "POST"])
    @login_required
    @required_role("supervisor")
    def create_employee():
        create_employee_page = "user/create_employee.html"

        if request.method != "POST":
            return render_template(create_employee_page)

        # get the field value or ""
        name: str     = request.form.get("name", "").strip()
        surname: str  = request.form.get("surname", "").strip()
        username: str = request.form.get("username", "").strip()
        password: str = request.form.get("password", "").strip()
        unit_id: str  = session["unit_id"]

        # if any variable had incorrect value
        if not all((name, surname, username, password)):
            return render_template(
                create_employee_page,
                error="All fields are required.",
                name=name,
                surname=surname,
                username=username,
            )

        employee_service.insert_employee(name, surname, username, password, unit_id)

        flash("Employee created successfully.", "success")

        return redirect(url_for("user.create_employee"))

    @user_bp.route("/<user_id>/delete", methods=["GET", "POST"])
    @login_required
    @required_role("supervisor")
    def delete_user(user_id: str):
        delete_user_page = "user/delete_user.html"
        prev_page = request.args.get("prev_page") or request.form.get("prev_page")
        unit_id: Optional[str] = session.get("unit_id")

        if request.method != "POST":
            user = user_service.get_user_by_id(user_id)

            return render_template(
                delete_user_page,
                user_id=user_id,
                user = user,
                prev_page = prev_page
            )

        employee_service.delete_employee_by_id(user_id, unit_id)

        flash("User deleted successfully.")
        return render_template(delete_user_page, user_id=user_id, prev_page=prev_page)


    @user_bp.route("/employees", methods=["GET", "POST"])
    @login_required
    @required_role("supervisor")
    def view_employees():
        # view all employees in unit, can select and delete employee
        view_employees_page       = "user/view_employees.html"
        employees: List[Employee] = []
        unit_id: Optional[str]    = session.get("unit_id")

        if request.method != "POST":
            if unit_id is None:
                return render_template(
                    view_employees_page, error="Unit id has no value."
                )

            employees =  employee_service.get_employees_in_unit(unit_id)

            return render_template(view_employees_page, employees=employees)

        # maybe have user_id to reuse this page
        # if an admin wants to delete a supervisor
        employee_id = request.form.get("employee_id", "").strip()

        if not employee_id:
            return render_template(
                view_employees_page,
                error="This employee does not exist.",
                employees=employees,
            )

        return redirect(url_for("user.view_employees", employees=employees))


    return user_bp
