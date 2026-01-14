from __future__ import annotations  # for pyright typechecking

from typing import Optional

from app.model.employee import Employee


class Supervisor(Employee):
    role: str = "supervisor"


    def __init__(
        self,
        id: Optional[str],
        name: str,
        surname: str,
        username: str,
        password: str,
        unit_id: str,
        unit_name: Optional[str],
        role: Optional[str] = None
    ):
        super().__init__(
            id        = id,
            name      = name,
            surname   = surname,
            username  = username,
            password  = password,
            unit_id   = unit_id,
            unit_name = unit_name,
            role      = "supervisor"
        )


    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"Supervisor({attrs})"


    # it is not specified if the supervisor should also assign a username
    def create_employee(self, name: str, surname: str, username: str, password: str) -> Employee:
        employee = Employee(
            id        = None,
            name      = name,
            surname   = surname,
            username  = username,
            password  = password,
            unit_id   = self.unit_id,
            unit_name = self.unit_name,
        )
        return employee
