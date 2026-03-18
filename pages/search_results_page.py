"""
pages/search_results_page.py
-----------------------------
Page Object for the search results page:
    https://mebelmart-saratov.ru/search/<query>

Layer: Page Layer (Layered Architecture).
"""

import logging

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class SearchResultsPage(BasePage):
    """Page Object for the Mebelmart search results page."""

    SEARCH_INPUT = ".header-laptop__stage2 .searchInput"
    SEARCH_BUTTON = ".header-laptop__stage2 .submit"

    # Results page structure
    PAGE_CONTAINER = ".page-search"
    RESULTS_HEADING = ".page-search h1"
    ITEMS_COUNT = ".page-search #w0 .w-100"
    PRODUCT_CARD = ".page-search .product-card"
    PRODUCT_NAME = ".page-search .product-card__name a"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Type '{query}' in the search box and submit")
    def search(self, query: str) -> "SearchResultsPage":
        """
        Type the query into the desktop search input and press Enter.

        Args:
            query: Search term to enter, e.g. "Чебурашка".
        """
        input_el = self.page.locator(self.SEARCH_INPUT)
        input_el.wait_for(state="visible", timeout=10_000)
        input_el.fill(query)
        input_el.press("Enter")
        logger.info("Search submitted: '%s'", query)
        self._wait_for_results()
        return self

    def is_loaded(self) -> bool:
        """Return True if the search results container is present."""
        try:
            self.page.locator(self.PAGE_CONTAINER).wait_for(timeout=10_000)
            return True
        except Exception:
            return False

    def get_heading(self) -> str:
        """Return the h1 heading text, e.g. 'Поиск «чебурашка»'."""
        try:
            return self.page.locator(self.RESULTS_HEADING).text_content().strip()
        except Exception:
            return ""

    def get_product_names(self) -> list[str]:
        """Return names of all products shown in search results."""
        elements = self.page.locator(self.PRODUCT_NAME).all()
        return [el.text_content().strip() for el in elements if el.text_content().strip()]

    def get_first_product_name(self) -> str | None:
        """Return the name of the first product in the results list."""
        try:
            el = self.page.locator(self.PRODUCT_NAME).first
            el.wait_for(timeout=10_000)
            return el.text_content().strip()
        except Exception:
            return None

    def get_items_count_text(self) -> str:
        """Return the summary text, e.g. 'Показаны записи 1-7 из 7'."""
        try:
            el = self.page.locator(self.ITEMS_COUNT).first
            el.wait_for(timeout=10_000)
            return el.text_content().strip()
        except Exception:
            return ""

    def _wait_for_results(self) -> None:
        """Wait for the search results container to appear after submission."""
        try:
            self.page.locator(self.PAGE_CONTAINER).wait_for(timeout=30_000)
        except Exception:
            logger.warning("Search results container did not appear within timeout")
