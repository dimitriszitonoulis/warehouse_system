from __future__ import annotations  # for pyright typechecking

import uuid
from operator import attrgetter
from typing import Optional


class Product:
    id: Optional[str]
    name: str
    quantity: int
    sold_quantity: int
    weight: float
    volume: float
    category: str
    purchase_price: float
    selling_price: float
    manufacturer: str
    unit_gain: float
    unit_id: str

    def __init__(
        self,
        id: Optional[str],
        name: str,
        quantity: int,
        sold_quantity: int,
        weight: float,
        volume: float,
        category: str,
        purchase_price: float,
        selling_price: float,
        manufacturer: str,
        unit_gain: float,
        unit_id: str
    ):
        self.id: Optional[str]     = id if id is not None else str(uuid.uuid4())
        self.name:str              = name
        self.quantity: int         = quantity
        self.sold_quantity: int    = sold_quantity
        self.weight: float         = weight
        self.volume: float         = volume
        self.category: str         = category
        self.purchase_price: float = purchase_price
        self.selling_price: float  = selling_price
        self.manufacturer: str     = manufacturer
        self.unit_gain: float      = unit_gain
        self.unit_id: str          = unit_id


    def __eq__(self, other: Product) -> bool:
        return self.id == other.id

    def __str__(self) -> str:
        return ", ".join(map(str, [
            self.id,
            self.name,
            self.quantity,
            self.sold_quantity,
            self.weight,
            self.volume,
            self.category,
            self.purchase_price,
            self.selling_price,
            self.manufacturer,
            self.unit_gain,
            self.unit_id,
        ]))


    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"Product({attrs})"


    def to_dict(self) -> dict:
        """
        Convert the Product instance into a dictionary.

        Returns:
            dict: A dictionary containing all the product attributes, including:
            - `id`
            - `name`
            - `quantity`
            - `sold_quantity`
            - `weight`
            - `volume`
            - `category`
            - `purchase_price`
            - `selling_price`
            - `manufacturer`
            - `unit_gain`
            - `unit_id`
        """
        return {
            "id":             self.id,
            "name":           self.name,
            "quantity":       self.quantity,
            "sold_quantity":  self.sold_quantity,
            "weight":         self.weight,
            "volume":         self.volume,
            "category":       self.category,
            "purchase_price": self.purchase_price,
            "selling_price":  self.selling_price,
            "manufacturer":   self.manufacturer,
            "unit_gain":      self.unit_gain,
            "unit_id":        self.unit_id,
        }

    @classmethod
    def from_dict(cls, data) -> Product:
        """
        Create a Product instance from a dictionary.

        This method validates that all required attributes are present and non-None.
        Raises an error if any required attribute is missing.

        Args:
            data (dict): Dictionary containing the product attributes.
            The following keys are required:
            - `name`
            - `quantity`
            - `sold_quantity`
            - `weight`
            - `volume`
            - `category`
            - `purchase_price`
            - `selling_price`
            - `manufacturer`
            - `unit_gain`
            - `unit_id`
            The key `id` is optional and may be None.

        Returns:
            Product: A Product instance initialized with the given attributes.

        Raises:
            ValueError: If any required attribute is missing or None.
        """
        # id can be None so dont include it in the attr list
        attributes = [
            "name",
            "quantity",
            "sold_quantity",
            "weight",
            "volume",
            "category",
            "purchase_price",
            "selling_price",
            "manufacturer",
            "unit_gain",
            "unit_id",
        ]

        for attr in attributes:
            if data.get(attr) is None:
                raise ValueError(f"Attribute {attr} cannot be None")

        product = cls(
            id             = data.get("id"),
            name           = data.get("name"),
            quantity       = data.get("quantity"),
            sold_quantity  = data.get("sold_quantity"),
            weight         = data.get("weight"),
            volume         = data.get("volume"),
            category       = data.get("category"),
            purchase_price = data.get("purchase_price"),
            selling_price  = data.get("selling_price"),
            manufacturer   = data.get("manufacturer"),
            unit_gain      = data.get("unit_gain"),
            unit_id        = data.get("unit_id"),
        )

        return product


    def calculate_loss(self, quantity: int) -> float:
        """
        Returns the loss of buing `quantity` items of the product

        Args: 
            quantity (int): The amount of items of the product to buy

        Returns:
            (float): The loss
        """
        return - self.purchase_price * quantity


    def calculate_profit(self, quantity):
        """
        Calculates the profit from selling `quantity` items of the product

        Args:
            quantity (int): The amount f items of the product to sell

        Returns:
            (float): The profit
        """
        return (self.selling_price - self.purchase_price) * quantity


    def sell_product(self, sold_product: int) -> None:
        """
        Sells a product

        Modifies the product parameters according to the amount of items sold
        :param sold_product: The amount of items of a program to sell
        """
        self.sold_quantity = self.sold_quantity + sold_product
        self.quantity      = self.quantity - sold_product
        self.unit_gain     = self.selling_price * sold_product


    @staticmethod
    def sort_name(product_list: list[Product], reverse: bool = False) -> None:
        """
        Sort a list of Product objects in place by their name.

        The list is sorted in ascending order by default. 
        Set `reverse=True` to sort in descending order.

        Args:
            product_list (list[Product]): The list of products to sort.
            reverse (bool, optional): If True, sort in descending order. Defaults to False.
        """
        product_list.sort(key=attrgetter("name"), reverse=reverse)


    @staticmethod
    def sort_sold_quantity(product_list: list[Product], reverse: bool):
        """
        Sort a list of Product objects in place by the quantity of items sold for each product.

        The list is sorted in ascending order by default. 
        Set `reverse=True` to sort in descending order.

        Args:
            product_list (list[Product]): The list of products to sort.
            reverse (bool, optional): If True, sort in descending order. Defaults to False.
        """
        product_list.sort(key=attrgetter("sold_quantity"), reverse=reverse)
