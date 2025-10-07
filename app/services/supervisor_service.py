from typing import Optional

from pymongo.results import InsertOneResult

from app.exceptions.exceptions import (
    UnitNotFoundByIdError,
    UserNotFoundByCredentialsError,
    UserNotFoundByIdError,
)
from app.model.supervisor import Supervisor
from app.model.unit import Unit
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.supervisor_repository import SupervisorRepository
from app.repositories.unit_repository import UnitRepository
from app.repositories.user_repository import UserRepository


class SupervisorService:
    user_repository: UserRepository
    employee_repository: EmployeeRepository
    supervisor_repository: SupervisorRepository
    unit_repository: UnitRepository


    def __init__(
        self,
        user_repository: UserRepository,
        employee_repository: EmployeeRepository,
        supervisor_repository: SupervisorRepository,
        unit_repository: UnitRepository,
    ):
        self.user_repository       = user_repository
        self.employee_repository   = employee_repository
        self.supervisor_repository = supervisor_repository
        self.unit_repository       = unit_repository


    def insert_supervisor(
        self,
        name: str,
        surname: str,
        username: str,
        password: str,
        unit_id: str,
    ) -> InsertOneResult:
        """
        Insert a supervisor to the database.

        Args:
            name (str): The name of the supervisor.
            surname (str): The surname of the supervisor.
            username (str): The username of the supervisor.
            password (str): The password of the supervisor.
            unit_id (str): The unit the employee is working on.

        Returns:
            InsertOneResult: The result of the insertion.

        Raises:
            ValueError:
            - If the supervisor record is missing required attributes
            (see SupervisorRepository.insert_supervisor()).
        """
        supervisor = Supervisor(
            id        = None,
            name      = name,
            surname   = surname,
            username  = username,
            password  = password,
            unit_id   = unit_id,
            unit_name = None
        )
        return self.supervisor_repository.insert_supervisor(supervisor)


    def get_supervisor_by_id(self, id: str):
        """
        Get a Supervisor instance from the DB by ID.

        This method:
        1) Retrieves the supervisor record from the repository.
        2) Fetches the unit associated with the supervisor's `unit_id`.
        3) Enriches the supervisor object by setting its `unit_name`.

        Args:
            id (str): The ID of the employee to retrieve.

        Returns:
            supervisor (Supervisor): A Supervisor object with the information
            of the employee identified by `id`.

        Raises:
            UserNotFoundByIdError: If the supervisor does not exist.
            UnitNotFoundByIdError: If the unit does not exist for the supervisor's `unit_id`.
            ValueError: If the employee record is missing required attributes
                (see EmployeeRepository.get_employee_by_id()).
        """
        supervisor: Optional[Supervisor]
        unit: Optional[Unit]
        unit_id: str

        # retrieve Supervisor object
        # unit_name is not saved in DB, it is None
        supervisor = self.supervisor_repository.get_supervisor_by_id(id)

        if supervisor is None:
            raise UserNotFoundByIdError(id)

        unit_id = supervisor.unit_id
        unit    = self.unit_repository.get_unit_by_id(unit_id)

        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        supervisor.unit_name = unit.name

        return supervisor


    def get_employee(self, username: str, password: str, unit_id: str) -> Supervisor:
        """
        Get a Supervisor instance from the DB by their credentials.

        This method:
        1) Retrieves the supervisor and the supervisor's unit records from the repository.
        2) Enriches the supervisor object by setting its `unit_name`.

        Args:
            username (str): The `username` of the supervisor.
            password (str): The `password` of the supervisor.
            unit_id (str): The `id` of the unit the supervisor is assigned to.

        Returns:
            supervisor (Supervisor): A Supervisor object with the information
            of the supervisor identified by `id`.

        Raises:
            UserNotFoundByCredentialsError: If the supervisor does not exist.
            UnitNotFoundByIdError: If the unit does not exist.
            ValueError: If the supervisor record is missing required attributes
                (see Supervisor.get_supervisor()).
        """
        # retrieve Supervisor object
        # unit_name is not saved in DB, it is None
        supervisor = self.supervisor_repository.get_supervisor(username, password, unit_id)
        unit     = self.unit_repository.get_unit_by_id(unit_id)

        if supervisor is None:
            raise UserNotFoundByCredentialsError(username, unit_id)
        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        supervisor.unit_name = unit.name

        return supervisor
