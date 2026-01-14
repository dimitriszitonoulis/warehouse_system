from functools import wraps

from flask import redirect, session, url_for

from app.blueprints.names import AUTH_BP


def login_required(f):
    """
    Decorator to ensure that a user is logged in.

    If the user is not logged in, they are redirected
    to the login page.

    Usage:
        @login_required
        def some_route():
            ...
    """
    @wraps(f)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for(f"{AUTH_BP}.login"))
        return f(**kwargs)

    return wrapped_view


def required_role(min_role: str):
    """
    Checks if a user has the required role

    Hierarchy: 'employee' < 'supervisor' < 'admin'.
    A user whose role is later in the hierarchy has access
    to all resources of the previous roles.


    If the user is not logged in, redirects to the login page.
    If the user does not have sufficient role, redirects to
    missing permissions page.

    Args:
        min_role: The minimum role to access a resource.

    Usage:
    Deny a resource from employees but allow supervisors and admins:
        @required_role("supervisor")
        def some_route():


    """
    def decorator(f):
        @wraps(f)
        def wrapped(**kwargs):

            hierarchy = ["employee", "supervisor", "admin"]
            user_role = session.get("role")

            if not isinstance(user_role, str):
                return redirect(url_for(f"{AUTH_BP}.login"))

            if hierarchy.index(user_role) < hierarchy.index(min_role):
                return redirect(url_for(f"{AUTH_BP}.missing_permissions"))

            return f(**kwargs)
        return wrapped
    return decorator


def is_admin_logged_in() -> bool:
    # Maybe if role not in sessio nredirect to login page
    if "role" in session:
        if session["role"] == "admin":
            return True
    return False
