"""
tests/test_search.py
---------------------
Test scenario 2.4: Search for a product by name.

Steps:
    1. Open the couches catalog.
    2. Type "Чебурашка" into the search input and press Enter.
    3. Verify the results page loaded correctly.
    4. Verify the first result contains the search query in its name.

Expected result:
    The first product in search results has "Чебурашка" in its name.
"""

import logging

import allure
import pytest

from pages.couches_catalog_page import CouchesCatalogPage
from pages.search_results_page import SearchResultsPage

logger = logging.getLogger(__name__)

SEARCH_QUERY = "Чебурашка"


@allure.feature("Search")
@allure.story("Search by product name")
@allure.title(
    f"Scenario 2.4: Search for '{SEARCH_QUERY}' - "
    "first result contains the search term"
)
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.regression
def test_search_by_name_returns_matching_product(page):
    """Scenario 2.4: Product search by name."""
    catalog = CouchesCatalogPage(page)
    search = SearchResultsPage(page)

    # Open the couches catalog (search input is in the page header)
    with allure.step("Step 1: Open the couches catalog"):
        catalog.open_catalog()
        assert catalog.is_catalog_loaded(), "Couches catalog page did not load"

    # Type the query and submit via Enter
    with allure.step(f"Step 2: Search for '{SEARCH_QUERY}'"):
        search.search(SEARCH_QUERY)

    # Verify the search results page loaded
    with allure.step("Step 3: Verify the search results page loaded"):
        assert search.is_loaded(), "Search results page did not load"

        heading = search.get_heading()
        items_text = search.get_items_count_text()

        allure.attach(
            f"Heading:  {heading}\n"
            f"Summary:  {items_text}\n"
            f"URL:      {search.current_url}",
            name="Search results page info",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("Search results loaded - heading: '%s', summary: '%s'",
                    heading, items_text)

        assert SEARCH_QUERY.lower() in heading.lower(), (
            f"Search heading does not mention '{SEARCH_QUERY}': '{heading}'"
        )

    # Verify the first result contains the search query
    with allure.step(
            f"Step 4: Verify the first result contains '{SEARCH_QUERY}'"
    ):
        first_name = search.get_first_product_name()
        all_names = search.get_product_names()

        allure.attach(
            f"First result: {first_name}\n"
            f"All results:\n" + "\n".join(f"  - {n}" for n in all_names),
            name="Search results",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("First result: '%s'", first_name)

        assert first_name is not None, "No products found in search results"
        assert SEARCH_QUERY.lower() in first_name.lower(), (
            f"First result '{first_name}' does not contain '{SEARCH_QUERY}'"
        )
