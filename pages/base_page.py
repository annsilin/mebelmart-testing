"""
pages/base_page.py
------------------
Page Layer - base Page Object class.
"""

import logging

import allure
from playwright.sync_api import Page

from config.config import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all Page Objects.

    Attributes:
        page: Active Playwright Page instance.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    # Navigation
    @allure.step("Navigate to: {url}")
    def open(self, url: str) -> "BasePage":
        """Navigate to the given URL and wait for the load event."""
        logger.info("Navigating to: %s", url)
        self.page.goto(url, wait_until="load")
        return self

    # Element access
    def locator(self, selector: str):
        """Return a Locator for the given CSS selector."""
        return self.page.locator(selector)

    def xpath(self, expression: str):
        """Return a Locator for the given XPath expression."""
        return self.page.locator(f"xpath={expression}")

    # Explicit waits
    def wait_for_selector(self, selector: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Wait for an element matching the selector to appear in the DOM."""
        self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_url(self, pattern: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Wait until the current URL matches the given string or pattern."""
        self.page.wait_for_url(pattern, timeout=timeout)

    def wait_for_load_state(self, state: str = "load") -> None:
        """Wait for the page to reach the specified load state."""
        self.page.wait_for_load_state(state)

    # Page metadata
    @property
    def title(self) -> str:
        """Return the current page title."""
        return self.page.title()

    @property
    def current_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    # Scroll
    def scroll_to_bottom(self) -> None:
        """Scroll the page to the very bottom."""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def scroll_to_center(self, locator) -> None:
        """Scroll the page so the element is centred in the viewport."""
        try:
            locator.first.evaluate(
                "el => el.scrollIntoView({ behavior: 'smooth', block: 'center' })"
            )
        except Exception as exc:
            logger.debug("scroll_to_center() skipped: %s", exc)