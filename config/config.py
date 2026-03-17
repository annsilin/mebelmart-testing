import os

# Target site
BASE_URL: str = os.getenv("BASE_URL", "https://mebelmart-saratov.ru")

COUCHES_URL: str = os.getenv(
    "COUCHES_URL",
    f"{BASE_URL}/myagkaya_mebel_v_saratove/divanyi_v_saratove",
)

# Timeouts (milliseconds)
DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))

# Browser
BROWSER: str = os.getenv("BROWSER", "chromium")  # chromium/firefox/webkit
HEADLESS: bool = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))
WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1920"))
WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "1080"))

# Test case 2.1 parameters
FILTER_PRICE_FROM: int = int(os.getenv("FILTER_PRICE_FROM", "10000"))
FILTER_PRICE_TO: int = int(os.getenv("FILTER_PRICE_TO", "15000"))

# Output paths
SCREENSHOTS_DIR: str = os.getenv("SCREENSHOTS_DIR", "screenshots")
ALLURE_RESULTS_DIR: str = os.getenv("ALLURE_RESULTS_DIR", "allure-results")
