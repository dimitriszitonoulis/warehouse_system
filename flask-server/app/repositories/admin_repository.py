from pymongo.database import Collection
from pymongo.results import InsertOneResult

from app.model.admin import Admin


class AdminRepository:
    user_collection: Collection

    def __init__(self, user_collection: Collection):
        self.user_collection = user_collection

    def get_admin(self, username: str, password: str) -> Admin | None:
        """
        Retrieve an Admin instance from the DB using their credentials.

        Note that `unit_name` is not stored in the DB and it will be set to None.

        Args:
            username (str): The `username` of the admin.
            password (str): The `password` of the admin.
            unit_id (str): The `id` of the unit the admin is assigned to.

        Returns:
            Employee | None:
            - An Admin object if found.
            - None if no admin with the given ID exists.

        Raises:
            ValueError: If the Database record is missing required attributes
            (see User.from_persistence_dict() for details on the required attributes).
        """
        query = {
            "username": username,
            "password": password,
            "role": "admin"
        }
        result = self.user_collection.find_one(query)

        if result is None:
            return None

        return Admin.from_persistence_dict(result)



    def insert_admin(self, admin: Admin) -> InsertOneResult:
        """
        Inserts an admin to the database.

        Args:
            admin (Admin): The admin to insert.

        Returns:
            pymongo.results.InsertOneResult: The result of the insertion.
        """
        return self.user_collection.insert_one(admin.to_percistance_dict())
