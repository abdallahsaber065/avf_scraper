"""
AVF Club Scraper package.

This package provides tools for scraping trainer and staff information
from the AVF (Association Valaisanne de Football) MatchCenter website.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .club_scraper import ClubScraper
from .data_processor import DataProcessor

__all__ = ["ClubScraper", "DataProcessor"]
