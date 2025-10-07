from typing import List, Optional

from pymongo import ASCENDING, DESCENDING
from pymongo.database import Collection
from pymongo.results import InsertManyResult, InsertOneResult

from app.model.product import Product


class ProductRepository:
    product_collection: Collection

    def __init__(self, product_collection: Collection):
        self.product_collection = product_collection

    def get_product_by_id(
        self, id: str, unit_id: Optional[str] = None
    ) -> Product | None:
        """
        Get a Product instance from the DB by ID.

        Args:
            id (str): The ID of the product to retrieve.
            unit_id (str | None): The id of the unit where the product is stored.
                If None the method looks for products in all units.

        Returns:
            product (Product): A Product object with the information
            of the product identified by `id`.

        Raises:
            ValueError: If the product record is missing required attributes
                (see Product.from_dict()).
        """
        query = {"id": id}
        if unit_id is not None:
            query["unit_id"] = unit_id
        result = self.product_collection.find_one(query)

        if result is None:
            return None

        return Product.from_dict(result)


    def get_products(self) -> List[Product]:
        """
        Get all the products in the database.

        Returns:
            List[Product]: A list of Product instances of all the products inside the database.

        Raises:
            ValueError: If the product record is missing required attributes
                (see ProductRepository.from_dict()).
        """
        cursor = self.product_collection.find()
        return [Product.from_dict(product) for product in cursor]


    def get_products_from_unit(self, unit_id: str):
        """
        Get all the products inside the unit identified by `unit_id`.

        Args:
            unit_id (str): The id of the unit from which to get the products from.

        Returns:
            List[Product]: A list of Product instances of all the products inside the unit
                identified by `unit_id`.

        Raises:
            ValueError: If the product record is missing required attributes
                (see Product.from_dict()).
        """
        cursor = self.product_collection.find({"unit_id": unit_id})
        return [Product.from_dict(product) for product in cursor]


    def get_quantity_and_volume_by_unit(self, unit_id: str) -> List[dict]:
        cursor = self.product_collection.find(
            {"unit_id": unit_id},
            projection={"id": 1 ,"quantity": 1, "volume": 1}
        )
        return list(cursor)


    def buy_product(self, product_id: str, quantity: int , unit_gain: float) -> Product:
        """
        Increases the quantity and the unit_gain of the product identified by `product_id`

        Args:
            product_id (str): The id of the product to update.
            quantity (int): The amount of items of the product to add.
            unit_gain (float): The amount by which to increase the unit_gain of the product

        Returns:
            Product: The updated product

        Raises:
            ValueError:
                - If no  product was found with `product_id`
                - If the product is missing required order_fields
                (see Product.from_dict() for more details
        """
        result = self.product_collection.find_one_and_update(
            {"id": product_id},
            {"$inc": {
                "quantity": quantity,
                "unit_gain": unit_gain
            }},
            return_document=True
        )

        return Product.from_dict(result)


    def _sell_product(self, product_id: str, unit_id: Optional[str], sell_quantity: int, profit: float):
        """
        Sell a product and update it in the database 

        This method decreases the product's quantity by `items_to_sell`
        and increases its `unit_gain` by the given `profit`.

        Args:
            product_id (str): The id of the product to sell.
            unit_id (str | None): The unit in which the product belongs.
                If none the method looks at all units.
            sell_quantity (int): The quantity of items of the product to be sold.
            profit (float): The profit from selling `sell_quantity` items

        Returns:
            Product | None: If the product was updated return the updated version,
                else return None

        Raises:
            ValueError: If the product is missing required attributes
                (see Product.from_dict() for more details).
        """

        filter = {
            "id": product_id,
            # are there enough items to sell?
            "quantity": {"$gte": sell_quantity},
        }
        if unit_id is not None:
            filter["unit_id"] = unit_id

        update = {
            "$inc": {
                "quantity": -sell_quantity,  # subtract sold quantity
                "unit_gain": profit,
            }
        }

        sell_result= self.product_collection.find_one_and_update(
            filter,
            update,
            return_document=True,
        )

        if sell_result is None:
            return None

        return Product.from_dict(sell_result)


    def sell_product(self, product_id: str, sell_quantity: int, profit: float) -> Optional[Product]:
        """
        Sell a product and update it in the database 

        This method decreases the product's quantity by `items_to_sell`
        and increases its `unit_gain` by the given `profit`.

        Args:
            product_id (str): The id of the product to sell.
            sell_quantity (int): The quantity of items of the product to be sold.
            profit (float): The profit from selling `sell_quantity` items

        Returns:
            Product | None: If the product was updated return the updated version,
                else return None

        Raises:
            ValueError: If the product is missing required attributes
        """
        return self._sell_product(product_id, None, sell_quantity, profit)


    def sell_products_from_unit(self, product_id: str, sell_quantity: int, profit: float, unit_id: str):
        """
        Sell a product and update it in the database 

        This method decreases the product's quantity by `items_to_sell`
        and increases its `unit_gain` by the given `profit`.

        Args:
            product_id (str): The id of the product to sell.
            unit_id (str | None): The unit in which the product belongs.
                If none the method looks at all units.
            sell_quantity (int): The quantity of items of the product to be sold.
            profit (float): The profit from selling `sell_quantity` items

        Returns:
            Product | None: If the product was updated return the updated version,
                else return None

        Raises:
            ValueError: If the product is missing required attributes
        """
        return self._sell_product(product_id, unit_id, sell_quantity, profit)



    def insert_product(self, product: Product) -> InsertOneResult:
        """
        Inserts a product to the database

        Args:
            product (Product): The product to insert

        Returns:
            pymongo.results.InsertOneResult: The result of the insertion
        """
        return self.product_collection.insert_one(product.to_dict())


    def insert_products(self, products: List[Product]) -> InsertManyResult:
        """
        Inserts a products to the database

        Args:
            products (List[Product]): A list with the products to insert

        Returns:
            pymongo.results.InsertOneResult: The result of the insertion
        """
        return self.product_collection.insert_many([p.to_dict() for p in products])


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

        It can also order the results of the find query based on `order_field`.
        If the `order_type` has a value other than "descending",
        the products are sorted in ascending order.

        This method:
        1) Checks which of the search fields (`name`, `id`, `min_quantity`, `max_quantity`)
            are specified and applies them to the find query.
        2) Checks if `order_field` is specified.
            If it is, orders results based on `order_type`.

        Args:
            order_field (str | None): The field by which to order.
            order_type (str | None): The order type, ascending or descending.
                If not specified (None or other value) defaults to ascending order.
            name (str | None): The name of the product to search.
            id (str | None): The id of the product to search.
            min_quantity (int | None): The minimum product quantity in the database.
            max_quantity (int | None): The maximum product quantity in the database.
            unit_id (str | None): The id of the unit to search. If None all units are searched.

        Returns:
            List[Product]: List of products that match the search query, sorted if requested.
        """

        query: dict = {}
        cursor = []

        if name is not None:
            query["name"] = name

        if id is not None:
            query["id"] = id

        if unit_id is not None:
            query["unit_id"] = unit_id

        if min_quantity is not None and max_quantity is not None:
            query["quantity"] = {"$gte": min_quantity, "$lte": max_quantity}

        cursor = self.product_collection.find(query)

        if order_field is not None:
            if order_type == "descending":
                cursor = cursor.sort(order_field, DESCENDING)
            else:
                cursor = cursor.sort(order_field, ASCENDING)

        return [Product.from_dict(product) for product in cursor]
