from typing import Optional


# User exceptions
class UserNotFoundByIdError(Exception):
    """Raised when a user cannot be found by their id."""

    def __init__(self, user_id):
        super().__init__(f"Employee with id={user_id} does not exist.")


class UserNotFoundByCredentialsError(Exception):
    """Raised when a user cannot be found by their credentials."""

    def __init__(self, username: str, unit_id: Optional[str] = None):
        error: str = (
            f"User with username={username} in unit with id={unit_id} was not found."
        )
        if unit_id is not None:
            error = f"User with username={username} was not found."
        super().__init__(error)


# Product exceptions
class ProductNotFoundByIdError(Exception):
    """Raised when a product cannot be found by its id."""

    def __init__(self, product_id):
        super().__init__(f"Product with id={product_id} does not exist.")


class ProductDoesNotFitInUnit(Exception):
    """Raised when the given product does not fit in the given unit."""

    def __init__(self, product_id: str, unit_id: str):
        super().__init__(
            f"Product with id={product_id} does not fit into unit with id={unit_id}"
        )


class InsufficientProductQuantity(Exception):
    """
    Raised when:
        - trying to sell more items than what is available the database.
        - `quantity_to_sell` is negative
    """

    def __init__(self, product_id: str, quantity_to_sell: str):
        super().__init__(
            f"Cannot sell {quantity_to_sell} items of product with id={product_id}."
        )


# Unit exceptions
class UnitNotFoundByIdError(Exception):
    """Raised when a unit cannot be found by its id."""

    def __init__(self, unit_id):
        super().__init__(f"Unit with id={unit_id} does not exist.")
