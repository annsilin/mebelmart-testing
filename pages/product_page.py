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
        tab.click()
        # Wait for the panel to become visible after the Bootstrap transition
        self.page.locator(self.CHARACTERISTICS_PANEL).wait_for(
            state="visible", timeout=10_000
        )
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

    def select_first_available_options(self) -> None:
        """
        Select the first option in every product configurator dropdown.
        If no configurator dropdowns are present the method exits silently.
        """
        select_btns = self.page.locator(self.SELECT_BTN).all()
        if not select_btns:
            logger.debug("No option dropdowns found - skipping option selection")
            return

        logger.info("Selecting first option in %d dropdown(s)", len(select_btns))
        # The optionList items are hidden by CSS until the dropdown is opened.
        # We use JS to click them directly, bypassing Playwright's visibility check.
        self.page.evaluate("""
                           () => {
                               document.querySelectorAll('.select-block .select').forEach(select => {
                                   const firstItem = select.querySelector('.optionList .optionList__item');
                                   if (firstItem) {
                                       firstItem.click();
                                   }
                               });
                           }
                           """)
        self.page.wait_for_timeout(500)
        logger.info("Options selected via JS")

    @allure.step("Click 'В корзину' button")
    def click_add_to_cart(self) -> None:
        """Click the 'В корзину' button on the product detail page."""
        # Select all required product options first (color, etc.)
        # Some products will not add to cart without explicit option selection.
        self.select_first_available_options()

        # Use .first - the page has a second hidden .btnToCart inside the
        # quick-order modal, which causes a strict mode violation otherwise.
        btn = self.page.locator(self.ADD_TO_CART_BTN).first
        btn.wait_for(state="visible", timeout=10_000)
        btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)

        # Dismiss an alert that pops up after adding an item to the cart
        def _dismiss_dialog(dialog):
            logger.info("Dialog appeared: '%s' - dismissing", dialog.message)
            dialog.dismiss()

        self.page.once("dialog", _dismiss_dialog)

        btn.dispatch_event("click")

        # Wait for the AJAX add-to-cart request to finish
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