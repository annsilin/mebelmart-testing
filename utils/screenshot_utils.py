"""
utils/screenshot_utils.py
-------------------------
Screenshot utility module.

Used by conftest.py to capture and attach screenshots on test failure:
    - save_screenshot  - writes a full-page PNG to SCREENSHOTS_DIR
    - attach_to_allure - attaches PNG bytes to the current Allure report
    - take_screenshot  - returns raw PNG bytes without saving to disk
"""

import logging
import os
from datetime import datetime

import allure
from playwright.sync_api import Page

from config.config import SCREENSHOTS_DIR

logger = logging.getLogger(__name__)


def take_screenshot(page: Page) -> bytes:
    """
    Capture a full-page screenshot and return raw PNG bytes.

    Args:
        page: Active Playwright Page instance.

    Returns:
        PNG image as bytes.
    """
    return page.screenshot(full_page=True)


def save_screenshot(page: Page, test_name: str) -> str:
    """
    Save a full-page screenshot to SCREENSHOTS_DIR.

    The filename is derived from the test node id and a timestamp
    to avoid collisions between runs.

    Args:
        page:      Active Playwright Page instance.
        test_name: Test identifier used as part of the filename.

    Returns:
        Absolute path to the saved PNG file.
    """
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
    filepath = os.path.join(SCREENSHOTS_DIR, f"{safe_name}_{timestamp}.png")

    page.screenshot(path=filepath, full_page=True)
    logger.info("Screenshot saved: %s", filepath)
    return filepath


def attach_to_allure(page: Page, name: str = "Screenshot on failure") -> None:
    """
    Attach a full-page PNG screenshot to the current Allure report step.

    Args:
        page: Active Playwright Page instance.
        name: Attachment label shown in the Allure report.
    """
    try:
        png_bytes = take_screenshot(page)
        allure.attach(
            png_bytes,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
        logger.debug("Screenshot attached to Allure: '%s'", name)
    except Exception as exc:
        logger.warning("Failed to attach screenshot to Allure: %s", exc)
