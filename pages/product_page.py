"""
pages/product_page.py
---------------------
Page Object for the individual product detail page (Playwright).

Covers:
    - Reading the product title from h1
    - Switching to the "Characteristics" tab
    - Parsing the characteristics table into a dict

Layer: Page Layer (Layered Architecture).
"""

import logging

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ProductPage(BasePage):
    """Page Object for a single product's detail view."""

    # Heading
    PRODUCT_TITLE = "h1"

    # Tabs
    # "Характеристики" tab trigger link
    CHARACTERISTICS_TAB = "#singleProdParamTab"
    # Tab panel that becomes visible after clicking the tab
    CHARACTERISTICS_PANEL = "#singleProdParam"
    # Rows inside the characteristics table
    CHARACTERISTICS_ROWS = "#singleProdParam table tbody tr"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # Title
    @allure.step("Get product title")
    def get_product_title(self) -> str:
        """Return the product name from the h1 heading."""
        try:
            return self.page.locator(self.PRODUCT_TITLE).first.text_content().strip()
        except Exception:
            return ""

    def is_product_page(self) -> bool:
        """Return True if the h1 heading is present on the current page."""
        try:
            self.page.locator(self.PRODUCT_TITLE).first.wait_for(timeout=5_000)
            return True
        except Exception:
            return False

    # Characteristics tab

    @allure.step("Open 'Characteristics' tab")
    def open_characteristics_tab(self) -> None:
        """Click the characteristics tab and wait for its panel to become visible."""
        tab = self.page.locator(self.CHARACTERISTICS_TAB)
        tab.wait_for(timeout=10_000)
        self.scroll_to_center(tab)
        tab.click()
        # Wait for the panel to become visible after the Bootstrap transition
        self.page.locator(self.CHARACTERISTICS_PANEL).wait_for(
            state="visible", timeout=10_000
        )
        self.page.wait_for_timeout(2000)
        logger.debug("Characteristics tab opened")

    @allure.step("Read characteristics table")
    def get_characteristics(self) -> dict[str, str]:
        """
        Parse the characteristics table into a key-value dictionary.

        Table structure (one row per characteristic):
            <tr>
                <td>Ширина, мм.</td>   # characteristic name
                <td>1400</td>          # characteristic value
            </tr>

        Returns:
            Dict mapping characteristic name to its string value, e.g.
            {"Ширина, мм.": "1400", "Глубина, мм.": "850", ...}.
            Empty rows are skipped silently.
        """
        rows = self.page.locator(self.CHARACTERISTICS_ROWS).all()
        characteristics: dict[str, str] = {}
        for row in rows:
            cells = row.locator("td").all()
            if len(cells) >= 2:
                key = cells[0].text_content().strip()
                value = cells[1].text_content().strip()
                if key:
                    characteristics[key] = value
        logger.debug("Characteristics read: %s", characteristics)
        return characteristics

    def get_characteristic_value(self, name: str) -> str | None:
        """
        Return the value of a single characteristic by its name.

        Performs a case-insensitive prefix match, so "Ширина" matches
        "Ширина, мм." in the table.

        Args:
            name: Characteristic name or its prefix.

        Returns:
            String value, or None if not found.
        """
        chars = self.get_characteristics()
        name_lower = name.lower()
        for key, value in chars.items():
            if key.lower().startswith(name_lower):
                return value
        return None

    ADD_TO_CART_BTN = "a.btnToCart"
    SELECT_BTN = ".select-block .select__btn"
    OPTION_LIST_ITEM = ".select-block .select .optionList .optionList__item"


    @allure.step("Wait for product page to fully load")
    def wait_for_page_ready(self) -> None:
        """Wait for the product page to be fully loaded and interactive."""
        self.page.wait_for_load_state("load")
        self.page.locator(self.ADD_TO_CART_BTN).first.wait_for(
            state="visible", timeout=15_000
        )
        logger.info("Product page fully loaded and interactive")

    @allure.step("Click 'В корзину' button")
    def click_add_to_cart(self) -> None:
        """Click the 'В корзину' button on the product detail page."""

        self.wait_for_page_ready()

        # Use .first - the page has a second hidden .btnToCart inside the
        # quick-order modal, which causes a strict mode violation otherwise.
        btn = self.page.locator(self.ADD_TO_CART_BTN).first
        self.scroll_to_center(btn)

        # Wait for the button to be fully enabled before clicking
        btn.wait_for(state="visible", timeout=10_000)
        btn.dispatch_event("click")

        # Wait for the AJAX add-to-cart request to complete.
        try:
            self.page.wait_for_function(
                "() => document.querySelector('.cart-counter b') !== null"
                " && document.querySelector('.cart-counter b').textContent.trim() !== ''",
                timeout=8_000,
            )
        except Exception:
            self.page.wait_for_timeout(2000)

        logger.info("'В корзину' complete")

    def get_product_price_from_page(self) -> int | None:
        """
        Read the current price from the product detail page.

        Returns:
            Integer price in RUB, or None if not found.
        """
        locator = self.page.locator(
            "xpath=//div[contains(@class,'product-card__now_price')]"
            "//b[not(ancestor::div[contains(@class,'product-card__old_price')])"
            "  and normalize-space(.)!='' and normalize-space(.)!='₽'][1]"
        )
        try:
            locator.wait_for(timeout=10_000)
            raw = locator.text_content().strip()
            digits = "".join(c for c in raw if c.isdigit())
            return int(digits) if digits else None
        except Exception as exc:
            logger.warning("Product page price not found: %s", exc)
            return None