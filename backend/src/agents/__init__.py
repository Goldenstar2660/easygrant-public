"""AI Agent pipeline for proposal generation.

Agents:
- RequirementsExtractor: Parse funding call into structured blueprint
"""

from .requirements_extractor import RequirementsExtractor

__all__ = ['RequirementsExtractor']
