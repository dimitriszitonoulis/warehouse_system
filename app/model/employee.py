from __future__ import annotations  # for pyright typechecking

from typing import Optional

from app.model.user import User


class Employee(User):
    role: str = "employee"

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
            # for when creating a supervisor
            role      = role if role is not  None else "employee"
        )


    def __eq__(self, other: Employee) -> bool:
        return self.id == other.id


    def __str__(self) -> str:
        return ", ".join(map(str, [
            self.id,
            self.name,
            self.surname,
            self.username,
            self.password,
            self.unit_id,
            self.unit_name,
        ]))


    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"Employee({attrs})"


    def change_password(self, new_password: str) -> bool:
        if self.password == new_password:
            return False
        self.password = new_password
        return True
