"""
tests/test_product_details.py
------------------------------
Test scenario 2.2: Product card detail verification.

Steps:
    1. Open the couches catalog.
    2. Find "Диван Шенилл" in the product listing.
    3. Read its dimensions (width, depth) from the catalog card.
    4. Click the product to open its detail page.
    5. Click the "Характеристики" (Characteristics) tab.
    6. Read width and depth from the characteristics table.
    7. Assert that both values match what was shown in the catalog card.

Expected result:
    The detail page opened for the correct product, and the dimension values
    in the Characteristics tab match those displayed on the catalog card.
"""

import logging

import allure
import pytest

from pages.couches_catalog_page import CouchesCatalogPage
from pages.product_page import ProductPage

logger = logging.getLogger(__name__)

TARGET_PRODUCT_NAME = "Шенилл"

DIMENSION_WIDTH_KEY = "Ширина"
DIMENSION_DEPTH_KEY = "Глубина"


@allure.feature("Product details")
@allure.story("Characteristics tab")
@allure.title(
    f"Scenario 2.2: '{TARGET_PRODUCT_NAME}' catalog card dimensions "
    "match the Characteristics tab on the product page"
)
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_product_details_match_catalog_card(page):
    """
    Scenario 2.2: Verify that dimensions shown in the catalog card
    are consistent with the Characteristics tab on the product detail page.
    """
    catalog = CouchesCatalogPage(page)
    product = ProductPage(page)

    # Open the couches catalog
    with allure.step("Step 1: Open the couches catalog"):
        catalog.open_catalog()
        assert catalog.is_catalog_loaded(), "Couches catalog page did not load"
        logger.info("Catalog loaded: %s", catalog.current_url)

    # Find the target product card
    with allure.step(f"Step 2: Find '{TARGET_PRODUCT_NAME}' in the catalog listing"):
        card = catalog.find_product_by_name(TARGET_PRODUCT_NAME)
        if card is None:
            pytest.fail(
                f"Product '{TARGET_PRODUCT_NAME}' was not found in the catalog"
            )
        logger.info("Product '%s' found in catalog", TARGET_PRODUCT_NAME)

    # Read dimensions from the catalog card
    with allure.step(f"Step 3: Read dimensions from the '{TARGET_PRODUCT_NAME}' catalog card"):
        catalog_dims = catalog.get_catalog_card_dimensions(TARGET_PRODUCT_NAME)
        allure.attach(
            "\n".join(f"{k}: {v} мм" for k, v in catalog_dims.items()),
            name="Dimensions from catalog card",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("Catalog card dimensions: %s", catalog_dims)

        assert DIMENSION_WIDTH_KEY in catalog_dims, (
            f"Width ('{DIMENSION_WIDTH_KEY}') not found in catalog card dimensions: {catalog_dims}"
        )
        assert DIMENSION_DEPTH_KEY in catalog_dims, (
            f"Depth ('{DIMENSION_DEPTH_KEY}') not found in catalog card dimensions: {catalog_dims}"
        )

        catalog_width = catalog_dims[DIMENSION_WIDTH_KEY]
        catalog_depth = catalog_dims[DIMENSION_DEPTH_KEY]

    # Navigate to the product detail page
    with allure.step(f"Step 4: Open '{TARGET_PRODUCT_NAME}' product detail page"):
        product_url = catalog.get_product_link_by_name(TARGET_PRODUCT_NAME)
        assert product_url, f"Could not resolve product URL for '{TARGET_PRODUCT_NAME}'"

        catalog.open(product_url)
        assert product.is_product_page(), "Product detail page did not load"

        page_title = product.get_product_title()
        allure.attach(
            page_title,
            name="Product page title",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("Product page opened: '%s'", page_title)

        assert TARGET_PRODUCT_NAME.lower() in page_title.lower(), (
            f"Expected '{TARGET_PRODUCT_NAME}' in page title, got: '{page_title}'"
        )

    # Open the Characteristics tab
    with allure.step("Step 5: Click the 'Характеристики' tab"):
        product.open_characteristics_tab()

    # Read dimensions from the characteristics table
    with allure.step("Step 6: Read dimensions from the Characteristics table"):
        page_width = product.get_characteristic_value(DIMENSION_WIDTH_KEY)
        page_depth = product.get_characteristic_value(DIMENSION_DEPTH_KEY)

        allure.attach(
            f"{DIMENSION_WIDTH_KEY}: {page_width} мм\n"
            f"{DIMENSION_DEPTH_KEY}: {page_depth} мм",
            name="Dimensions from Characteristics tab",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info(
            "Characteristics tab - width: %s, depth: %s", page_width, page_depth
        )

        assert page_width is not None, (
            f"'{DIMENSION_WIDTH_KEY}' not found in Characteristics tab"
        )
        assert page_depth is not None, (
            f"'{DIMENSION_DEPTH_KEY}' not found in Characteristics tab"
        )

    # Assert catalog card values match the product page
    with allure.step(
            "Step 7: Assert catalog card dimensions match the Characteristics tab"
    ):
        allure.attach(
            f"Catalog card  - {DIMENSION_WIDTH_KEY}: {catalog_width} мм, "
            f"{DIMENSION_DEPTH_KEY}: {catalog_depth} мм\n"
            f"Product page  - {DIMENSION_WIDTH_KEY}: {page_width} мм, "
            f"{DIMENSION_DEPTH_KEY}: {page_depth} мм",
            name="Dimension comparison",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert catalog_width == page_width, (
            f"Width mismatch: catalog card shows {catalog_width} мм, "
            f"Characteristics tab shows {page_width} мм"
        )
        assert catalog_depth == page_depth, (
            f"Depth mismatch: catalog card shows {catalog_depth} мм, "
            f"Characteristics tab shows {page_depth} мм"
        )

        logger.info(
            "Dimensions match - width: %s мм, depth: %s мм", catalog_width, catalog_depth
        )
