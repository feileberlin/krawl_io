"""
Core web scraping functionality for krawl_io.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import logging


class Scraper:
    """
    Main scraper class that handles web page fetching and parsing.
    
    Attributes:
        url (str): The URL to scrape
        timeout (int): Request timeout in seconds
        headers (dict): HTTP headers to use for requests
    """
    
    def __init__(
        self,
        url: str,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the Scraper.
        
        Args:
            url: The target URL to scrape
            timeout: Request timeout in seconds (default: 30)
            headers: Optional HTTP headers dictionary
        """
        self.url = url
        self.timeout = timeout
        self.headers = headers or {
            'User-Agent': 'krawl_io/0.1.0 (Web Scraping Library)'
        }
        self.logger = logging.getLogger(__name__)
    
    def fetch(self) -> str:
        """
        Fetch the HTML content from the URL.
        
        Returns:
            The HTML content as a string
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            self.logger.info(f"Fetching URL: {self.url}")
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            self.logger.info(f"Successfully fetched {len(response.text)} characters")
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch URL: {e}")
            raise
    
    def parse(self, html: str, selector: Optional[str] = None) -> List[str]:
        """
        Parse HTML content and extract text.
        
        Args:
            html: The HTML content to parse
            selector: Optional CSS selector to filter elements
            
        Returns:
            List of extracted text strings
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            if selector:
                elements = soup.select(selector)
                self.logger.info(f"Found {len(elements)} elements matching '{selector}'")
                return [elem.get_text(strip=True) for elem in elements]
            else:
                # Extract all text if no selector specified
                text = soup.get_text(strip=True)
                return [text] if text else []
                
        except Exception as e:
            self.logger.error(f"Failed to parse HTML: {e}")
            raise
    
    def scrape(self, selector: Optional[str] = None) -> List[str]:
        """
        Fetch and parse the URL in one operation.
        
        Args:
            selector: Optional CSS selector to filter elements
            
        Returns:
            List of extracted text strings
            
        Raises:
            requests.RequestException: If fetching fails
            Exception: If parsing fails
        """
        html = self.fetch()
        return self.parse(html, selector)
