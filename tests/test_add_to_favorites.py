"""
tests/test_add_to_favorites.py
-------------------------------
Test scenario 2.3: Add product to favorites.

Steps:
    1. Open the couches catalog.
    2. Click the favorite icon on the first product card.
    3. Verify the icon changes to the active (filled) state.
    4. Navigate to the favorites page via the header link.
    5. Verify the product appears in the favorites list.

Expected result:
    The selected couch is displayed on the favorites page, and its
    favorite icon in the catalog is in the active state.
"""

import logging

import allure
import pytest

from pages.couches_catalog_page import CouchesCatalogPage
from pages.favorites_page import FavoritesPage

logger = logging.getLogger(__name__)


@allure.feature("Favorites")
@allure.story("Add to favorites")
@allure.title("Scenario 2.3: First catalog product can be added to favorites")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_add_first_product_to_favorites(page):
    """
    Scenario 2.3: Add the first product in the catalog to favorites
    and verify it appears on the favorites page.

    Postcondition:
        Removes the product from favorites to restore initial state.
    """
    catalog = CouchesCatalogPage(page)
    favorites = FavoritesPage(page)

    # Open the couches catalog
    with allure.step("Step 1: Open the couches catalog"):
        catalog.open_catalog()
        assert catalog.is_catalog_loaded(), "Couches catalog page did not load"

    # Identify the first product and click its favorite icon
    with allure.step("Step 2: Click the favorite icon on the first product card"):
        product_name = catalog.get_first_product_name()
        assert product_name, "Could not read the first product name from the catalog"

        allure.attach(
            product_name,
            name="Target product",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("Adding to favorites: '%s'", product_name)

        catalog.click_favorite_icon(product_name)

    # Verify the icon changed to active state
    with allure.step("Step 3: Verify the favorite icon is now active (filled)"):
        is_active = catalog.is_favorite_icon_active(product_name)
        allure.attach(
            f"Icon active: {is_active}",
            name="Favorite icon state",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert is_active, (
            f"Favorite icon did not become active after clicking for '{product_name}'"
        )
        logger.info("Favorite icon is active for '%s'", product_name)

    # Navigate to the favorites page
    with allure.step("Step 4: Navigate to the favorites page via the header link"):
        catalog.navigate_to_favorites()
        assert favorites.is_loaded(), "Favorites page did not load"
        logger.info("Favorites page loaded: %s", favorites.current_url)

    # Verify the product is in the favorites list
    with allure.step(f"Step 5: Verify '{product_name}' appears in the favorites list"):
        # is_product_in_favorites() matches by model name only (prefix stripped).
        model_name = favorites._model_name(product_name)
        found = favorites.is_product_in_favorites(product_name)

        items_text = favorites.get_items_count_text()
        product_names = favorites.get_product_names()

        allure.attach(
            f"Catalog name:  {product_name}\n"
            f"Model name:    {model_name}\n"
            f"Summary:       {items_text}\n"
            f"Products in favorites: {product_names}",
            name="Favorites page content",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("Looking for model '%s' in favorites: %s", model_name, product_names)

        assert found, (
            f"Model '{model_name}' (from '{product_name}') was not found on the favorites page. "
            f"Products present: {product_names}"
        )

    # Postcondition: remove from favorites to restore initial state
    with allure.step("Postcondition: remove product from favorites (cleanup)"):
        # Navigate back to catalog and click the icon again to deactivate it
        catalog.open_catalog()
        catalog.click_favorite_icon(product_name)
        logger.info("'%s' removed from favorites (cleanup)", product_name)