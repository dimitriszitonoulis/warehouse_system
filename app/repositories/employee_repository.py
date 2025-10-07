from typing import List, Optional

from pymongo.database import Collection
from pymongo.results import DeleteResult, InsertManyResult, InsertOneResult

from app.model.employee import Employee

"""
Avoid Singleton pattern, use Dependency Injection
"""
class EmployeeRepository:
    user_collection: Collection

    def __init__(self, employee_collection: Collection) -> None:
        self.user_collection = employee_collection


    def get_employee_by_id(self, id: str) -> Optional[Employee]:
        """
        Get an Employee instance from the DB by ID.

        Args:
            id (str): The ID of the employee to retrieve.

        Returns:
            Employee | None:
            - An Employee object if found.
              Note that `unit_name` is not stored in the database.
            - None if no employee with the given ID exists.

        Raises:
            ValueError: If the Database record is missing required attributes
            (see User.from_persistence_dict() for details on the required attributes).
        """
        query = {"id": id, "role": "employee"}
        result = self.user_collection.find_one(query)

        if result is None:
            return None

        return Employee.from_persistence_dict(result)


    def get_employee(self, username: str, password: str, unit_id: str) -> Optional[Employee]:
        """
        Retrieve an Employee instance from the DB using their credentials.

        Note that `unit_name` is not stored in the DB and it will be set to None.

        Args:
            username (str): The `username` of the employee.
            password (str): The `password` of the employee.
            unit_id (str): The `id` of the unit the employee is assigned to.

        Returns:
            Employee | None:
            - An Employee object if found.
              Note that `unit_name` is not stored in the database.
            - None if no employee with the given credentials exists.

        Raises:
            ValueError: If the Database record is missing required attributes
            (see User.from_persistence_dict() for details on the required attributes).
        """

        query = {
            "username": username,
            "password": password,
            "unit_id":  unit_id,
            "role":     "employee"
        }

        result = self.user_collection.find_one(query)

        if result is None:
            return None

        return Employee.from_persistence_dict(result)


    def get_employees_in_unit(self, unit_id: str) -> List[Employee]:
        """
        Retrieve all the employees inside the unit specified by `unit_id`.

        Note that for each Employee instance the field `unit_name`
        is not stored in the DB and it will be set to None.

        Args:
            unit_id (str): The id of the unit.

        Returns:
            List[Employee]: A list of all the employees in the given unit.
                If no employees are found the list is emply.

        Raises:
            ValueError: If the Database record of any employee
            is missing required attributes
            (see User.from_persistence_dict() for details on the required attributes).
        """

        cursor = self.user_collection.find({"unit_id": unit_id, "role": "employee"})

        if cursor is None:
            return []

        return [Employee.from_persistence_dict(e) for e in cursor]


    def insert_employee(self, employee: Employee) -> InsertOneResult:
        """
        Inserts an employee to the database.

        Removes the field `unit_name` from `employee`,
        since only the `unit_id` is needed.

        Args:
            employee (Employee): The employee to insert.

        Returns:
            pymongo.results.InsertOneResult: The result of the insertion.
        """
        return self.user_collection.insert_one(employee.to_percistance_dict())


    def insert_employees(self, employees: List[Employee]) -> InsertManyResult:
        """
        Inserts employees to the database.

        Removes the field `unit_name` from each employee in `employees`,
        only the `unit_id` is needed.

        Args:
            employees (List[Employee]): A list with the employees to insert.

        Returns:
            pymongo.results.InsertManyResult: The result of the insertion.
        """
        return self.user_collection.insert_many([e.to_percistance_dict() for e in employees])


    def delete_employee_by_id(self, employee_id: str, unit_id: Optional[str] = None) -> DeleteResult:
        """
        Deletes an employee from the Database.

        Args:
            employee_id (str): The id of the employee to delete.
            unit_id (str | None): The id of the unit the employee belongs to.
                If None search all units are searched.

        Returns:
            DeleteResult: The result of the deletion.
        """

        query = {"id": employee_id, "role": "employee"}

        if unit_id is not None:
            query["unit_id"] = unit_id

        return self.user_collection.delete_one(query)

