from __future__ import annotations  # for pyright typechecking

import uuid
from typing import Any, Dict, List, Optional, Type

from app.types import UserOrSubclass


class User:
    id: str                  = ""
    name: str                = ""
    surname: str             = ""
    username: str            = ""
    password: str            = ""
    unit_id: str             = ""
    unit_name: Optional[str] = None
    role: str                = ""


    def __init__(
        self,
        id: Optional[str],
        name: str,
        surname: str,
        username: str,
        password: str,
        unit_id: str,
        unit_name: Optional[str],
        role: str
    ):
        self.id        = id if id is not None else str(uuid.uuid4())
        self.name      = name
        self.surname   = surname
        self.username  = username
        self.password  = password
        self.unit_id   = unit_id
        self.unit_name = unit_name
        self.role      = role


    def to_dict(self) -> dict[str, Any]:
        """
        Convert the User object into a full dictionary representation.

        Returns:
            dict[str, Any]: A dictionary containing all attributes of the user.
        """
        return {
            "id":        self.id,
            "name":      self.name,
            "surname":   self.surname,
            "username":  self.username,
            "password":  self.password,
            "unit_id":   self.unit_id,
            "unit_name": self.unit_name,
            "role":      self.role
        }


    def to_percistance_dict(self) -> dict[str, Any]:
        """
        Convert the User object into a dictionary suitable for persistence.

        This excludes fields that should not be stored in the database, such as 
        `unit_name`, which can be derived later by querying the unit collection.

        Returns:
            dict[str, Any]: A dictionary containing only the fields to persist in the database.
        """
        emp_dict = self.to_dict()
        emp_dict.pop("unit_name", None)
        return emp_dict


    @classmethod
    def from_user(cls, user: User):
        return cls(
            id        = user.id,
            name      = user.name,
            surname   = user.surname,
            username  = user.username,
            password  = user.password,
            unit_id   = user.unit_id,
            unit_name = user.unit_name,
            role      = user.role
        )


    @classmethod
    def from_dict(cls: Type[UserOrSubclass], data: Dict[str, Any]) -> UserOrSubclass:
        """
        Returns a User instance from a dictionary


        Use this method to create an User object where `unit_name` is allowed to be missing.

        This method validates that all required attributes are present and non-None.
        Raises ValueError if any required attribute is missing.

        Args:
            data (dict): Dictionary containing the user attributes.
            The following keys are required:
            - `name`
            - `surname`
            - `username`
            - `password`
            - `unit_id`
            - `unit_name`

        Returns:
            User: A User instance initialized with the given attributes

        Raises:
            ValueError: If any required attribute is missing or None.
        """
        # id can be None so dont include it in the attr list
        required_attrs = ["name", "surname", "username", "password", "unit_id", "unit_name"]
        return cls._from_dict(data, required_attrs)


    @classmethod
    def from_persistence_dict(cls: Type[UserOrSubclass], data: Dict[str, Any]):
        """
        Returns an User instance from a dictionary.

        Use this method to create an User object from a DB document 
        where `unit_name` is allowed to be missing.

        This method validates that all required attributes are present and non-None.
        Raises ValueError if any required attribute is missing.

        Args:
            data (dict): Dictionary containing the user attributes.
            The following keys are required:
            - `name`
            - `surname`
            - `username`
            - `password`
            - `unit_id`

        Returns:
            User: An User instance initialized with the given attributes

        Raises:
            ValueError: If any required attribute is missing or None.
        """
        required_attrs = ["name", "surname", "username", "password", "unit_id"]
        return cls._from_dict(data, required_attrs)


    @classmethod
    def _from_dict(cls: Type[UserOrSubclass], data: dict[str, Any], required_attrs: List[str]) -> UserOrSubclass:
        """
        Returns an User instance from a dictionary

        Validates that all required attributes are present and non-None.
        Raises ValueError if any required attribute is missing.

        Args:
            data (dict): Dictionary containing the user attributes.
            require_attrs (List[str]): A list containing the names of all the required attributes.

        Returns:
            User: An User instance initialized with the given attributes

        Raises:
            ValueError: If any required attribute is missing or None.
        """
        for attr in required_attrs:
            if data.get(attr) is None:
                raise ValueError(f"Attribute {attr} cannot be None")

        user = cls(
            id        = data.get("id"),
            name      = str(data["name"]),
            surname   = str(data["surname"]),
            username  = str(data["username"]),
            password  = str(data["password"]),
            unit_id   = str(data["unit_id"]),
            unit_name = data.get("unit_name"),
            role      = data.get("role")
        )
        return user
