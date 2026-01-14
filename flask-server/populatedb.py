import os

from pymongo import MongoClient
from pymongo.database import Collection

from app.model.employee import Employee
from app.model.product import Product
from app.model.supervisor import Supervisor
from app.model.unit import Unit
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.supervisor_repository import SupervisorRepository
from app.repositories.unit_repository import UnitRepository


def add_employees(emp_repo: EmployeeRepository, user_collection: Collection):
    employees_list = []

    values = {
        "name": ["John", "Mary", "Jim", "Pam", "Andrew", "Peter"],
        "surname": ["Smith", "Jacobs", "Halpert", "Wesley", "Mathews", "Parker"],
        "username": ["js", "mj", "jh", "pw", 'am', "pp"],
        "password": ["12","12","12","12","12", "12"],
        "unit_id": ["u1", "u1", "u2", "u2", "u3", "u3"],
    }
    employees_to_add = len(values["name"])

    for i in range(employees_to_add):
        employee = {}
        for field in values.keys():
            employee[field] = values[field][i]
        employees_list.append(Employee.from_persistence_dict(employee))

    result = emp_repo.insert_employees(employees_list)

    print(f"Inserted {len(result.inserted_ids)} employees")


def add_supervisors(sup_repo: SupervisorRepository):
    supervisor_list = []

    values = {
        "name": ["Bruce", "Will", "Mary"],
        "surname": ["Wayne", "Jacub", "Stokes"],
        "username": ["bw", "wj", "ms"],
        "password": ["12","12","12"],
        "unit_id": ["u1", "u2", "u3"],
        "unit_name": ["unit1", "unit2", "unit3",],
    }
    supervisors_to_add = len(values["name"])

    for i in range(supervisors_to_add):
        supervisor = {}
        for field in values.keys():
            supervisor[field] = values[field][i]
        supervisor_list.append(Supervisor.from_persistence_dict(supervisor))

    result = sup_repo.insert_supervisors(supervisor_list)

    print(f"Inserted {len(result.inserted_ids)} supervisors")


def add_units(unit_repo: UnitRepository):
    unit_list = []

    values = {
        "id": ["u1", "u2", "u3"],
        "name": ["unit_1", "unit_2", "unit_3"],
        "volume": [100, 100, 100]
    }

    units_to_add = len(values["name"])

    for i in range(units_to_add):
        unit = {}
        for field in values.keys():
            unit[field] = values[field][i]
        unit_list.append(Unit.from_dict(unit))

    result = unit_repo.insert_units(unit_list)

    print(f"Inserted {len(result.inserted_ids)} units")


def add_products(prod_repo: ProductRepository):
    prod_list = []

    values = {
        "id": ["p1", "p2", "p3", "p4", "p5"],
        "name": ["pr1", "pr2", "pr3", "pr4", "pr5"],
        "quantity": [4, 5, 6, 7, 8],
        "sold_quantity": [1, 2, 3, 4, 5],
        "weight": [12, 5, 3, 12, 12],
        "volume": [3, 2, 1, 2, 3],
        "category": ["Electronics", "Clothing", "Book", "Electronics", "Electronics"],
        "purchase_price": [100, 20, 10, 30, 40],
        "selling_price": [150, 50, 20, 40, 50],
        "manufacturer": ["Acme", "Acme", "Acme", "Acme", "Acme"],
        "unit_gain": [100, 100, 100, 100, 100],
        "unit_id": ["u1", "u2", "u3", "u1", "u1"],
    }

    products_to_add = len(values["name"])

    for i in range(products_to_add):
        product = {}
        for field in values.keys():
            product[field] = values[field][i]
        prod_list.append(Product.from_dict(product))


    result = prod_repo.insert_products(prod_list)

    print(f"Inserted {len(result.inserted_ids)} products")


def main():
    # Connection for usage from the Lab
    # client = pymongo.MongoClient("83.212.238.166", 27017)
    MONGO_DATABASE        = os.environ.get("MONGO_DATABASE", "LogisticsDB")
    MONGO_HOST            = os.environ.get("MONGO_HOST", "localhost")
    MONGO_PORT            = int(os.environ.get("MONGO_PORT", 27017))
    client                = MongoClient(MONGO_HOST, MONGO_PORT)
    db                    = client[MONGO_DATABASE]
    user_collection       = db["users"]
    unit_collection       = db["units"]
    product_collection    = db["products"]

    user_collection.drop()
    unit_collection.drop()
    product_collection.drop()

    # repositories
    emp_repo = EmployeeRepository(user_collection)
    sup_repo = SupervisorRepository(user_collection)
    unit_repo = UnitRepository(unit_collection)
    prod_repo = ProductRepository(product_collection)

    add_employees(emp_repo, user_collection)
    add_supervisors(sup_repo)
    add_units(unit_repo)
    add_products(prod_repo)

main()
