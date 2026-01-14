from __future__ import annotations  # for pyright typechecking

from typing import Optional

from app.model.user import User


class Admin(User):
    role: str = "admin"


    def __init__(
        self,
        id: Optional[str],
        username: str,
        password: str,
    ):
        super().__init__(
            id        = id,
            name      = "",
            surname   = "",
            username  = username,
            password  = password,
            unit_id   = "",
            unit_name = "",
            role      = "admin"
        )


    def __eq__(self, other: Admin) -> bool:
        return self.id == other.id


    def __str__(self) -> str:
        return ", ".join(map(str, [
            self.id,
            self.username,
            self.password
        ]))


    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"Admin({attrs})"


    @classmethod
    def from_user(cls, user: User):
        return cls(
            id       = user.id,
            username = user.username,
            password = user.password
        )
