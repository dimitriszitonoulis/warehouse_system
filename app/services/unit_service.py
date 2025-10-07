from typing import Optional

from pymongo.results import InsertOneResult

from app.exceptions.exceptions import UnitNotFoundByIdError
from app.model.unit import Unit
from app.repositories.unit_repository import UnitRepository


class UnitService:
    unit_repository: UnitRepository


    def __init__(self, unit_repository: UnitRepository):
        self.unit_repository = unit_repository


    def get_unit_by_id(self, unit_id: str) -> Unit:
        """
        Get a Unit instance from the DB by ID.

        Args:
            id (str): The ID of the unit to retrieve.

        Returns:
            unit (Unit): A Unit object with the information
            of the unit identified by `id`.

        Raises:
            UnitNotFoundByIdError: If the unit does not exist.
            ValueError: If the unit record is missing required attributes
                (see UnitRepository.get_unit_by_id()).
        """
        unit = self.unit_repository.get_unit_by_id(unit_id)

        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        return unit


    def insert_unit(self, id: Optional[str], name: str, volume: float) -> InsertOneResult:
        """
        Insert a unit to the database.

        Args:
            id (str): The id of the unit to insert to the database.
            name (str): The name of the unit.
            volume (float): The total volume of the unit.

        Returns:
            InsertOneResult: The result of the insertion.

        Raises:
            ValueError:
            - If the unit record is missing required attributes
            (see UnitRepository.insert_unit()).
        """

        unit = Unit(
            id     = id,
            name   = name,
            volume = volume
        )
        return self.unit_repository.insert_unit(unit)
