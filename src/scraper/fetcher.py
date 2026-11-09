"""HTTP request fetcher implementing custom headers, rate limiting, and retry logic."""

import logging
import time
from typing import Optional
requests = None
try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


class WebFetcher:
    """Fetches web pages with polite rate limiting and retry mechanisms."""

    def __init__(self, retries: int = 3, backoff_factor: float = 1.0, delay: float = 0.5) -> None:
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.delay = delay
        self.session = requests.Session() if requests else None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def fetch(self, url: str) -> Optional[str]:
        if not self.session:
            raise RuntimeError("requests library is not installed.")
        
        # Polite rate limiting delay
        time.sleep(self.delay)

        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
                logger.warning("Attempt %d: Received status code %d for %s", attempt, response.status_code, url)
            except requests.RequestException as exc:
                logger.warning("Attempt %d failed for %s: %s", attempt, url, exc)

            if attempt < self.retries:
                sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                time.sleep(sleep_time)

        logger.error("Failed to fetch %s after %d attempts.", url, self.retries)
        return None
