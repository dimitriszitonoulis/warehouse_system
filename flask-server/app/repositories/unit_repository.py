from typing import List

from pymongo.database import Collection
from pymongo.results import InsertManyResult, InsertOneResult

from app.model.unit import Unit

"""
Avoid Singleton pattern, use Dependency Injection
"""
class UnitRepository:
    unit_collection: Collection

    def __init__(self, unit_collection: Collection):
        self.unit_collection = unit_collection


    def get_all_units(self) -> List[Unit]:
        """
        Get all the stored units
        """
        result = self.unit_collection.find()
        return [Unit.from_dict(unit) for unit in result]


    def get_all_units_ids(self) -> List[str]:
        """
        Get the ids of all the stored units

        Returns:
            List[str]: The ids of all the stored units.
        """
        cursor = self.unit_collection.find({}, projection={"id": 1, "_id": 0})
        # instead of returning a list like: [{id: 1}, {id: 2}...], return [1, 2, ...]
        return [unit.get("id") for unit in cursor if "id" in unit]


    def get_unit_by_id(self, id: str) -> Unit | None:
        """
        Get a User instance from the DB by ID.

        Args:
            id (str): The ID of the unit to retrieve.

        Returns:
            Unit | None:
            - A Unit object if found.
            - None if no unit with the given ID exists.

        Raises:
            ValueError: If the Database record is missing required attributes
            (see Unit.from_persistence_dict() for details on the required attributes).
        """

        result = self.unit_collection.find_one({"id": id})

        if result is None:
            return None

        return Unit.from_dict(result)


    def insert_unit(self, unit: Unit) -> InsertOneResult:
        """
        Inserts a unit to the database

        Args:
            unit (Unit): The unit to insert.

        Returns:
            pymongo.results.InsertOneResult: The result of the insertion.
        """
        return self.unit_collection.insert_one(unit.to_dict())


    def insert_units(self, units: List[Unit]) -> InsertManyResult:
        """
        Inserts a units to the database

        Args:
            units (List[Unit]): A list with the units to insert

        Returns:
            pymongo.results.InsertManyResult: The result of the insertion
        """
        return self.unit_collection.insert_many([u.to_dict() for u in units])
