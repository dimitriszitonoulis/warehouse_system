from typing import List, Optional

from pymongo.results import InsertManyResult, InsertOneResult

from app.exceptions.exceptions import (
    InsufficientProductQuantity,
    ProductDoesNotFitInUnit,
    ProductNotFoundByIdError,
    UnitNotFoundByIdError,
)
from app.model.product import Product
from app.model.unit import Unit
from app.repositories.product_repository import ProductRepository
from app.repositories.unit_repository import UnitRepository


class ProductService:
    product_repository: ProductRepository
    unit_repository: UnitRepository

    def __init__(self, product_repository: ProductRepository, unit_repository: UnitRepository):
        self.product_repository = product_repository
        self.unit_repository = unit_repository


    def get_product_by_id(self, id: str, unit_id: Optional[str] = None) -> Product:
        """
        Get a Product instance from the DB by ID.

        Search the unit identified by `unit_id` for the product
        identified by `product_id`.

        Args:
            id (str): The ID of the product to retrieve.
            unit_id (str | None): The ID of the unit where the product is stored.
                If `unit_id` is None search all units.

        Returns:
            product (Product): A Product object with the information
            of the product identified by `product_id`.

        Raises:
            UnitNotFoundByIdError: If `unit_id` is specified and no unit exists
                with that ID.
            ProductNotFoundByIdError: If the product does not exist.
            ValueError: If the product record is missing required attributes
                (see ProductRepository.get_product_by_id()).
        """
        product: Optional[Product]

        if unit_id is None:
            product = self.product_repository.get_product_by_id(id)
        else:
            if self.unit_repository.get_unit_by_id(unit_id) is None:
                raise UnitNotFoundByIdError(unit_id)
            product = self.product_repository.get_product_by_id(id, unit_id)

        if product is None:
            raise ProductNotFoundByIdError(id)

        return product


    def get_products(self) -> List[Product]:
        """
        Get all the products in the database.

        Returns:
            List[Product]: A list of Product instances of all the products inside the database.

        Raises:
            ValueError: If the product record is missing required attributes
                (see ProductRepository.from_dict()).
        """
        return self.product_repository.get_products()


    def get_products_from_unit(self, unit_id: str) -> List[Product]:
        """
        Get all the products inside the unit identified by `unit_id`.

        Args:
            unit_id (str): The id of the unit from which to get the products from.

        Returns:
            List[Product]: A list of Product instances of all the products inside the unit
                identified by `unit_id`.

        Raises:
            UnitNotFoundByIdError: If the unit does not exist.
            ValueError: If the product record is missing required attributes
                (see ProductRepository.get_products_from_unit()).
        """

        unit: Optional[Unit] = self.unit_repository.get_unit_by_id(unit_id)

        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        return self.product_repository.get_products_from_unit(unit_id)


    def _insert_product_to_unit(
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
    ) -> InsertOneResult:
        """
        Insert a product into a specific unit.

        Creates a Product instance and inserts it into the product collection 
        for the unit identified by `unit_id`.

        Args:
            id (str | None): The product ID. Can be None if not yet assigned.
            name (str): The name of the product.
            quantity (int): The number of items of the product to insert in the unit.
            sold_quantity (int): The number of items of the product sold from the unit.
            weight (float): The weight of one item of the product.
            volume (float): The volume of one item of the product.
            category (str): The category of the product (e.g., "Electronics", "Clothing").
            purchase_price (float): The cost price of one item of the product.
            selling_price (float): The selling price of one item of the product.
            manufacturer (str): The product manufacturer.
            unit_gain (float): The total gain or loss of the product in this unit.
            unit_id (str): The ID of the unit where the product will be inserted.

        Returns:
            pymongo.results.InsertOneResult: The result of the database insertion.

        Raises:
            UnitNotFoundByIdError: If no unit with the given `unit_id` exists.
            ValueError: If any of the neccesary Product fields are missing when creating a Product instance
              from a dictionary
        """
        product: Product
        unit: Optional[Unit]

        unit = self.unit_repository.get_unit_by_id(unit_id)

        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        try:
            product = Product.from_dict(
                {
                    "id":             id,
                    "name":           name,
                    "quantity":       int(quantity),
                    "sold_quantity":  int(sold_quantity),
                    "weight":         float(weight),
                    "volume":         float(volume),
                    "category":       category,
                    "purchase_price": float(purchase_price),
                    "selling_price":  float(selling_price),
                    "manufacturer":   manufacturer,
                    "unit_gain":      float(unit_gain),
                    "unit_id":        unit_id,
                }
            )
        except Exception as e:
            raise ValueError("Invalid product format") from e

        result = self.product_repository.insert_product(product)

        return result


    def _insert_product_to_all_units(
        self,
        id: Optional[str],
        name: str,
        weight: float,
        volume: float,
        category: str,
        purchase_price: float,
        selling_price: float,
        manufacturer: str,
    ) -> InsertManyResult:
        """
        Insert a new product into all units.

        This method creates a Product with default values for quantity, sold_quantity,
        and unit_gain (all set to 0), then inserts it into the product collection for
        each unit in the system. A separate document is created for each unit.

        Args:
            id (str | None): The product ID. Can be None if not yet assigned.
            name (str): The name of the product.
            weight (float): The weight of one item of the product.
            volume (float): The volume of one item of the product.
            category (str): The category of the product (e.g., "Electronics", "Clothing").
            purchase_price (float): The cost price of one item of the product.
            selling_price (float): The selling price of one item of the product.
            manufacturer (str): The product manufacturer.

        Returns:
            List[pymongo.results.InsertOneResult]: A list of insertion results, one for each unit.

        Raises:
            ValueError: If any of the neccesary Product fields are missing when creating a Product instance
            from a dictionary
        """

        product: Product
        result: InsertManyResult

        prod_dict = {
            "id": id,
            "name": name,
            "quantity": 0,
            "sold_quantity": 0,
            "weight": weight,
            "volume": volume,
            "category": category,
            "purchase_price": purchase_price,
            "selling_price": selling_price,
            "manufacturer": manufacturer,
            "unit_gain": 0,
        }

        # get all units and unit ids
        unit_ids = self.unit_repository.get_all_units_ids()

        insert_list = []

        for unit_id in unit_ids:
            prod_dict_copy = dict(prod_dict)
            prod_dict_copy["unit_id"] = unit_id
            try:
                product = Product.from_dict(prod_dict_copy)
            except Exception as e:
                raise ValueError("Invalid product format") from e
            insert_list.append(product)
        # insert a product to each unit by inserting it multiple times
        # but with different unit_id each time
        result = self.product_repository.insert_products(insert_list)

        return result


    def _does_product_fit_in_unit(self, unit_id: str, product_quantity: int, product_volume: float) -> bool:
        """
        Checks if a product can fit in the unit that is associated by `unit_id`

        This method gets the total volume of the unit associated by `unit_id`.
        It then gets information about how much storage each product of the unit takes up
        and subtracts it from the total volume.
        If the remainder is enough to store the product with `product_quantity` and `product_volume`
        the product can be placed inside the unit.

        Args:
        unit_id (str): The ID of the unit to check if a product fits in it
        product_quantity (int): The number of items of the product to insert in the unit.
        product_volume (float): The volume of one item of the product to insert to the unit.

        Returns:
            bool: True if there is space in the unit for the product, False otherwise

        Raises:
            UnitNotFoundByIdError: If no unit with the given `unit_id` exists.
        """
        free_space: float
        used_space: float
        unit: Optional[Unit] = self.unit_repository.get_unit_by_id(unit_id)

        # no unit with unit_id was found
        if unit is None:
            raise UnitNotFoundByIdError(unit_id)

        # get storage information for all the products in the unit
        products = self.product_repository.get_quantity_and_volume_by_unit(unit_id)

        used_space = sum(p["quantity"] * p["volume"] for p in products)
        free_space = float(unit.volume) - used_space

        return free_space >= product_quantity * product_volume


    def insert_product(
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
        unit_id: str | None = None,
    ) -> InsertOneResult | InsertManyResult:
        """
        Inserts a product to the database

        The product defined by the method's arguments is added to the unit identified by `unit_id`,
        if `unit_id` is not None. If `unit_id` is None then the product is added to all units

        Args:
            id (str | None): The product ID. Can be None if not yet assigned.
            name (str): The name of the product.
            quantity (int): The number of items of the product to insert in the unit.
            sold_quantity (int): The number of items of the product sold from the unit.
            weight (float): The weight of one item of the product.
            volume (float): The volume of one item of the product.
            category (str): The category of the product (e.g., "Electronics", "Clothing").
            purchase_price (float): The cost price of one item of the product.
            selling_price (float): The selling price of one item of the product.
            manufacturer (str): The product manufacturer.
            unit_gain (float): The total gain or loss of the product in this unit.
            unit_id (str | None): The ID of the unit where the product will be inserted.
            If `unit_id` is None then the product is added to all the units

        Returns:
            pymongo.results.InsertOneResult: If inserting to a single unit.
            pymongo.results.InsertManyResult: If inserting to all units.

        Raises:
            ValueError: 
                - If the `unit_id` is specified but no unit is found with that ID
                - If there is not enough space in the unit with `unit_id` to fit the product
        """

        if unit_id is not None:
            if not self._does_product_fit_in_unit(unit_id, int(quantity), float(volume)):
                raise ValueError(f"Product with id={id} does not fit in unit")

            result = self._insert_product_to_unit(
                id,
                name,
                quantity,
                sold_quantity,
                weight,
                volume,
                category,
                purchase_price,
                selling_price,
                manufacturer,
                unit_gain,
                unit_id,
            )
            return result

        result = self._insert_product_to_all_units(
            id,
            name,
            weight,
            volume,
            category,
            purchase_price,
            selling_price,
            manufacturer,
        )
        return result

#####################################################################################################
# Search and sort

    def search_products(
        self,
        order_field: Optional[str],
        order_type: Optional[str],
        name: Optional[str],
        id: Optional[str],
        min_quantity: Optional[int],
        max_quantity: Optional[int],
        unit_id: Optional[str]
    ) -> List[Product]:
        """
        Search the database and order results.

        This method can search for products based on `name`, `id`,
        or quantity range ([`min_quantity`, `max_quantity`]).

        It can also order the found products based on `order_field`.

        Args:
            order_field (str | None): The field by which to order.
            order_type (str | None): The order type, ascending or descending.
            name (str | None): The name of the product to search.
            id (str | None): The id of the product to search.
            min_quantity (int | None): The minimum product quantity in the database.
            max_quantity (int | None): The maximum product quantity in the database.
            unit_id (str | None): The id of the unit to search. If None all units are searched.

        Returns:
            List[Product]: List of products that match the search query, sorted if requested.

        Raises:
            ValueError: If min_quantity or max_quantity are negative or if min_quantity > max_quantity.
        """

        if min_quantity is not None and max_quantity is not None:
            # are indexes valid?
            if (min_quantity > max_quantity) or (min_quantity < 0 or max_quantity < 0):
                raise ValueError(f"Invalid prices for min_quanity={min_quantity} and max_quantity={max_quantity}")

        # is order_field valid?
        if order_field != "name" and order_field != "quantity":
            return  self.product_repository.search_products(None, None, name, id, min_quantity, max_quantity, unit_id)

        # No need to check order_type, ascending is default unless descending is specified
        return self.product_repository.search_products(order_field, order_type, name, id, min_quantity, max_quantity, unit_id)

#####################################################################################################


    def buy_product(
        self,
        product_id: str,
        purchased_quantity: int,
    ) -> Product:
        """
        Buy a product and update it to the database

        This method fetches the database for the product identified by `product_id`.
        It then decreases the unit_gain (balance) and increases the quantity of the product
        based on the `purchased_quantity`.

        Args:
            product_id (str): The id of the product to buy.
            purchased_quantity (int): The quantity of items of the product to be purchased.

        Returns:
            Product: The updated product

        Raises:
            ProductNotFoundByIdError: If no product exists with the given `product_id`
            ProductDoesNotFitInUnit: If there is no space for the product in the unit it is in.
            ValueError: If the product could not be updated
        """
        unit_id: str
        loss: float
        product: Optional[Product] = self.product_repository.get_product_by_id(product_id)

        if product is None:
            raise ProductNotFoundByIdError(product_id)

        unit_id = product.unit_id

        if not self._does_product_fit_in_unit(unit_id, int(purchased_quantity), float(product.volume)):
            raise ProductDoesNotFitInUnit(product_id, unit_id)

        # loss MUST BE NEGATIVE because of $inc in the following query
        loss = product.calculate_loss(purchased_quantity)

        # update the product and return the updated document
        try:
            updated_product = self.product_repository.buy_product(
                product_id, purchased_quantity, loss
            )
        except ValueError as e:
            raise ValueError("Could not buy product") from e

        return updated_product


    def sell_product(
        self,
        product_id: str,
        quantity_to_sell: int,
        unit_id: Optional[str] = None
    ) -> Product:
        """
        Sell a product by validating and updating it.

        This service method:
        1. Checks that the product exists.
        2. Calculates the profit for the given quantity to sell.
        3. Calls repository to update the product.

        Args:
            product_id (str): The ID of the product to sell.
            quantity_to_sell (int): The number of items to sell.
            unit_id (str): The id of the unit to were the product is stored.
                If None the method will try to find the product in all units.

        Returns:
            Product: The updated product object after the sale.

        Raises:
            ProductNotFoundByIdError: If the product does not exist.
            InsufficientProductQuantity:
                - If trying to sell more items than what is available the database.
                - If `quantity_to_sell` is negative.
            ValueError: If the product's record in the database is missing required attributes
                (see ProductRepository.sell_product() for more details).
        """
        profit: float
        product: Optional[Product] = self.product_repository.get_product_by_id(product_id)

        if product is None:
            raise ProductNotFoundByIdError(f"Product with id={product_id} does not exist.")

        if quantity_to_sell < 0:
            raise InsufficientProductQuantity(product_id, str(quantity_to_sell))

        profit = product.calculate_profit(quantity_to_sell)

        # This might throw value error
        if unit_id is None:
            updated_product = self.product_repository.sell_product(
                product_id, quantity_to_sell, profit
            )
        else:
            updated_product = self.product_repository.sell_products_from_unit(
                product_id, quantity_to_sell, profit, unit_id
            )

        if updated_product is None:
            raise InsufficientProductQuantity(product_id, str(quantity_to_sell))

        return updated_product
