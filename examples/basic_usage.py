"""
Example usage of krawl_io library.

This script demonstrates how to use the krawl_io library
to scrape web content programmatically.
"""

from krawl_io import Scraper, Config
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

def example_basic_scraping():
    """Example: Basic web scraping"""
    print("\n=== Example 1: Basic Scraping ===")
    
    # Create a scraper for a URL
    scraper = Scraper(url="https://example.com")
    
    # Fetch and parse the page
    results = scraper.scrape()
    
    print(f"Extracted {len(results)} text blocks")
    for i, text in enumerate(results[:3], 1):  # Show first 3 results
        print(f"\nBlock {i}:")
        print(text[:200] + "..." if len(text) > 200 else text)


def example_with_selector():
    """Example: Scraping with CSS selector"""
    print("\n=== Example 2: Using CSS Selectors ===")
    
    # Scrape only specific elements using a CSS selector
    scraper = Scraper(url="https://example.com")
    
    # Extract only paragraph text
    results = scraper.scrape(selector="p")
    
    print(f"Found {len(results)} paragraphs")
    for i, text in enumerate(results[:3], 1):
        print(f"\nParagraph {i}: {text}")


def example_with_config():
    """Example: Using configuration"""
    print("\n=== Example 3: Using Configuration ===")
    
    # Create a configuration
    config = Config()
    config.set("timeout", 60)
    config.set("max_retries", 5)
    
    # Use configuration with scraper
    scraper = Scraper(
        url="https://example.com",
        timeout=config.get("timeout")
    )
    
    print(f"Using timeout: {config.get('timeout')} seconds")
    results = scraper.scrape()
    print(f"Scraped successfully with {len(results)} results")


def example_error_handling():
    """Example: Error handling"""
    print("\n=== Example 4: Error Handling ===")
    
    try:
        # Try to scrape an invalid URL
        scraper = Scraper(url="https://invalid-url-that-does-not-exist-12345.com")
        results = scraper.scrape()
    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")
        print("This demonstrates proper error handling in krawl_io")


if __name__ == "__main__":
    print("krawl_io Library Examples")
    print("=" * 60)
    
    # Note: These examples use example.com which is a real domain
    # In production, you should respect robots.txt and rate limits
    
    try:
        example_basic_scraping()
        example_with_selector()
        example_with_config()
        example_error_handling()
    except Exception as e:
        print(f"\nExample execution error: {e}")
        print("This may be due to network connectivity issues.")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
