"""
pages/cart_page.py
------------------
Page Object for the shopping cart page:
    https://mebelmart-saratov.ru/cart

Layer: Page Layer (Layered Architecture).
"""

import logging

import allure
from playwright.sync_api import Page

from config.config import BASE_URL
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class CartPage(BasePage):
    """Page Object for the Mebelmart shopping cart."""

    URL: str = f"{BASE_URL}/cart"

    # Cart widget (rendered by JS)
    CART_WIDGET = "#cartWidget"

    CART_ITEM = "#cartWidget .list-group-item"
    CART_ITEM_NAME = "#cartWidget .list-group-item a.font-weight-bold"

    # Price cell - second .col-md-2 inside the row
    # Structure: col-md-6 (name+options) | col-md-2 (price) | col-md-2 (qty) | col-md-2 (delete)
    CART_ITEM_PRICE = "#cartWidget .list-group-item .col-md-2:nth-child(2)"

    CART_TOTAL = "#cartWidget .my-4 h2"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Navigate to cart page via header link")
    def navigate_to_cart(self) -> "CartPage":
        """Click the cart icon in the stage2 desktop header."""
        locator = self.page.locator(".header-laptop__cart a")
        locator.wait_for(state="visible", timeout=10_000)
        locator.click()
        self._wait_for_widget()
        logger.info("Cart page loaded: %s", self.current_url)
        return self

    def is_loaded(self) -> bool:
        """Return True if the cart widget is present on the page."""
        try:
            self.page.locator(self.CART_WIDGET).wait_for()
            self.page.locator(self.CART_ITEM).first.wait_for(timeout=15_000)
            self.page.wait_for_timeout(2000)
            return True
        except Exception:
            return False

    def get_item_names(self) -> list[str]:
        """Return names of all products currently in the cart."""
        elements = self.page.locator(self.CART_ITEM_NAME).all()
        return [el.text_content().strip() for el in elements if el.text_content().strip()]

    def is_product_in_cart(self, product_name: str) -> bool:
        """
        Return True if a product whose name contains the given substring
        is present in the cart.

        Args:
            product_name: Partial or full product name to search for.
        """
        locator = self.page.locator(
            f"xpath=//*[@id='cartWidget']//a[contains(@class,'font-weight-bold')"
            f" and contains(., '{product_name}')]"
        )
        try:
            locator.first.wait_for(timeout=10_000)
            return True
        except Exception:
            return False

    def get_item_price(self, product_name: str) -> int | None:
        """
        Return the price (in RUB) shown in the cart row for the named product.

        Args:
            product_name: Partial or full product name.

        Returns:
            Integer price, or None if the product is not found.
        """
        locator = self.page.locator(
            f"xpath=//*[@id='cartWidget']//div[contains(@class,'list-group-item')]"
            f"[.//a[contains(., '{product_name}')]]"
            f"//div[contains(@class,'col-md-2')][1]"
        )
        try:
            locator.first.wait_for(timeout=10_000)
            raw = locator.first.text_content().strip()
            return self._parse_price(raw)
        except Exception as exc:
            logger.warning("Cart price not found for '%s': %s", product_name, exc)
            return None

    def get_total_price(self) -> int | None:
        """
        Return the order total shown at the bottom of the cart widget.

        Parses text like "Итого: 12 405 Р" -> 12405.
        """
        try:
            el = self.page.locator(self.CART_TOTAL).first
            el.wait_for(timeout=10_000)
            raw = el.text_content().strip()
            return self._parse_price(raw)
        except Exception as exc:
            logger.warning("Cart total not found: %s", exc)
            return None

    # Private helpers
    def _wait_for_widget(self) -> None:
        """Wait for the cart JS widget to render after navigation."""
        try:
            self.page.locator(self.CART_WIDGET).wait_for()
            self.page.locator(self.CART_ITEM).first.wait_for(timeout=15_000)
        except Exception:
            logger.warning("Cart widget did not appear within timeout")

    @staticmethod
    def _parse_price(raw: str) -> int:
        """
        Parse a price string into an integer, stripping all non-digit characters.

        Handles:
            "12 405 Р" -> 12405
            "Итого: 12 405 Р" -> 12405
            "12\u00a0405Р" -> 12405

        Returns:
            Integer price, or 0 on parse failure.
        """
        try:
            digits = "".join(c for c in raw if c.isdigit())
            return int(digits) if digits else 0
        except (ValueError, AttributeError):
            logger.debug("Failed to parse cart price: '%s'", raw)
            return 0
