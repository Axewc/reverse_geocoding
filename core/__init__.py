"""
Core module for reverse geocoding tools.

This module contains the main functionality for:
- KML data extraction
- CRESTA integration
- Geographic data processing
"""

from .kml_extractor import KMLExtractor

# Optional import for cresta_integration
try:
    from .cresta_integration import *
except ImportError:
    pass

__all__ = ['KMLExtractor']