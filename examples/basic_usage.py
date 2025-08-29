#!/usr/bin/env python3
"""
Example: Basic usage of the AVF Club Scraper

This script demonstrates the basic usage of the scraper
to extract trainer data from all configured clubs.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraper import ClubScraper, DataProcessor


def main():
    """Example of basic scraper usage."""
    print("AVF Club Scraper - Basic Example")
    print("=" * 40)

    # Initialize the scraper
    scraper = ClubScraper()

    # Scrape all clubs
    print("Starting scrape of all clubs...")
    results = scraper.scrape_all_clubs()

    # Print results
    successful = sum(results.values())
    total = len(results)
    print(f"\nScraping completed: {successful}/{total} clubs successful")

    # Process the data
    processor = DataProcessor()

    # Create combined Excel file
    print("\nCreating combined Excel file...")
    processor.combine_csv_files_to_xlsx()

    # Show summary
    print("\nData Summary:")
    processor.print_summary()


if __name__ == "__main__":
    main()
