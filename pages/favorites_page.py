"""
pages/favorites_page.py
------------------------
Page Object for the favorites page:
    https://mebelmart-saratov.ru/favorite/

Layer: Page Layer (Layered Architecture).
"""

import logging

import allure
from playwright.sync_api import Page

from config.config import BASE_URL
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class FavoritesPage(BasePage):
    """Page Object for the Mebelmart favorites (wishlist) page."""

    URL: str = f"{BASE_URL}/favorite/"

    # Page structure
    PAGE_CONTAINER   = ".page-favorite"
    ITEMS_COUNT      = "#w0 .w-100"

    # Product cards (same markup as catalog)
    PRODUCT_CARD      = ".page-favorite .product-card"
    PRODUCT_NAME_LINK = ".page-favorite .product-card__name a"

    # Active (filled) favorite icon inside a card - confirms item is saved
    FAVORITE_ICON_ACTIVE = ".page-favorite .favorite-icon.active"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Open favorites page")
    def open_favorites(self) -> "FavoritesPage":
        """Navigate directly to the favorites page URL."""
        self.open(self.URL)
        self._wait_for_page()
        logger.info("Favorites page loaded: %s", self.current_url)
        return self

    def is_loaded(self) -> bool:
        """Return True if the favorites page container is present."""
        try:
            self.page.locator(self.PAGE_CONTAINER).wait_for(timeout=10_000)
            return True
        except Exception:
            return False

    def get_product_names(self) -> list[str]:
        """Return names of all products currently in the favorites list."""
        elements = self.page.locator(self.PRODUCT_NAME_LINK).all()
        return [el.text_content().strip() for el in elements if el.text_content().strip()]

    # Furniture type prefixes that may differ between the catalog and
    # the favorites / product pages (e.g. "Диван Лотос" vs "Модульный набор ... Лотос").
    # Stripping these prefixes lets us match by the model name alone.
    _FURNITURE_PREFIXES = (
        "Диван ", "Угловой диван ", "Кресло ", "Кровать ",
        "Шкаф ", "Комод ", "Стол ", "Пуф ",
    )

    @staticmethod
    def _model_name(full_name: str) -> str:
        """
        Extract the model name by stripping known furniture type prefixes.

        Examples:
            "Диван Лотос"  → "Лотос"
            "Лотос"        → "Лотос"

        Args:
            full_name: Full product name as shown in the catalog or page.

        Returns:
            Model name string with the furniture prefix removed.
        """
        for prefix in FavoritesPage._FURNITURE_PREFIXES:
            if full_name.startswith(prefix):
                return full_name[len(prefix):]
        return full_name

    def is_product_in_favorites(self, product_name: str) -> bool:
        """
        Return True if a product whose model name matches the given name
        exists on the favorites page.

        Comparison is done on the model name only (furniture type prefix
        is stripped).

        Args:
            product_name: Full or partial product name from the catalog card.
        """
        model = self._model_name(product_name)
        locator = self.page.locator(
            f"xpath=//div[contains(@class,'product-card__name')]"
            f"//a[contains(., '{model}')]"
        )
        try:
            locator.first.wait_for(timeout=10_000)
            return True
        except Exception:
            return False

    def get_items_count_text(self) -> str:
        """Return the summary text, e.g. 'Показаны записи 1-1 из 1'."""
        try:
            el = self.page.locator(self.ITEMS_COUNT).first
            el.wait_for(timeout=10_000)
            return el.text_content().strip()
        except Exception:
            return ""

    def _wait_for_page(self) -> None:
        """Wait for the favorites page container to appear."""
        try:
            self.page.locator(self.PAGE_CONTAINER).wait_for(timeout=30_000)
        except Exception:
            logger.warning("Favorites page container did not appear within timeout")