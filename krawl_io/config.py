"""
Configuration management for krawl_io.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class Config:
    """
    Configuration manager for krawl_io scraping sessions.
    
    Provides methods to load, save, and manage scraping configurations.
    """
    
    DEFAULT_CONFIG = {
        "timeout": 30,
        "user_agent": "krawl_io/0.1.0 (Web Scraping Library)",
        "max_retries": 3,
        "log_level": "INFO"
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.settings = self.DEFAULT_CONFIG.copy()
        self.logger = logging.getLogger(__name__)
        
        if config_path and config_path.exists():
            self.load(config_path)
    
    def load(self, config_path: Path) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                self.settings.update(user_config)
                self.logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            self.logger.warning(f"Failed to load config from {config_path}: {e}")
    
    def save(self, config_path: Path) -> None:
        """
        Save current configuration to a JSON file.
        
        Args:
            config_path: Path where to save the configuration
        """
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
                self.logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config to {config_path}: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
        """
        self.settings[key] = value
        self.logger.debug(f"Set config {key} = {value}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get all configuration as a dictionary.
        
        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()
