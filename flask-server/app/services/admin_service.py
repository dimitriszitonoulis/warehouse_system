from pymongo.results import InsertOneResult

from app.model.admin import Admin
from app.repositories.admin_repository import AdminRepository


class AdminService:
    admin_repository: AdminRepository


    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository


    def insert_admin(
        self,
        username: str,
        password: str,
    ) -> InsertOneResult:
        """
        Insert an employee to the database.

        Args:
            username (str): The username of the employee.
            password (str): The password of the employee.

        Returns:
            InsertOneResult: The result of the insertion.

        Raises:
            DuplicateKeyError: If an admin with the same username
                already exists.
                There is an index for (username, unit_id) and all Admins
                have the same unit_id="". As a result, all admin usernames
                must be unique.
            ValueError: If the admin record is missing required attributes
            (see AdminRepository.insert_employee()).
        """


        admin = Admin(
            id        = None,
            username  = username,
            password  = password,
        )

        return self.admin_repository.insert_admin(admin)
