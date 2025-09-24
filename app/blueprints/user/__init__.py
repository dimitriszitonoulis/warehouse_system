from typing import List, Optional, Union
from flask import Blueprint, redirect, request, session, render_template, flash, url_for
from pymongo.errors import DuplicateKeyError
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


def create_user_blueprint(
    user_service: UserService,
    employee_service: EmployeeService
    ):
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


    def _try_insert_employee(
        name: str,
        surname: str,
        username: str,
        password: str,
        unit_id: str
    ) -> Optional[str]:
        error: Optional[str] = None
        try:
            insert_result = employee_service.insert_employee(
                name, surname, username, password, unit_id
            )
        except UnitNotFoundByIdError:
            error="Could not find your unit."
        except DuplicateKeyError:
            error="A user with the same username already exists in the unit."
        except ValueError:
            error="The user's record in the database is missing required attributes."
        return error


    def _try_delete_employee(employee_id: str, unit_id: Optional[str]):
        error: Optional[str] = None
        try:
            employee_service.delete_employee_by_id(employee_id, unit_id)
        except UnitNotFoundByIdError:
            error="Could not find your unit."
        except UserNotFoundByIdError:
            error = "Could not find employee."

        return error


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

        error = _try_insert_employee(name, surname, username, password, unit_id)

        if error is not None:
            return render_template(
                create_employee_page,
                error=error,
                name=name,
                surname=surname,
                username=username,
            )

        flash("Employee created successfully.", "success")

        return redirect(url_for("user.create_employee"))


    @user_bp.route("/employees", methods=["GET", "POST"])
    @login_required
    @required_role("supervisor")
    def view_employees():
        # view all employees in unit, can select and delete employee
        view_employees_page       = "user/view_employees.html"
        employees: List[Employee] = []
        unit_id: Optional[str]    = session.get("unit_id")
        error: Optional[str]      = None

        if unit_id is not None:
            employees = employee_service.get_employees_in_unit(unit_id)

        if request.method != "POST":
            return render_template(view_employees_page, employees=employees)

        employee_id = request.form.get("employee_id", "").strip()

        if not employee_id:
            return render_template(
                view_employees_page,
                error="This employee does not exist.",
                employees=employees,
            )

        error = _try_delete_employee(employee_id, unit_id)

        if error is not None:
            return render_template(
                view_employees_page, error=error, employees=employees
            )

        return redirect(url_for("user.view_employees"))


    return user_bp
