# krawl_io

A Python web scraping library with an accessible command-line interface, designed to make web data extraction simple and user-friendly.

## Introduction

The `krawl_io` project provides robust web scraping capabilities with a focus on accessibility and ease of use. It allows developers and data scientists to efficiently gather and analyze data from various online sources with minimal setup.

## Features

- **Accessible CLI Interface**: Clear prompts, helpful error messages, and verbose output options
- **Simple Python API**: Easy-to-use programmatic interface for custom scraping tasks
- **CSS Selector Support**: Target specific elements on web pages
- **Configurable Settings**: Save and reuse scraping configurations
- **Comprehensive Logging**: Track scraping operations with detailed logging
- **Error Handling**: Robust error handling with helpful user feedback

## Installation

### From Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/feileberlin/krawl_io.git
   cd krawl_io
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

### Requirements

- Python 3.8 or higher
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0

## Usage

### Command-Line Interface

The CLI provides an accessible way to scrape web pages from your terminal:

**Basic scraping:**
```bash
krawl https://example.com
```

**Scrape with CSS selector:**
```bash
krawl https://example.com -s "p.content"
```

**Save results to file:**
```bash
krawl https://example.com -o results.txt
```

**Use custom timeout:**
```bash
krawl https://example.com -t 60
```

**Verbose output:**
```bash
krawl https://example.com -v
```

**Quiet mode (errors only):**
```bash
krawl https://example.com -q
```

**Use configuration file:**
```bash
krawl https://example.com -c config.json
```

**View all options:**
```bash
krawl --help
```

### Python API

You can also use krawl_io programmatically in your Python scripts:

```python
from krawl_io import Scraper, Config

# Basic scraping
scraper = Scraper(url="https://example.com")
results = scraper.scrape()

# With CSS selector
results = scraper.scrape(selector="p")

# Using configuration
config = Config()
config.set("timeout", 60)
scraper = Scraper(url="https://example.com", timeout=config.get("timeout"))
results = scraper.scrape()
```

See `examples/basic_usage.py` for more detailed examples.

## Configuration

Create a JSON configuration file to customize scraping behavior:

```json
{
  "timeout": 30,
  "user_agent": "krawl_io/0.1.0",
  "max_retries": 3,
  "log_level": "INFO"
}
```

Load it with:
```bash
krawl https://example.com -c config.json
```

Or in Python:
```python
from krawl_io import Config
config = Config(Path("config.json"))
```

## Accessibility Features

krawl_io is designed with accessibility in mind:

- **Clear command-line options** with descriptive help text
- **Informative error messages** that guide users to solutions
- **Logging levels** for different output verbosity needs
- **Progress indicators** to keep users informed
- **Keyboard interrupt handling** for graceful cancellation
- **Exit codes** that follow standard conventions

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or using unittest:
```bash
python -m unittest discover tests
```

## Examples

See the `examples/` directory for sample scripts demonstrating various use cases.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Respect for Websites

When using krawl_io, please:
- Respect robots.txt files
- Implement rate limiting for repeated requests
- Follow website terms of service
- Be considerate of server resources