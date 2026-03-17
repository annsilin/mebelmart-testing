"""
pages/couches_catalog_page.py
------------------------------
Page Object for the couches catalog page:
    https://mebelmart-saratov.ru/myagkaya_mebel_v_saratove/divanyi_v_saratove

Layer: Page Layer (Layered Architecture).
"""

import logging

import allure
from playwright.sync_api import Page

from config.config import COUCHES_URL
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class CouchesCatalogPage(BasePage):
    """Page Object for the Mebelmart couches catalog."""

    URL: str = COUCHES_URL

    # Filter
    FILTER_BLOCK = "#filterContainer"
    FILTER_APPLY_BTN = "#filterLinkContainer"

    # Product cards
    PRODUCT_CARD = ".product-card"
    PRODUCT_NAME_LINK = ".product-card__name a"
    PRODUCT_BUY_BTN = ".product-card .btn.btn-primary.btn-block"

    # XPath for the current (sale) price only.
    PRODUCT_CURRENT_PRICE_XPATH = (
        "//div[contains(@class,'product-card__now_price')]"
        "//b[not(ancestor::div[contains(@class,'product-card__old_price')])"
        "  and normalize-space(.)!='' and normalize-space(.)!='₽']"
    )

    # Pagination / summary
    ITEMS_COUNT = "#w8 > div.w-100"

    # Sub-category blocks
    SUB_CATEGORY = ".sub-category .category__name"


    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # Navigation

    @allure.step("Open couches catalog")
    def open_catalog(self) -> "CouchesCatalogPage":
        """Navigate to the catalog URL and wait for product cards to render."""
        self.open(self.URL)
        self._wait_for_products()
        logger.info("Couches catalog loaded: %s", self.current_url)
        return self

    # Data accessors

    def get_product_names(self) -> list[str]:
        """Return the display names of all product cards on the current page."""
        elements = self.page.locator(self.PRODUCT_NAME_LINK).all()
        return [el.text_content().strip() for el in elements if el.text_content().strip()]

    def get_product_prices(self) -> list[int]:
        """
        Return the current prices of all products on the page.
        Iterates over individual cards and scopes the XPath query to each card
        to avoid cross-card matches.
        """
        cards = self.page.locator(self.PRODUCT_CARD).all()
        prices: list[int] = []
        for card in cards:
            try:
                price_els = card.locator(f"xpath={self.PRODUCT_CURRENT_PRICE_XPATH}").all()
                if price_els:
                    raw = price_els[0].text_content().strip()
                    price = self._parse_price(raw)
                    if price > 0:
                        prices.append(price)
            except Exception as exc:
                logger.warning("Could not read price from card: %s", exc)
        return prices

    def get_items_count_text(self) -> str:
        """Return the pagination summary text, e.g. 'Records 1-25 of 526'."""
        try:
            el = self.page.locator(self.ITEMS_COUNT).first
            el.wait_for(timeout=10_000)
            return el.text_content().strip()
        except Exception:
            return ""

    @allure.step("Find product by name: {name}")
    def find_product_by_name(self, name: str):
        """
        Locate the first product card whose title contains the given substring.

        Args:
            name: Partial or full product name to search for.

        Returns:
            Locator pointing to the matching title element, or None if not found.
        """
        locator = self.page.locator(
            f"xpath=//div[contains(@class,'product-card__name')]"
            f"//a[contains(., '{name}')]"
        )
        try:
            locator.first.wait_for(timeout=10_000)
            return locator.first
        except Exception:
            return None

    def get_product_price_by_name(self, name: str) -> int | None:
        """
        Return the current price (in RUB) of the product matching the given name.

        Args:
            name: Partial or full product name.

        Returns:
            Integer price in rubles, or None if the product or its price
            cannot be located.
        """
        locator = self.page.locator(
            f"xpath=//div[contains(@class,'product-card__name')]"
            f"//a[contains(., '{name}')]"
            f"/ancestor::div[contains(@class,'product-card')]"
            f"//div[contains(@class,'product-card__now_price')]"
            f"//b[not(ancestor::div[contains(@class,'product-card__old_price')])"
            f"  and normalize-space(.)!='' and normalize-space(.)!='₽'][1]"
        )
        try:
            locator.first.wait_for(timeout=10_000)
            raw = locator.first.text_content().strip()
            return self._parse_price(raw)
        except Exception as exc:
            logger.warning("Price not found for '%s': %s", name, exc)
            return None

    def is_catalog_loaded(self) -> bool:
        """Return True if at least one product card is visible on the page."""
        try:
            self.page.locator(self.PRODUCT_CARD).first.wait_for(timeout=10_000)
            return True
        except Exception:
            return False

    # Private helpers
    def _wait_for_products(self) -> None:
        """Wait until at least one product card appears in the DOM."""
        try:
            self.page.locator(self.PRODUCT_CARD).first.wait_for(timeout=30_000)
        except Exception:
            logger.warning("Product cards did not appear within the timeout")

    @staticmethod
    def _parse_price(raw: str) -> int:
        """
        Parse a price string into an integer.

        Handles Russian locale formatting where thousands are separated
        by a non-breaking space, e.g. "12\u00a0405" → 12405.

        Args:
            raw: Raw price string from the page, e.g. "12 405" or "12405".

        Returns:
            Price as an integer in rubles, or 0 if parsing fails.
        """
        try:
            cleaned = (
                raw.replace("\u00a0", "")
                .replace("\xa0", "")
                .replace(" ", "")
                .replace("₽", "")
                .strip()
            )
            return int(cleaned)
        except (ValueError, AttributeError):
            logger.debug("Failed to parse price string: '%s'", raw)
            return 0
