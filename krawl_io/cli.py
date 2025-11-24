"""
Command-line interface for krawl_io with accessibility features.

This module provides an accessible CLI for interacting with the krawl_io
web scraping functionality.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from .scraper import Scraper
from .config import Config


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging with accessible output format.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='[%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def create_parser() -> argparse.ArgumentParser:
    """
    Create an argument parser with detailed help text for accessibility.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='krawl_io',
        description='krawl_io - Accessible web scraping tool',
        epilog='For more information, visit: https://github.com/feileberlin/krawl_io',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        'url',
        type=str,
        help='URL to scrape (required)'
    )
    
    # Optional arguments
    parser.add_argument(
        '-s', '--selector',
        type=str,
        help='CSS selector to filter elements (optional)',
        metavar='SELECTOR'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (default: print to stdout)',
        metavar='FILE'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)',
        metavar='SECONDS'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file (JSON format)',
        metavar='FILE'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (DEBUG level)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress all output except errors'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='krawl_io 0.1.0'
    )
    
    return parser


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging based on verbosity flags
    if args.quiet:
        log_level = 'ERROR'
    elif args.verbose:
        log_level = 'DEBUG'
    else:
        log_level = 'INFO'
    
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration if provided
        config = None
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                logger.error(f"Configuration file not found: {args.config}")
                return 1
            config = Config(config_path)
            logger.info(f"Loaded configuration from {args.config}")
        
        # Create scraper instance
        timeout = args.timeout
        if config:
            timeout = config.get('timeout', timeout)
        
        logger.info(f"Starting scrape of: {args.url}")
        scraper = Scraper(url=args.url, timeout=timeout)
        
        # Perform scraping
        results = scraper.scrape(selector=args.selector)
        
        if not results:
            logger.warning("No content extracted from the URL")
            return 0
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in results:
                    f.write(item + '\n')
            logger.info(f"Results saved to {args.output}")
            print(f"Successfully scraped {len(results)} items to {args.output}")
        else:
            # Print to stdout
            print("\n" + "="*60)
            print("SCRAPE RESULTS")
            print("="*60 + "\n")
            for i, item in enumerate(results, 1):
                print(f"Item {i}:")
                print(item)
                print("-" * 60)
            print(f"\nTotal items: {len(results)}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
