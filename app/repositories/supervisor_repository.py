from typing import List, Optional

from pymongo.database import Collection
from pymongo.results import InsertManyResult, InsertOneResult

from app.model.supervisor import Supervisor


class SupervisorRepository:
    user_collection: Collection


    def __init__(self, user_collection: Collection) -> None:
        self.user_collection = user_collection

    def get_supervisor_by_id(self, id: str) -> Optional[Supervisor]:
        """
        Get a Supervisor instance from the DB by ID.

        Args:
            id (str): The ID of the supervisor to retrieve.

        Returns:
            Supervisor | None:
            - A Supervisor object if found. Note that `unit_name` is not stored in the database.
            - None if no supervisor with the given ID exists.

        Raises:
            ValueError: If the Database record is missing required attributes
            (see User.from_persistence_dict() for details on the required attributes).
        """
        query = {"id": id, "role": "supervisor"}
        result = self.user_collection.find_one(query)

        if result is None:
            return None

        return Supervisor.from_persistence_dict(result)


    def get_supervisor(self, username: str, password: str, unit_id: str):
        """
        Retrieve a Supervisor instance from the DB using their credentials.

        Note that `unit_name` is not stored in the DB and it will be set to None.

        Args:
            username (str): The `username` of the supervisor.
            password (str): The `password` of the supervisor.
            unit_id (str): The `id` of the unit the supervisor is assigned to.

        Returns:
            Supervisor | None:
            - A Supervisor object if found.
              Note that `unit_name` is not stored in the database.
            - None if no supervisor with the given ID exists.

        Raises:
            ValueError: If the Database record is missing required attributes
            (see User.from_persistence_dict() for details on the required attributes).
        """

        query = {
            "username": username,
            "password": password,
            "unit_id":  unit_id,
            "role":     "supervisor"
        }

        result = self.user_collection.find_one(query)

        if result is None:
            return None

        return Supervisor.from_persistence_dict(result)


    def insert_supervisor(self, supervisor: Supervisor) -> InsertOneResult:
        """
        Inserts supervisor to the database.

        Removes the field `unit_name` from `supervisor`,
        since only the `unit_id` is needed.

        Args:
            supervisor (Supervisor): The supervisor to insert.

        Returns:
            pymongo.results.InsertOneResult: The result of the insertion.
        """
        return self.user_collection.insert_one(supervisor.to_percistance_dict())


    def insert_supervisors(self, supervisors: List[Supervisor]) -> InsertManyResult:
        """
        Inserts supervisors to the database.

        Removes the field `unit_name` from each supervisor in `supervisors`,
        only the `unit_id` is needed.

        Args:
            supervisors (List[Supervisor]): A list with the supervisors to insert.

        Returns:
            pymongo.results.InsertManyResult: The result of the insertion.
        """
        return self.user_collection.insert_many([s.to_percistance_dict() for s in supervisors])
