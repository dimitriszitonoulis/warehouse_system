from typing import TypeVar

UserOrSubclass = TypeVar("UserOrSubclass", bound="User")
UserSubclass = TypeVar("UserSubclass", bound="User", covariant=True)
# UserSubclass = Admin | Supervisor | Employee
