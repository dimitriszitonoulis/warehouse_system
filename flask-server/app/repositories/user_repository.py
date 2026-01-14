from typing import Optional

from pymongo.database import Collection

from app.model.user import User


class UserRepository:
    user_collection: Collection


    def __init__(self, user_collection: Collection) -> None:
        self.user_collection = user_collection


    def get_user_by_id(self, id: str) -> User | None:
        """
        Get a User instance from the DB by ID.

        Args:
            id (str): The ID of the user to retrieve.

        Returns:
            User | None:
            - A User object if found. Note that `unit_name` is not stored in the database.
            - None if no user with the given ID exists.

        Raises:
            ValueError: If the Database record is missing required attributes
            (see User.from_persistence_dict() for details on the required attributes).
        """
        result = self.user_collection.find_one({"id": id})

        if result is None:
            return None

        return User.from_persistence_dict(result)


    def get_user(self, username: str, password: str, unit_id: Optional[str]) -> User | None:
        """
        Retrieve a User instance from the DB using their credentials.

        Note that `unit_name` is not stored in the DB and it will be set to None.

        Args:
            username (str): The `username` of the employee.
            password (str): The `password` of the employee.
            unit_id (str | None): The `id` of the unit the employee is assigned to.
                If None then the user is not assigned to any unit (ex Admin).

        Returns:
            User | None:
            - A User object if found. Note that `unit_name` is not stored in the database.
            - None if no employee with the given ID exists.

        Raises:
            ValueError: If the Database record is missing required attributes
            (see User.from_persistence_dict() for details on the required attributes).
        """
        query = {
            "username": username,
            "password": password,
        }

        if unit_id is not None:
            query["unit_id"] = unit_id

        result = self.user_collection.find_one(query)

        if result is None:
            return None

        return User.from_persistence_dict(result)


    def change_password(self, id: str, password: str) -> bool:
        """
        Changes the password of the user identified by `id`.

        Args:
            id (str): The id of the user whose password is going to change.
            password (str): The new password.

        Returns:
            bool: True if the password is changed false otherwise
        """
        result = self.user_collection.find_one_and_update(
            {"id": id},
            {"$set": {"password": password}},
            upsert = False
        )

        return result is not None
