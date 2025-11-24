"""
krawl_io - A web scraping package with an accessible interface.

This package provides robust web scraping capabilities with an easy-to-use
command-line interface designed for accessibility.
"""

__version__ = "0.1.0"
__author__ = "krawl_io contributors"

from .scraper import Scraper
from .config import Config
from .daemon import Daemon, SourceDiscovery

__all__ = ["Scraper", "Config", "Daemon", "SourceDiscovery"]
