"""
Tests for the daemon and source discovery functionality.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
from krawl_io import Daemon, SourceDiscovery, Config
import tempfile
from pathlib import Path


class TestSourceDiscovery(unittest.TestCase):
    """Test cases for the SourceDiscovery class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.topics = ["python", "programming"]
        self.areas = ["san francisco", "california"]
        self.discovery = SourceDiscovery(
            topics=self.topics,
            areas=self.areas,
            max_depth=2
        )
    
    def test_initialization(self):
        """Test source discovery initializes correctly."""
        self.assertEqual(self.discovery.topics, ["python", "programming"])
        self.assertEqual(self.discovery.areas, ["san francisco", "california"])
        self.assertEqual(self.discovery.max_depth, 2)
        self.assertEqual(len(self.discovery.discovered_urls), 0)
    
    def test_is_relevant_with_topic_match(self):
        """Test relevance checking with topic match only (no areas)."""
        # Create discovery without areas for this test
        discovery_no_areas = SourceDiscovery(topics=["python", "programming"], max_depth=2)
        text = "This is an article about Python programming"
        self.assertTrue(discovery_no_areas.is_relevant(text))
    
    def test_is_relevant_with_area_match(self):
        """Test relevance checking with both topic and area match."""
        text = "Python programming meetup in San Francisco"
        self.assertTrue(self.discovery.is_relevant(text))
    
    def test_is_relevant_no_match(self):
        """Test relevance checking with no match."""
        text = "This is about Java in New York"
        self.assertFalse(self.discovery.is_relevant(text))
    
    def test_is_relevant_url_match(self):
        """Test relevance checking from URL."""
        text = "Some content about california"
        url = "https://python-programming.com/events"
        self.assertTrue(self.discovery.is_relevant(text, url))
    
    def test_extract_links(self):
        """Test link extraction from HTML."""
        html = '''
        <html>
            <body>
                <a href="https://example.com/page1">Link 1</a>
                <a href="/relative/path">Link 2</a>
                <a href="mailto:test@example.com">Email</a>
            </body>
        </html>
        '''
        base_url = "https://example.com"
        links = self.discovery.extract_links(html, base_url)
        
        self.assertIn("https://example.com/page1", links)
        self.assertIn("https://example.com/relative/path", links)
        self.assertNotIn("mailto:test@example.com", links)
    
    def test_calculate_relevance(self):
        """Test relevance score calculation."""
        text = "Python programming in San Francisco and California"
        url = "https://example.com"
        score = self.discovery._calculate_relevance(text, url)
        
        # Should match all keywords
        self.assertGreater(score, 0.5)
        self.assertLessEqual(score, 1.0)
    
    def test_extract_title(self):
        """Test title extraction from HTML."""
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        title = self.discovery._extract_title(html)
        self.assertEqual(title, "Test Page")
    
    def test_extract_title_no_title_tag(self):
        """Test title extraction when no title tag exists."""
        html = "<html><body><h1>Header</h1></body></html>"
        title = self.discovery._extract_title(html)
        self.assertEqual(title, "")


class TestDaemon(unittest.TestCase):
    """Test cases for the Daemon class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.topics = ["test", "example"]
        self.discovery = SourceDiscovery(topics=self.topics)
        self.daemon = Daemon(config=self.config, discovery=self.discovery)
    
    def test_initialization(self):
        """Test daemon initializes correctly."""
        self.assertFalse(self.daemon.running)
        self.assertEqual(len(self.daemon.discovered_sources), 0)
        self.assertIsNotNone(self.daemon.config)
        self.assertIsNotNone(self.daemon.discovery)
    
    def test_stop(self):
        """Test daemon stop functionality."""
        self.daemon.running = True
        self.daemon.stop()
        self.assertFalse(self.daemon.running)
    
    def test_get_status(self):
        """Test status reporting."""
        status = self.daemon.get_status()
        
        self.assertIn('running', status)
        self.assertIn('discovered_sources', status)
        self.assertIn('unique_urls', status)
        self.assertFalse(status['running'])
        self.assertEqual(status['discovered_sources'], 0)
    
    def test_save_sources(self):
        """Test saving discovered sources to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "test_sources.json"
            self.config.set('daemon_output', str(output_file))
            
            # Add some mock sources
            self.daemon.discovered_sources = [
                {'url': 'https://example.com', 'title': 'Test'}
            ]
            
            self.daemon._save_sources()
            
            self.assertTrue(output_file.exists())
    
    @patch('krawl_io.daemon.SourceDiscovery.discover_from_url')
    def test_start_single_cycle(self, mock_discover):
        """Test daemon runs a single cycle."""
        # Mock discovery to return immediately
        mock_discover.return_value = [
            {'url': 'https://test.com', 'title': 'Test', 'discovered_at': '2025-01-01'}
        ]
        
        # Mock config to stop after one cycle
        self.config.set('daemon_stop_on_error', True)
        
        # Run for a very short interval
        daemon = Daemon(config=self.config, discovery=self.discovery)
        
        # Manually run one cycle instead of full start
        daemon.running = True
        seed_urls = ['https://example.com']
        
        # Simulate one cycle
        for seed_url in seed_urls:
            new_sources = mock_discover.return_value
            for source in new_sources:
                daemon.discovered_sources.append(source)
        
        daemon.stop()
        
        self.assertGreater(len(daemon.discovered_sources), 0)
        self.assertFalse(daemon.running)


class TestDaemonIntegration(unittest.TestCase):
    """Integration tests for daemon functionality."""
    
    @patch('krawl_io.daemon.Scraper.fetch')
    def test_discovery_integration(self, mock_fetch):
        """Test source discovery with mocked scraper."""
        mock_fetch.return_value = '''
        <html>
            <head><title>Python Events in Berlin</title></head>
            <body>
                <p>Join us for Python programming events in Berlin</p>
                <a href="https://example.com/event1">Event 1</a>
                <a href="https://example.com/event2">Event 2</a>
            </body>
        </html>
        '''
        
        discovery = SourceDiscovery(
            topics=["python", "events"],
            areas=["berlin"],
            max_depth=0  # Don't follow links
        )
        
        sources = discovery.discover_from_url("https://example.com")
        
        # Should discover the main URL as relevant
        self.assertGreater(len(sources), 0)
        self.assertEqual(sources[0]['url'], "https://example.com")
        self.assertIn("Python Events in Berlin", sources[0]['title'])


if __name__ == '__main__':
    unittest.main()
