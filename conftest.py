"""
conftest.py
-----------
Test Infrastructure Layer - Playwright + pytest.

Usage examples:
    pytest                              # headless Chromium (default)
    pytest --browser=firefox            # Firefox
    pytest --browser=webkit             # WebKit (Safari engine)
    pytest --headed                     # run with a visible browser window
    pytest --browser=chromium --headed  # visible Chromium
"""

import logging
import os

import allure
import pytest

from config.config import (
    DEFAULT_TIMEOUT,
    NAVIGATION_TIMEOUT,
    SCREENSHOTS_DIR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from utils.screenshot_utils import attach_to_allure, save_screenshot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("conftest")


# Browser configuration

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Override default BrowserContext arguments for the entire session."""
    return {
        **browser_context_args,
        "viewport": {"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT},
        "locale": "ru-RU",
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    """
    Override browser launch arguments for the entire session.
    Headless mode is controlled by the --headed CLI flag.
    """
    return {
        **browser_type_launch_args,
        "slow_mo": 0,
    }


@pytest.fixture(autouse=True)
def set_timeouts(page) -> None:
    """Apply project default timeouts to every page before each test."""
    page.set_default_timeout(DEFAULT_TIMEOUT)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)


# Failure handling

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """
    Post-test hook that captures a screenshot when a test fails.

    Executed after every test phase (setup / call / teardown).
    Only acts on the `call` phase to avoid duplicate screenshots.

    On failure:
        1. Saves a full-page PNG to SCREENSHOTS_DIR.
        2. Attaches the PNG to the Allure report.
        3. Attaches the current URL and page title as text artifacts.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        pw_page = item.funcargs.get("page")
        if pw_page is None:
            return

        test_name = item.nodeid.replace("::", "__").replace("/", "_")
        screenshot_path = save_screenshot(pw_page, test_name)
        logger.error("Test failed. Screenshot: %s", screenshot_path)

        attach_to_allure(pw_page, name=f"FAIL: {item.name}")

        with allure.step("Browser state at the point of failure"):
            allure.attach(
                pw_page.url,
                name="URL on failure",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                pw_page.title(),
                name="Page title",
                attachment_type=allure.attachment_type.TEXT,
            )


# Session setup

@pytest.fixture(scope="session", autouse=True)
def _setup_directories() -> None:
    """Create required output directories before the test session begins."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs("allure-results", exist_ok=True)
    logger.info("Output directories ready.")
