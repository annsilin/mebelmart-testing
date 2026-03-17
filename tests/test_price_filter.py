"""
tests/test_price_filter.py
--------------------------
Test scenario 2.1: Filter by price and verify product presence.

Steps:
    1. Open the couches catalog.
    2. Apply a price filter: 10 000-15 000 RUB.
    3. Locate "Лотос" couch in the filtered results.
    4. Assert that its price falls within the active filter range.

Expected result:
    "Лотос" couch (12 405 RUB) is present in the results and its price
    satisfies the filter condition (10 000-15 000 RUB).

Note:
    The filter is applied via URL query parameters (?filterRange=&price=MIN-MAX),
"""

import logging

import allure
import pytest

from config.config import COUCHES_URL
from pages.couches_catalog_page import CouchesCatalogPage

logger = logging.getLogger(__name__)

# Test case parameters
PRICE_FROM = 10_000
PRICE_TO = 15_000

TARGET_PRODUCT_NAME = "Лотос"
TARGET_PRODUCT_PRICE = 12_405


def _build_filter_url(price_from: int, price_to: int) -> str:
    """
    Build a catalog URL with price filter query parameters.

    The site expects the format: ?filterRange=&price=MIN-MAX

    Args:
        price_from: Lower bound of the price range in RUB.
        price_to:   Upper bound of the price range in RUB.

    Returns:
        Full URL string with filter parameters applied.
    """
    return f"{COUCHES_URL}?filterRange=&price={price_from}-{price_to}"


@allure.feature("Filtering")
@allure.story("Price filter")
@allure.title(
    f"Scenario 2.1: Price filter {PRICE_FROM:,}-{PRICE_TO:,} RUB - "
    f"'{TARGET_PRODUCT_NAME}' couch ({TARGET_PRODUCT_PRICE:,} RUB) is present in results"
)
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.filter
def test_price_filter_and_product_presence(page):
    """
    Scenario 2.1: Price filter + specific product presence check.

    Verifies the end-to-end filtering flow:
        - catalog loads successfully
        - price filter narrows the results
        - a known product that matches the filter is visible
        - the product's displayed price is within the filter range
    """
    catalog = CouchesCatalogPage(page)

    # Open the couches catalog
    with allure.step("Step 1: Open the couches catalog"):
        catalog.open_catalog()
        assert catalog.is_catalog_loaded(), "Couches catalog page did not load"
        logger.info("Catalog loaded: %s", catalog.current_url)

    # Apply the price filter
    with allure.step(f"Steps 2-3: Apply price filter {PRICE_FROM:,}-{PRICE_TO:,} RUB"):
        filter_url = _build_filter_url(PRICE_FROM, PRICE_TO)
        allure.attach(
            filter_url,
            name="Filter URL",
            attachment_type=allure.attachment_type.TEXT,
        )
        catalog.open(filter_url)
        catalog._wait_for_products()
        logger.info("Filter applied: %s", filter_url)

    # Find the target product in the results
    with allure.step(f"Step 4: Find '{TARGET_PRODUCT_NAME}' couch in filtered results"):
        product = catalog.find_product_by_name(TARGET_PRODUCT_NAME)

        if product is None:
            found_names = catalog.get_product_names()
            allure.attach(
                "\n".join(found_names),
                name="Products in results (target not found)",
                attachment_type=allure.attachment_type.TEXT,
            )
            pytest.fail(
                f"'{TARGET_PRODUCT_NAME}' couch was not found in results "
                f"with price filter {PRICE_FROM:,}-{PRICE_TO:,} RUB"
            )

        logger.info("'%s' couch found in results", TARGET_PRODUCT_NAME)

    # Assert the product price is within the filter range
    with allure.step(
            f"Step 5: Assert price is within {PRICE_FROM:,}-{PRICE_TO:,} RUB"
    ):
        actual_price = catalog.get_product_price_by_name(TARGET_PRODUCT_NAME)

        allure.attach(
            f"Expected price: {TARGET_PRODUCT_PRICE:,} RUB\n"
            f"Actual price:   {actual_price:,} RUB\n"
            f"Filter range:   {PRICE_FROM:,}-{PRICE_TO:,} RUB",
            name="Price assertion details",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info(
            "'%s' price: %s RUB (expected within %d-%d)",
            TARGET_PRODUCT_NAME, actual_price, PRICE_FROM, PRICE_TO,
        )

        assert actual_price is not None and actual_price > 0, (
            f"Could not read price for '{TARGET_PRODUCT_NAME}' couch"
        )
        assert PRICE_FROM <= actual_price <= PRICE_TO, (
            f"'{TARGET_PRODUCT_NAME}' price {actual_price:,} RUB "
            f"is outside the filter range {PRICE_FROM:,}-{PRICE_TO:,} RUB"
        )
