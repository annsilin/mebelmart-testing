"""
drivers/driver_factory.py
-------------------------
Driver / Infrastructure Layer.

Supported browsers:
    chromium
    firefox
    webkit
"""

import logging

from playwright.sync_api import Browser, BrowserContext, Playwright

from config.config import (
    DEFAULT_TIMEOUT,
    HEADLESS,
    NAVIGATION_TIMEOUT,
    SLOW_MO,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)

logger = logging.getLogger(__name__)

SUPPORTED_BROWSERS = ("chromium", "firefox", "webkit")


def create_browser(
        playwright: Playwright,
        browser: str = "chromium",
        headless: bool = HEADLESS,
) -> Browser:
    """
    Launch and return a Browser instance.

    Args:
        playwright: Playwright instance provided by pytest-playwright.
        browser:    Browser engine identifier - "chromium", "firefox", or "webkit".
        headless:   Whether to run the browser without a visible window.

    Returns:
        Launched Browser instance.

    Raises:
        ValueError: If an unsupported browser identifier is given.
    """
    browser = browser.lower().strip()
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError(
            f"Unsupported browser: '{browser}'. Supported: {SUPPORTED_BROWSERS}"
        )

    logger.info("Launching browser: %s (headless=%s)", browser, headless)

    launch_kwargs = dict(headless=headless, slow_mo=SLOW_MO)

    if browser == "chromium":
        return playwright.chromium.launch(**launch_kwargs)
    elif browser == "firefox":
        return playwright.firefox.launch(**launch_kwargs)
    else:
        return playwright.webkit.launch(**launch_kwargs)


def create_context(browser: Browser) -> BrowserContext:
    """
    Create and return an isolated BrowserContext.

    Each context has its own cookies, localStorage, and session storage,
    ensuring complete test isolation without shared state between tests.

    Args:
        browser: A running Browser instance.

    Returns:
        Configured BrowserContext ready for use.
    """
    context = browser.new_context(
        viewport={"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT},
        locale="ru-RU",
    )
    context.set_default_timeout(DEFAULT_TIMEOUT)
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

    logger.debug("BrowserContext created: viewport=%dx%d", WINDOW_WIDTH, WINDOW_HEIGHT)
    return context
