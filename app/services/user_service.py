from typing import Optional, Union
from app.exceptions.exceptions import UnitNotFoundByIdError, UserNotFoundByCredentialsError, UserNotFoundByIdError
from app.model.employee import Employee
from app.model.supervisor import Supervisor
from app.model.admin import Admin
from app.model.unit import Unit
from app.model.user import User
from app.repositories.unit_repository import UnitRepository
from app.repositories.user_repository import UserRepository
from app.types import UserOrSubclass


class UserService:
    user_repository: UserRepository
    unit_repository: UnitRepository

    def __init__(self, user_repository: UserRepository, unit_repository: UnitRepository) -> None:
        self.user_repository = user_repository
        self.unit_repository = unit_repository


    def get_user_by_id(self, id: str) -> Union[Employee, Supervisor, Admin]:
        """
        Get a User instance from the DB by ID.

        This method:
        1) Retrieves the user record from the repository.
        2) Fetches the unit associated with the user's `unit_id`.
        3) Enriches the user object by setting its `unit_name`.

        Args:
            id (str): The ID of the employee to retrieve.

        Returns:
            UserSubclass: The appropriate subclass of a User object
            with the information of the user identified by `id`.

        Raises:
            UserNotFoundByIdError: If the employee does not exist.
            UnitNotFoundByIdError: If the unit does not exist for the employee's `unit_id`.
            ValueError: If the employee record is missing required attributes
                (see EmployeeRepository.get_employee_by_id()).
        """
        user: Optional[User] = self.user_repository.get_user_by_id(id)

        if user is None:
            raise UserNotFoundByIdError(id)

        unit: Optional[Unit] = self.unit_repository.get_unit_by_id(user.unit_id)

        if unit is None:
            raise UnitNotFoundByIdError(user.unit_id)

        user.unit_name = unit.name

        return self._get_user_subclass(user)


    def get_user(self, username: str, password: str, unit_id: Optional[str] = None) -> Union[Employee, Supervisor, Admin]:
        """
        Get a User instance from the DB by their credentials.

        This method:
        1) Retrieves the user and the user's unit records from the repository.
        2) Enriches the user object by setting its `unit_name`.
        3) Returns the appropriate type of user based on `User.role`.

        Args:
            username (str): The `username` of the user.
            password (str): The `password` of the user.
            unit_id (str | None): The `id` of the unit the user is assigned to.
                If None then the user is not assigned to any unit (ex Admin).

        Returns:
            user (User): A User object with the information
            of the user identified by `id`.

        Raises:
            UserNotFoundByCredentialsError: If the user does not exist.
            UnitNotFoundByIdError: If the unit does not exist.
            ValueError:
                - If the user record is missing required attributes
                (see UserRepository.get_user()).
                - If the user has a role field other than: "admin", "supervisor", "employee".
        """

        user = self.user_repository.get_user(username, password, unit_id)

        if user is None:
            raise UserNotFoundByCredentialsError(username, unit_id)

        if unit_id is not None:
            unit = self.unit_repository.get_unit_by_id(unit_id)

            if unit is None:
                raise UnitNotFoundByIdError(unit_id)

            user.unit_name = unit.name

        return self._get_user_subclass(user)


    def change_password(self, id: str, password: str) -> bool:
        return self.user_repository.change_password(id, password)


    def _get_user_subclass(self, user: User) -> Union[Employee, Supervisor, Admin]:
        """
        Convert base user to subclass based on role field.

        Args:
            user (User): The user to convert.

        Returns:
            UserSubclass: The corresponding subclass of user based on `user.role`.

        Raises:
            ValueError: If the role field has a value other than:
            "admin", "supervisor", "employee".
        """

        match user.role:
            case "admin":
                return Admin.from_user(user)
            case "supervisor":
                return Supervisor.from_user(user)
            case "employee":
                return Employee.from_user(user)
            case _:
                raise ValueError(f"User with id={user.id} has invalid role field.")
