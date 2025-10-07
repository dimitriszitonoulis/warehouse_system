import uuid
from typing import Optional


class Unit:
    id: str
    name: str
    volume: float

    def __init__(self, id: Optional[str], name: str, volume: float):
        self.id: str       = id if id is not None else str(uuid.uuid4())
        self.name: str     = name
        self.volume: float = volume


    def __str__(self) -> str:
        return ", ".join(map(str, [
            self.id,
            self.name,
            self.volume
        ]))


    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"Unit({attrs})"


    def to_dict(self) -> dict:
        """
        Convert the Unit object into a full dictionary representation.

        Returns:
            dict[str, Any]: A dictionary containing all attributes of the unit.
        """
        return {
            "id":     self.id,
            "name":   self.name,
            "volume": self.volume
        }


    @classmethod
    def from_dict(cls, data):
        """
        Returns a Unit instance from a dictionary

        This method validates that all required attributes are present and non-None.
        Raises ValueError if any required attribute is missing.

        Args:
            data (dict): Dictionary containing the user attributes.
            The following keys are required:
            - `name`
            - `volume`

        Returns:
            Unit: A Unit instance initialized with the given attributes

        Raises:
            ValueError: If any required attribute is missing or None.
        """
        # id can be None so dont include it in the attr list
        attributes = ["name", "volume"]

        for attr in attributes:
            if data.get(attr) is None:
                raise Exception(f"Attribute {attr} cannot be None")

        unit = cls(
            data.get("id"),
            data.get("name"),
            data.get("volume")
        )

        return unit
