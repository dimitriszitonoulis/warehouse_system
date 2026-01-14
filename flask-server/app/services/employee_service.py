from typing import List, Optional

from pymongo.results import InsertOneResult

from app.exceptions.exceptions import (
    UnitNotFoundByIdError,
    UserNotFoundByCredentialsError,
    UserNotFoundByIdError,
)
from app.model.employee import Employee
from app.model.unit import Unit
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.unit_repository import UnitRepository
from app.repositories.user_repository import UserRepository


class EmployeeService():
    user_repository: UserRepository
    employee_repository: EmployeeRepository
    unit_repository: UnitRepository

    def __init__(
        self,
        user_repository: UserRepository,
        employee_repository: EmployeeRepository,
        unit_repo: UnitRepository,
    ):
        self.user_repository     = user_repository
        self.employee_repository = employee_repository
        self.unit_repository     = unit_repo


    def insert_employee(
        self,
        name: str,
        surname: str,
        username: str,
        password: str,
        unit_id: str,
    ) -> InsertOneResult:
        """
        Insert an employee to the database.

        Args:
            name (str): The name of the employee.
            surname (str): The surname of the employee.
            username (str): The username of the employee.
            password (str): The password of the employee.
            unit_id (str): The unit the employee is working on.

        Returns:
            InsertOneResult: The result of the insertion.

        Raises:
            DuplicateKeyError: If an employee with the same username
                already exists in the unit (the pair username unit_id must be unique).
            UnitNotFoundByIdError: If no unit with the given `unit_id` exists.
        """

        unit: Optional[Unit] = self.unit_repository.get_unit_by_id(unit_id)

        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        employee = Employee(
            id        = None,
            name      = name,
            surname   = surname,
            username  = username,
            password  = password,
            unit_id   = unit_id,
            unit_name = None
        )
        return self.employee_repository.insert_employee(employee)

    def get_employee_by_id(self, id: str) -> Employee:
        """
        Get an Employee instance from the DB by ID.

        This method:
        1) Retrieves the employee record from the repository.
        2) Fetches the unit associated with the employee's `unit_id`.
        3) Enriches the employee object by setting its `unit_name`.

        Args:
            id (str): The ID of the employee to retrieve.

        Returns:
            employee (Employee): An Employee object with the information
            of the employee identified by `id`.

        Raises:
            UserNotFoundByIdError: If the employee does not exist.
            UnitNotFoundByIdError: If the unit does not exist
            for the employee's `unit_id`.
            ValueError: If the employee record is missing required attributes
                (see EmployeeRepository.get_employee_by_id()).
        """
        employee: Optional[Employee]
        unit: Optional[Unit]
        unit_id: str

        # retrieve Employee object
        # unit_name is not saved in DB, it is None
        employee = self.employee_repository.get_employee_by_id(id)

        if employee is None:
            raise UserNotFoundByIdError(id)

        unit_id = employee.unit_id
        unit    = self.unit_repository.get_unit_by_id(unit_id)

        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        employee.unit_name = unit.name

        return employee


    def get_employee(self, username: str, password: str, unit_id: str) -> Employee:
        """
        Get an Employee instance from the DB by their credentials.

        This method:
        1) Retrieves the employee and the employee's unit records from the repository.
        2) Enriches the employee object by setting its `unit_name`.

        Args:
            username (str): The `username` of the employee.
            password (str): The `password` of the employee.
            unit_id (str): The `id` of the unit the employee is assigned to.

        Returns:
            employee (Employee): An Employee object with the information
            of the employee identified by `id`.

        Raises:
            UserNotFoundByCredentialsError: If the employee does not exist.
            UnitNotFoundByIdError: If the unit does not exist.
            ValueError: If the employee record is missing required attributes
                (see EmployeeRepository.get_employee()).
        """
        # retrieve Employee object
        # unit_name is not saved in DB, it is None
        employee = self.employee_repository.get_employee(username, password, unit_id)
        unit     = self.unit_repository.get_unit_by_id(unit_id)

        if employee is None:
            raise UserNotFoundByCredentialsError(username, unit_id)
        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        employee.unit_name = unit.name

        return employee


    def get_employees_in_unit(self, unit_id: str) -> List[Employee]:
        """
        Returns all the employees inside the unit specified by `unit_id`

        Args:
            unit_id (str): The id of the unit.

        Returns:
            employees (List[Employee]): A list of all the employees
                in the given unit.

        Raises:
            UnitNotFoundByIdError: If the unit does not exist.
            ValueError: If the employee record is missing required attributes
                (see EmployeeRepository.get_employees()).
        """

        unit = self.unit_repository.get_unit_by_id(unit_id)

        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        employees = self.employee_repository.get_employees_in_unit(unit_id)

        # the unit_name is not saved in the db for each employee
        for employee in employees:
            employee.unit_name = unit.name

        return employees


    def delete_employee_by_id(
        self, employee_id: str, unit_id: Optional[str] = None
    ) -> None:
        """
        Deletes an employee from the Database.

        Args:
            employee_id (str): The id of the employee to delete.
            unit_id (str | None): The id of the unit the employee belongs to.
                If None search all units are searched.

        Returns:
            DeleteResult: The result of the deletion.

        Raises:
            UserNotFoundByIdError: If the employee does not exist.
            UnitNotFoundByIdError: If the unit does not exist.
        """

        unit: Optional[Unit]

        if unit_id is not None:
            unit = self.unit_repository.get_unit_by_id(unit_id)

            if unit is None:
                raise UnitNotFoundByIdError(unit_id)

        result = self.employee_repository.delete_employee_by_id(employee_id, unit_id)

        if not result.acknowledged:
            raise UserNotFoundByIdError(employee_id)
