"""Configuration loader with validation.

Loads and validates the backend/config.yaml file.
Implements Constitution Principle VIII: Centralized configuration.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Loads and validates configuration from config.yaml"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Singleton pattern to load config once"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the config loader"""
        if self._config is None:
            self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.yaml"""
        # Try multiple paths to find config.yaml
        possible_paths = [
            Path("backend/config.yaml"),  # From repo root
            Path("config.yaml"),  # From backend directory
            Path("../config.yaml"),  # From src directory
            Path("../../config.yaml"),  # From utils directory
        ]
        
        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        
        if not config_path:
            raise FileNotFoundError(
                "config.yaml not found. Checked: " + 
                ", ".join(str(p) for p in possible_paths)
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required sections
        required_sections = ['llm', 'embeddings', 'retrieval', 'vector_store', 'upload', 'hosting']
        missing = [s for s in required_sections if s not in config]
        if missing:
            raise ValueError(f"Missing required config sections: {missing}")
        
        return config
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get nested configuration value.
        
        Args:
            *keys: Nested keys to traverse (e.g., 'llm', 'requirements_model')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            config.get('llm', 'requirements_model')  # 'gpt-4o'
            config.get('embeddings', 'chunk_size')  # 600
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value
    
    @property
    def llm(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self._config.get('llm', {})
    
    @property
    def embeddings(self) -> Dict[str, Any]:
        """Get embeddings configuration"""
        return self._config.get('embeddings', {})
    
    @property
    def retrieval(self) -> Dict[str, Any]:
        """Get retrieval configuration"""
        return self._config.get('retrieval', {})
    
    @property
    def vector_store(self) -> Dict[str, Any]:
        """Get vector store configuration"""
        return self._config.get('vector_store', {})
    
    @property
    def upload(self) -> Dict[str, Any]:
        """Get upload configuration"""
        return self._config.get('upload', {})
    
    @property
    def hosting(self) -> Dict[str, Any]:
        """Get hosting configuration"""
        return self._config.get('hosting', {})
    
    @property
    def privacy(self) -> Dict[str, Any]:
        """Get privacy configuration"""
        return self._config.get('privacy', {})


# Global config instance
config = ConfigLoader()
