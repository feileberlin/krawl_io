"""
Tests for the krawl_io package.
"""

import unittest
from unittest.mock import patch, Mock
from krawl_io import Scraper, Config
from pathlib import Path
import tempfile
import json


class TestScraper(unittest.TestCase):
    """Test cases for the Scraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_url = "https://example.com"
        self.scraper = Scraper(url=self.test_url)
    
    def test_scraper_initialization(self):
        """Test scraper initializes with correct attributes."""
        self.assertEqual(self.scraper.url, self.test_url)
        self.assertEqual(self.scraper.timeout, 30)
        self.assertIsNotNone(self.scraper.headers)
    
    def test_scraper_custom_timeout(self):
        """Test scraper with custom timeout."""
        scraper = Scraper(url=self.test_url, timeout=60)
        self.assertEqual(scraper.timeout, 60)
    
    def test_scraper_custom_headers(self):
        """Test scraper with custom headers."""
        headers = {'User-Agent': 'CustomAgent/1.0'}
        scraper = Scraper(url=self.test_url, headers=headers)
        self.assertEqual(scraper.headers, headers)
    
    @patch('krawl_io.scraper.requests.get')
    def test_fetch_success(self, mock_get):
        """Test successful fetch operation."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch()
        
        self.assertEqual(result, "<html><body>Test</body></html>")
        mock_get.assert_called_once()
    
    @patch('krawl_io.scraper.requests.get')
    def test_fetch_failure(self, mock_get):
        """Test fetch operation with network error."""
        mock_get.side_effect = Exception("Network error")
        
        with self.assertRaises(Exception):
            self.scraper.fetch()
    
    def test_parse_html(self):
        """Test HTML parsing."""
        html = "<html><body><p>Test paragraph</p></body></html>"
        results = self.scraper.parse(html, selector="p")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "Test paragraph")
    
    def test_parse_html_no_selector(self):
        """Test HTML parsing without selector."""
        html = "<html><body><p>Test</p></body></html>"
        results = self.scraper.parse(html)
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""
    
    def test_config_initialization(self):
        """Test config initializes with defaults."""
        config = Config()
        self.assertEqual(config.get('timeout'), 30)
        self.assertIsNotNone(config.get('user_agent'))
    
    def test_config_get_set(self):
        """Test getting and setting configuration values."""
        config = Config()
        config.set('custom_key', 'custom_value')
        
        self.assertEqual(config.get('custom_key'), 'custom_value')
    
    def test_config_get_default(self):
        """Test getting with default value."""
        config = Config()
        result = config.get('nonexistent', 'default')
        
        self.assertEqual(result, 'default')
    
    def test_config_save_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            
            # Create and save config
            config1 = Config()
            config1.set('test_key', 'test_value')
            config1.save(config_path)
            
            # Load into new config
            config2 = Config(config_path)
            
            self.assertEqual(config2.get('test_key'), 'test_value')
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        config.set('custom', 'value')
        
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['custom'], 'value')


if __name__ == '__main__':
    unittest.main()
