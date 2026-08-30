"""
Web scraper module using BeautifulSoup for extracting links from HTML.
"""

import requests
import logging
from urllib.parse import urljoin, urlparse
from typing import Set, Optional
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)


class WebScraper:
    """
    A web scraper that extracts all href links from HTML pages.
    """

    def __init__(self, timeout: int = 10, user_agent: Optional[str] = None):
        """
        Initialize the scraper.

        Args:
            timeout: Timeout in seconds for HTTP requests
            user_agent: Custom User-Agent header (default: standard bot)
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL.

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string, or None if fetch fails
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.Timeout:
            logger.warning(f"Timeout while fetching {url}")
            return None
        except requests.ConnectionError:
            logger.warning(f"Connection error while fetching {url}")
            return None
        except requests.HTTPError as e:
            logger.warning(f"HTTP error {e.response.status_code} for {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """
        Extract all href links from HTML content.

        Args:
            html: HTML content as string
            base_url: Base URL for resolving relative links

        Returns:
            Set of absolute URLs found in the HTML
        """
        links = set()

        try:
            soup = BeautifulSoup(html, "html.parser")

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"].strip()

                # Skip empty links and fragments
                if not href or href.startswith("#"):
                    continue

                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)

                # Remove fragments from URLs
                absolute_url = absolute_url.split("#")[0]

                # Only add valid URLs
                if self._is_valid_url(absolute_url):
                    links.add(absolute_url)

        except Exception as e:
            logger.error(f"Error extracting links from {base_url}: {e}")

        return links

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        Validate if a URL is valid.

        Args:
            url: URL to validate

        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ["http", "https"], result.netloc])
        except Exception:
            return False

    def close(self):
        """Close the session."""
        self.session.close()
