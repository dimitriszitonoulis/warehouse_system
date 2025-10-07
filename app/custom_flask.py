from flask import Flask
from pymongo.collection import Collection
from pymongo.database import Database


class CustomFlask(Flask):
    db: Database
    admin_collection: Collection
    unit_collection: Collection
    product_collection: Collection
    user_collection: Collection

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

