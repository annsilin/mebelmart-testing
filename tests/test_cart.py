"""
tests/test_cart.py
-------------------
Test scenario 2.5: Add product to cart and verify price.

Steps:
    1. Open the couches catalog.
    2. Read the first product's name and price from the catalog card.
    3. Click the product title to open its detail page.
    4. Select product options if required (color, upholstery, etc.).
    5. Click "В корзину" on the product detail page.
    6. Navigate to the cart via the header cart icon.
    7. Verify the product is present in the cart.
    8. Verify the cart price matches the catalog price.

Expected result:
    The first couch is in the cart and its price matches the catalog.
"""

import logging

import allure
import pytest

from pages.cart_page import CartPage
from pages.couches_catalog_page import CouchesCatalogPage
from pages.favorites_page import FavoritesPage
from pages.product_page import ProductPage

logger = logging.getLogger(__name__)


@allure.feature("Cart")
@allure.story("Add to cart")
@allure.title("Scenario 2.5: First catalog product can be added to cart with correct price")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_add_to_cart_and_verify_price(page):
    """
    Scenario 2.5: Add the first catalog product to the cart and verify
    the price matches what was shown in the catalog.
    """
    catalog = CouchesCatalogPage(page)
    product = ProductPage(page)
    cart = CartPage(page)

    # Open the couches catalog
    with allure.step("Step 1: Open the couches catalog"):
        catalog.open_catalog()
        assert catalog.is_catalog_loaded(), "Couches catalog page did not load"

    # Read first product name and price from catalog card
    with allure.step("Step 2: Read first product name and price from catalog card"):
        product_name = catalog.get_first_product_name()
        assert product_name, "Could not read the first product name"

        catalog_prices = catalog.get_product_prices()
        assert catalog_prices, "Could not read prices from catalog"
        catalog_price = catalog_prices[0]

        allure.attach(
            f"Product: {product_name}\nCatalog price: {catalog_price:,} ₽",
            name="Catalog card data",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("First product: '%s', catalog price: %d ₽", product_name, catalog_price)

    # Click product title to open detail page
    with allure.step(f"Step 3: Open '{product_name}' detail page"):
        catalog.click_product_link(product_name)
        assert product.is_product_page(), "Product detail page did not load"

        page_title = product.get_product_title()
        allure.attach(page_title, name="Product page title",
                      attachment_type=allure.attachment_type.TEXT)
        logger.info("Product page: '%s'", page_title)

    # Select options if needed, then click "В корзину"
    with allure.step("Steps 4–5: Select options (if any) and click 'В корзину'"):
        product.click_add_to_cart()

    # Navigate to cart
    with allure.step("Step 6: Open cart via header icon"):
        cart.navigate_to_cart()
        assert cart.is_loaded(), "Cart page did not load"

    # Verify product is in cart
    with allure.step(f"Step 7: Verify '{product_name}' is in the cart"):
        item_names = cart.get_item_names()
        allure.attach(
            "\n".join(item_names) if item_names else "(empty)",
            name="Cart items",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("Cart items: %s", item_names)

        model_name = FavoritesPage._model_name(product_name)
        found = any(model_name.lower() in name.lower() for name in item_names)
        assert found, (
            f"'{product_name}' (model: '{model_name}') not found in cart. "
            f"Items: {item_names}"
        )

    # Verify price matches catalog
    with allure.step(f"Step 8: Verify cart price = catalog price ({catalog_price:,} ₽)"):
        cart_total = cart.get_total_price()
        allure.attach(
            f"Catalog price: {catalog_price:,} ₽\nCart total: {cart_total:,} ₽",
            name="Price comparison",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("Catalog: %d ₽, cart total: %s ₽", catalog_price, cart_total)

        assert cart_total is not None and cart_total > 0, "Could not read cart total"
        assert cart_total == catalog_price, (
            f"Price mismatch: catalog {catalog_price:,} ₽ vs cart {cart_total:,} ₽"
        )