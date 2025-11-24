"""
Daemon mode for continuous web scraping and source discovery.

This module provides functionality to run krawl_io as a background daemon,
continuously monitoring and discovering new sources related to configured topics.
"""

import time
import signal
import sys
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional, Callable
from datetime import datetime
import json
from urllib.parse import urljoin, urlparse

from .scraper import Scraper
from .config import Config


class SourceDiscovery:
    """
    Discovers new sources by following links and filtering by topics/areas.
    """
    
    def __init__(
        self,
        topics: List[str],
        areas: Optional[List[str]] = None,
        max_depth: int = 2
    ):
        """
        Initialize source discovery.
        
        Args:
            topics: List of topics/keywords to filter sources
            areas: Optional list of geographic areas to filter
            max_depth: Maximum depth for link following (default: 2)
        """
        self.topics = [t.lower() for t in topics]
        self.areas = [a.lower() for a in areas] if areas else []
        self.max_depth = max_depth
        self.discovered_urls: Set[str] = set()
        self.logger = logging.getLogger(__name__)
    
    def is_relevant(self, text: str, url: str = "") -> bool:
        """
        Check if content is relevant based on topics and areas.
        
        Args:
            text: The text content to check
            url: The URL being analyzed
            
        Returns:
            True if content matches topics/areas
        """
        text_lower = text.lower()
        url_lower = url.lower()
        
        # Check if any topic is mentioned
        topic_match = any(topic in text_lower or topic in url_lower 
                         for topic in self.topics)
        
        # Check areas if specified
        if self.areas:
            area_match = any(area in text_lower or area in url_lower 
                           for area in self.areas)
            return topic_match and area_match
        
        return topic_match
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML content.
        
        Args:
            html: The HTML content
            base_url: The base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for tag in soup.find_all(['a', 'link'], href=True):
                href = tag.get('href', '')
                if href:
                    absolute_url = urljoin(base_url, href)
                    # Only include http/https links
                    if absolute_url.startswith(('http://', 'https://')):
                        links.append(absolute_url)
            
            return links
        except Exception as e:
            self.logger.error(f"Failed to extract links: {e}")
            return []
    
    def discover_from_url(
        self,
        url: str,
        depth: int = 0,
        visited: Optional[Set[str]] = None
    ) -> List[Dict[str, any]]:
        """
        Discover new sources starting from a URL.
        
        Args:
            url: Starting URL
            depth: Current recursion depth
            visited: Set of already visited URLs
            
        Returns:
            List of discovered source metadata
        """
        if visited is None:
            visited = set()
        
        if depth > self.max_depth or url in visited:
            return []
        
        visited.add(url)
        discovered = []
        
        try:
            scraper = Scraper(url=url)
            html = scraper.fetch()
            
            # Check if this page is relevant
            text_content = scraper.parse(html)
            full_text = ' '.join(text_content)
            
            if self.is_relevant(full_text, url):
                source_info = {
                    'url': url,
                    'discovered_at': datetime.now().isoformat(),
                    'depth': depth,
                    'title': self._extract_title(html),
                    'relevance_score': self._calculate_relevance(full_text, url)
                }
                discovered.append(source_info)
                self.discovered_urls.add(url)
                self.logger.info(f"Discovered relevant source: {url}")
            
            # Follow links if not at max depth
            if depth < self.max_depth:
                links = self.extract_links(html, url)
                # Limit links to follow to avoid explosion
                for link in links[:10]:  # Only follow first 10 links per page
                    if link not in visited:
                        time.sleep(1)  # Rate limiting
                        discovered.extend(
                            self.discover_from_url(link, depth + 1, visited)
                        )
        
        except Exception as e:
            self.logger.debug(f"Failed to process {url}: {e}")
        
        return discovered
    
    def _extract_title(self, html: str) -> str:
        """Extract page title from HTML."""
        from bs4 import BeautifulSoup
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.get_text(strip=True) if title_tag else ""
        except:
            return ""
    
    def _calculate_relevance(self, text: str, url: str) -> float:
        """Calculate relevance score (0-1) based on topic mentions."""
        text_lower = text.lower()
        url_lower = url.lower()
        
        topic_count = sum(1 for topic in self.topics 
                         if topic in text_lower or topic in url_lower)
        area_count = sum(1 for area in self.areas 
                        if area in text_lower or area in url_lower)
        
        total_keywords = len(self.topics) + len(self.areas)
        if total_keywords == 0:
            return 0.0
        
        return (topic_count + area_count) / total_keywords


class Daemon:
    """
    Daemon for continuous web scraping and source monitoring.
    """
    
    def __init__(
        self,
        config: Config,
        discovery: Optional[SourceDiscovery] = None
    ):
        """
        Initialize the daemon.
        
        Args:
            config: Configuration object
            discovery: Optional SourceDiscovery instance
        """
        self.config = config
        self.discovery = discovery
        self.running = False
        self.logger = logging.getLogger(__name__)
        self.discovered_sources: List[Dict] = []
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(
        self,
        seed_urls: List[str],
        interval: int = 3600,
        callback: Optional[Callable[[Dict], None]] = None
    ) -> None:
        """
        Start the daemon.
        
        Args:
            seed_urls: Initial URLs to start discovery from
            interval: Time between scraping cycles in seconds (default: 1 hour)
            callback: Optional callback function for each discovered source
        """
        self.running = True
        self.logger.info("Starting krawl_io daemon...")
        
        cycle = 0
        while self.running:
            cycle += 1
            self.logger.info(f"Starting scraping cycle #{cycle}")
            
            try:
                # Discover new sources
                if self.discovery:
                    for seed_url in seed_urls:
                        self.logger.info(f"Discovering from: {seed_url}")
                        new_sources = self.discovery.discover_from_url(seed_url)
                        
                        for source in new_sources:
                            if source['url'] not in [s['url'] for s in self.discovered_sources]:
                                self.discovered_sources.append(source)
                                self.logger.info(
                                    f"New source: {source['url']} "
                                    f"(relevance: {source.get('relevance_score', 0):.2f})"
                                )
                                
                                # Call callback if provided
                                if callback:
                                    callback(source)
                
                # Save discovered sources
                self._save_sources()
                
                self.logger.info(
                    f"Cycle #{cycle} complete. "
                    f"Total sources: {len(self.discovered_sources)}"
                )
                
                # Wait for next cycle
                if self.running:
                    self.logger.info(f"Sleeping for {interval} seconds...")
                    time.sleep(interval)
            
            except Exception as e:
                self.logger.error(f"Error in daemon cycle: {e}")
                if self.config.get('daemon_stop_on_error', False):
                    self.stop()
                else:
                    time.sleep(60)  # Wait a minute before retry
    
    def stop(self) -> None:
        """Stop the daemon."""
        self.running = False
        self._save_sources()
        self.logger.info("Daemon stopped.")
    
    def _save_sources(self) -> None:
        """Save discovered sources to file."""
        output_file = Path(self.config.get('daemon_output', 'discovered_sources.json'))
        
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(self.discovered_sources, f, indent=2)
            self.logger.debug(f"Saved {len(self.discovered_sources)} sources to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save sources: {e}")
    
    def get_status(self) -> Dict[str, any]:
        """
        Get daemon status information.
        
        Returns:
            Dictionary with status information
        """
        return {
            'running': self.running,
            'discovered_sources': len(self.discovered_sources),
            'unique_urls': len(set(s['url'] for s in self.discovered_sources))
        }
