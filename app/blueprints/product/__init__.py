import re
from typing import List, Optional, Tuple

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.blueprints.names import PRODUCT_BP
from app.exceptions.exceptions import (
    InsufficientProductQuantity,
    ProductNotFoundByIdError,
    UnitNotFoundByIdError,
)
from app.model.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.utils.auth_utils import is_admin_logged_in, login_required, required_role


def create_product_blueprint(product_service: ProductService):
    product_bp = Blueprint(PRODUCT_BP, __name__, template_folder="templates")


    def _view_products() -> Tuple[Optional[List[Product]], Optional[str]]:
        products: Optional[List[Product]]
        error: Optional[str] = None
        try:
            if is_admin_logged_in():
                products = product_service.get_products()
            else:
                products = product_service.get_products_from_unit(session["unit_id"])
        except UnitNotFoundByIdError:
            error = "Could not find your unit."
        except ValueError:
            error = "The product's record in the database is missing required attributes."

        return products, error


    def _get_product_or_error(product_id: str, unit_id: Optional[str] = None) -> Tuple[Optional[Product], Optional[str]]:
        product: Optional[Product] = None
        error: Optional[str]       = None
        try:
            product = product_service.get_product_by_id(product_id, unit_id)
        except ProductNotFoundByIdError:
            error="Could not find product."
        except ValueError:
            error="The product's record in the database is missing required attributes."

        return product, error


    def _sell_product_or_error(product_id:str, quantity_to_sell: float) -> Tuple[Optional[Product], Optional[str]]:
        product: Optional[Product] = None
        error: Optional[str]       = None
        try:
            product = product_service.sell_product(product_id, int(quantity_to_sell))
        except ProductNotFoundByIdError:
            error="Could not find product."
        except InsufficientProductQuantity:
            error="There are not enough items of the product in stock."
        except ValueError:
            error=(
                "The product's record in the database is missing required attributes"
                "or the quantity to sell is not a number."
            )

        return product, error


    @product_bp.route("/search-products", methods=["GET", "POST"])
    @login_required
    @required_role("employee")
    def search_products():
        error: Optional[str]           = ""
        products: List[Product]        = []
        start_index_int: Optional[int] = None
        end_index_int: Optional[int]   = None
        search_products_page: str      = "product/search_products.html"

        if request.method != "POST":
            products_list, error = _view_products()
            if error:
                return render_template(search_products_page, error=error)

            return render_template(search_products_page, products=products_list)

        # if the field is falsy (here it can be empty string "") assign None
        # 0 can be falsy, but this is not a problem because if 0 is entered in form
        # min_quantity will be "0" which is not falsy
        order_field: Optional[str]  = request.form.get("order_field") or None
        order_type: Optional[str]   = request.form.get("order_type") or None
        product_name: Optional[str] = request.form.get("product_name") or None
        product_id: Optional[str]   = request.form.get("product_id") or None
        min_quantity: Optional[str] = request.form.get("start_index") or None
        max_quantity: Optional[str] = request.form.get("end_index") or None
        unit_id: Optional[str]      = session.get("unit_id")

        # are both present?
        if min_quantity not in ("", None) and max_quantity not in ("", None):
            try:
                start_index_int = int(min_quantity)
                end_index_int   = int(max_quantity)
            except ValueError:
                error = "From and To fields must be numbers"
                return render_template(search_products_page, error=error, products=products)

        try:
            products = product_service.search_products(order_field, order_type, product_name, product_id, start_index_int, end_index_int, unit_id)
        except ValueError:
            error = "Invalid prices for range fields."
            return render_template(search_products_page, error=error)

        if not products:
            error = "No products found"
            return render_template(search_products_page, error=error)

        return render_template(search_products_page, error=error, products=products)


    @product_bp.route("/products", methods=["GET", "POST"])
    # need POST to build ulr, otherwise it would be /products?product_id=<value> when manual searching
    @product_bp.route("/products/<product_id>", methods=["GET", "POST"])
    @login_required
    @required_role("employee")
    def view_product(product_id: Optional[str] = None):
        product: Optional[Product] = None
        view_product_page: str     = "product/view_product.html"
        unit_id: Optional[str]     = session.get("unit_id")

        # Case 1: Came here after viewing all products and choosing one
        if product_id:
            product, error = _get_product_or_error(product_id, unit_id)
            if error:
                return render_template(view_product_page, error=error)
            return render_template(
                view_product_page, product=product, product_id=product_id
            )

        # Case 2: manual search by entering a product's id
        # The user enters the product's id
        if request.method != "POST":
            return render_template(view_product_page, product_id="")

        product_id = request.form.get("product_id")

        if not product_id:
            return render_template(view_product_page)

        # retrieve product_id and redirect to Case 1 (to build ulr like: products/<product_id>)
        return redirect(url_for("product.view_product", product_id=product_id))


    @product_bp.route("/products/sell", methods=["GET", "POST"])
    # need POST to build ulr, otherwise it would be /products/sell?product_id=<value> when manual searching
    @product_bp.route("/products/<product_id>/sell", methods=["GET", "POST"])
    @login_required
    @required_role("employee")
    def sell_product(product_id: Optional[str] = None):
        products: List[Optional[Product]]        = []
        error: Optional[str]                     = None
        product_to_sell: Optional[Product]       = None
        product_after_sell: Optional[Product]    = None
        unit_id: Optional[str]                   = session.get("unit_id")
        sell_product_page                        = "product/sell_product.html"

        if request.method == "GET":
            # Case 1: Came here from view_product:
            if product_id:
                # get old product and show it.
                product_to_sell, error = _get_product_or_error(product_id, unit_id)
                if error:
                    return render_template(
                        sell_product_page, product_id=product_id, error=error
                    )
                return render_template(
                    sell_product_page, product_id=product_id, products=[product_to_sell]
                )
            return render_template(sell_product_page, product_id="")

        # Case 2: Came here after clicking sell product in dashboard:
        # POST is used here
        product_id       = request.form.get("product_id")
        quantity_to_sell = request.form.get("product_quantity_sell")

        if not product_id:
            return render_template(sell_product_page)

        # retrieve product from db
        product_to_sell, error = _get_product_or_error(product_id, unit_id)
        if error:
            return render_template(
                sell_product_page, product_id=product_id, error=error
            )
        products.append(product_to_sell)

        # show product and its id
        if not quantity_to_sell:
            return render_template(
                sell_product_page, product_id=product_id, products=products
            )

        # sell product
        product_after_sell, error = _sell_product_or_error(product_id, int(quantity_to_sell))
        if error:
            return render_template(
                sell_product_page, product_id=product_id, products=products, error=error
            )
        products.append(product_after_sell)

        # show product before and after selling
        return render_template(
            sell_product_page, product_id=product_id, products=products
        )


    return product_bp
