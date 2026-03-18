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
    FILTER_PRICE_TITLE = "xpath=//a[text()='Цена']"
    FILTER_PRICE_SLIDER_INPUT = "#w0"
    FILTER_PRICE_SLIDER = "#w0-slider"
    FILTER_APPLY_BTN = "xpath=//div[contains(text(),'Применить фильтр')]"

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

    @allure.step("Open price filter")
    def open_price_filter(self) -> "CouchesCatalogPage":
        """
        Click the 'Цена' title to expand the price filter section
        and wait for the slider widget to initialize.
        """
        self.page.locator(self.FILTER_PRICE_TITLE).click()
        self.page.wait_for_selector(self.FILTER_PRICE_SLIDER, timeout=10_000)
        logger.info("Price filter opened")
        return self

    @allure.step("Set price range: {price_from} – {price_to} RUB")
    def set_price_filter(self, price_from: int, price_to: int) -> "CouchesCatalogPage":
        """
        Set the price slider range using the bootstrap-slider jQuery API.

        Args:
            price_from: Lower price bound in RUB.
            price_to:   Upper price bound in RUB.
        """
        self.page.evaluate(
            "([min, max]) => { $('#w0').slider('setValue', [Number(min), Number(max)], true, true); }",
            [price_from, price_to],
        )
        logger.info("Price slider set: %d – %d RUB", price_from, price_to)
        return self

    @allure.step("Apply filter")
    def apply_filter(self) -> "CouchesCatalogPage":
        """Click the 'Применить фильтр' button and wait for the results to reload."""
        self.page.locator(self.FILTER_APPLY_BTN).click()
        self._wait_for_products()
        logger.info("Filter applied, waiting for results")
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

    def get_catalog_card_dimensions(self, product_name: str) -> dict[str, str]:
        """
        Read dimension labels and values from the catalog card of a named product.

        Args:
            product_name: Partial or full product name to locate the card.

        Returns:
            Dict mapping dimension name to string value, e.g.
            {"Ширина": "1400", "Глубина": "850"}.
            Returns an empty dict if the card or its dimensions are not found.
        """
        card_locator = self.page.locator(
            f"xpath=//div[contains(@class,'product-card__name')]"
            f"//a[contains(., '{product_name}')]"
            f"/ancestor::div[contains(@class,'product-card')]"
        )
        try:
            card_locator.first.wait_for(timeout=10_000)
            small_els = card_locator.first.locator(".text-center small").all()
            dimensions: dict[str, str] = {}
            for el in small_els:
                raw = el.text_content().strip().rstrip(",").strip()
                # Expected format: "Ширина: 1400 мм" or "Глубина: 850 мм"
                if ":" in raw:
                    key, rest = raw.split(":", 1)
                    # Extract numeric value only
                    value = "".join(c for c in rest if c.isdigit())
                    if key.strip() and value:
                        dimensions[key.strip()] = value
            logger.debug("Catalog card dimensions for '%s': %s", product_name, dimensions)
            return dimensions
        except Exception as exc:
            logger.warning("Could not read catalog card dimensions for '%s': %s", product_name, exc)
            return {}

    # def get_product_link_by_name(self, product_name: str) -> str | None:
    #     """
    #     Return the href of the product detail link for the named catalog card.
    #
    #     Args:
    #         product_name: Partial or full product name.
    #
    #     Returns:
    #         Absolute URL string, or None if not found.
    #     """
    #     locator = self.page.locator(
    #         f"xpath=//div[contains(@class,'product-card__name')]"
    #         f"//a[contains(., '{product_name}')]"
    #     )
    #     try:
    #         locator.first.wait_for(timeout=10_000)
    #         href = locator.first.get_attribute("href")
    #         if href and href.startswith("/"):
    #             from config.config import BASE_URL
    #             href = BASE_URL + href
    #         return href
    #     except Exception as exc:
    #         logger.warning("Product link not found for '%s': %s", product_name, exc)
    #         return None

    def get_first_product_name(self) -> str | None:
        """
        Return the name of the first product card visible in the catalog.

        Returns:
            Product name string, or None if no cards are found.
        """
        try:
            el = self.page.locator(self.PRODUCT_NAME_LINK).first
            el.wait_for(timeout=10_000)
            return el.text_content().strip()
        except Exception:
            return None

    def click_favorite_icon(self, product_name: str) -> None:
        """
        Click the favorite (wishlist) icon on the card for the named product.

        Args:
            product_name: Partial or full product name to locate the card.
        """
        locator = self.page.locator(
            f"xpath=//div[contains(@class,'product-card__name')]"
            f"//a[contains(., '{product_name}')]"
            f"/ancestor::div[contains(@class,'product-card')]"
            f"//div[contains(@class,'product-card__favorites')]"
            f"//a[contains(@class,'favorite-icon')]"
        )
        locator.first.wait_for(timeout=10_000)
        locator.first.click()
        logger.info("Favorite icon clicked for '%s'", product_name)

    def is_favorite_icon_active(self, product_name: str) -> bool:
        """
        Return True if the favorite icon on the named product's card has the
        'active' CSS class, indicating the product is in the favorites list.

        Args:
            product_name: Partial or full product name.
        """
        locator = self.page.locator(
            f"xpath=//div[contains(@class,'product-card__name')]"
            f"//a[contains(., '{product_name}')]"
            f"/ancestor::div[contains(@class,'product-card')]"
            f"//a[contains(@class,'favorite-icon') and contains(@class,'active')]"
        )
        try:
            locator.first.wait_for(timeout=5_000)
            return True
        except Exception:
            return False

    def navigate_to_favorites(self) -> None:
        """
        Click the favorites icon in the main desktop header to open
        the favorites page.
        """
        locator = self.page.locator(".header-laptop__favorite a.favorite-informer")
        locator.wait_for(state="visible", timeout=10_000)
        locator.click()
        logger.info("Navigated to favorites via desktop header link")

    def click_product_link(self, product_name: str) -> None:
        """
        Click the product title link on the catalog card to open its detail page.

        Args:
            product_name: Partial or full product name to locate the card.
        """
        locator = self.page.locator(
            f"xpath=//div[contains(@class,'product-card__name')]"
            f"//a[contains(., '{product_name}')]"
        )
        locator.first.wait_for(timeout=10_000)
        locator.first.click()
        logger.info("Clicked product link for '%s'", product_name)
