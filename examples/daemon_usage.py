"""
Example of using krawl_io in daemon mode for continuous source discovery.

This script demonstrates how to run krawl_io as a daemon to continuously
monitor and discover new sources related to specific topics and areas.
"""

from krawl_io import Daemon, SourceDiscovery, Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def on_source_discovered(source):
    """
    Callback function called when a new source is discovered.
    
    Args:
        source: Dictionary with source metadata
    """
    print(f"\n🎯 NEW SOURCE DISCOVERED!")
    print(f"   URL: {source['url']}")
    print(f"   Title: {source.get('title', 'N/A')}")
    print(f"   Relevance: {source.get('relevance_score', 0):.2f}")
    print(f"   Discovered at: {source['discovered_at']}")


def example_daemon_programmatic():
    """Example: Run daemon programmatically"""
    print("\n=== Example 1: Programmatic Daemon ===")
    
    # Create configuration
    config = Config()
    config.set("timeout", 30)
    config.set("daemon_output", "my_sources.json")
    
    # Setup source discovery with topics and areas
    discovery = SourceDiscovery(
        topics=["events", "concert", "festival", "party"],
        areas=["berlin", "germany"],
        max_depth=2
    )
    
    # Create daemon
    daemon = Daemon(config=config, discovery=discovery)
    
    # Start daemon (will run continuously)
    # Use Ctrl+C to stop
    seed_urls = [
        "https://example.com/events",
        "https://example.com/calendar"
    ]
    
    print("Starting daemon... (Press Ctrl+C to stop)")
    print(f"Topics: {discovery.topics}")
    print(f"Areas: {discovery.areas}")
    print(f"Seed URLs: {', '.join(seed_urls)}")
    
    # daemon.start(
    #     seed_urls=seed_urls,
    #     interval=3600,  # Check every hour
    #     callback=on_source_discovered
    # )


def example_daemon_cli():
    """Example: Run daemon via CLI"""
    print("\n=== Example 2: CLI Daemon Mode ===")
    print("\nTo run daemon mode from command line:")
    print()
    print("# Basic daemon mode with topics")
    print("krawl https://example.com/events \\")
    print("  --daemon \\")
    print("  --topics events concert festival \\")
    print("  --interval 3600")
    print()
    print("# Daemon with topics and geographic filtering")
    print("krawl https://example.com/events,https://example.com/calendar \\")
    print("  --daemon \\")
    print("  --topics events music party \\")
    print("  --areas berlin germany \\")
    print("  --interval 1800 \\")
    print("  --max-depth 3")
    print()
    print("# With configuration file")
    print("krawl https://example.com/events \\")
    print("  --daemon \\")
    print("  --topics events \\")
    print("  --config daemon_config.json \\")
    print("  -v  # verbose mode")


def example_discovery_only():
    """Example: Use SourceDiscovery standalone"""
    print("\n=== Example 3: Standalone Source Discovery ===")
    
    # Create discovery instance
    discovery = SourceDiscovery(
        topics=["technology", "startup", "innovation"],
        areas=["san francisco", "bay area"],
        max_depth=1
    )
    
    # Discover sources from a seed URL
    print("Discovering sources...")
    # sources = discovery.discover_from_url("https://example.com")
    
    # print(f"\nDiscovered {len(sources)} relevant sources:")
    # for source in sources[:5]:  # Show first 5
    #     print(f"  - {source['url']} (score: {source['relevance_score']:.2f})")


if __name__ == "__main__":
    print("krawl_io Daemon Mode Examples")
    print("=" * 60)
    
    # Note: Actual daemon execution is commented out to prevent
    # running indefinitely. Uncomment to test in your environment.
    
    example_daemon_cli()
    example_discovery_only()
    
    # Uncomment to run programmatically (will run indefinitely):
    # example_daemon_programmatic()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("\nNote: Daemon examples show usage but don't execute to avoid")
    print("running indefinitely. Uncomment the code to test in your environment.")
