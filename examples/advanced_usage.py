#!/usr/bin/env python3
"""
Example: Advanced usage with custom configuration

This script shows how to use the scraper with custom settings,
selective club scraping, and advanced data processing.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import CLUBS
from scraper import ClubScraper, DataProcessor


def setup_custom_logging():
    """Set up custom logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("advanced_scraper.log"), logging.StreamHandler()],
    )


def main():
    """Example of advanced scraper usage."""
    print("AVF Club Scraper - Advanced Example")
    print("=" * 50)

    # Set up logging
    setup_custom_logging()
    logger = logging.getLogger(__name__)

    # Select specific clubs to scrape
    selected_clubs = {
        "FC Sion": CLUBS["FC Sion"],
        "FC Sierre": CLUBS["FC Sierre"],
        "FC Bramois": CLUBS["FC Bramois"],
    }

    logger.info(f"Selected {len(selected_clubs)} clubs for scraping")

    # Initialize scraper with custom output directory
    custom_output_dir = "custom_data"
    scraper = ClubScraper(output_dir=custom_output_dir)

    # Scrape selected clubs
    print(f"\nScraping {len(selected_clubs)} selected clubs...")
    results = scraper.scrape_all_clubs(selected_clubs)

    # Analyze results
    successful_clubs = [club for club, success in results.items() if success]
    failed_clubs = [club for club, success in results.items() if not success]

    print(f"\nResults:")
    print(f"  Successful: {len(successful_clubs)}")
    print(f"  Failed: {len(failed_clubs)}")

    if failed_clubs:
        print(f"  Failed clubs: {', '.join(failed_clubs)}")

    # Process data with custom options
    processor = DataProcessor(output_dir=custom_output_dir)

    # Convert individual files to Excel
    print("\nConverting CSV files to Excel...")
    csv_files = processor.get_csv_files()
    for csv_file in csv_files:
        success = processor.convert_csv_to_xlsx(csv_file)
        if success:
            print(f"  ✓ Converted {csv_file.name}")
        else:
            print(f"  ✗ Failed to convert {csv_file.name}")

    # Create combined workbook with separate sheets
    print("\nCreating combined workbook...")
    success = processor.combine_csv_files_to_xlsx(
        output_filename="selected_clubs_combined.xlsx", separate_sheets=True
    )

    if success:
        print("  ✓ Combined workbook created successfully")
    else:
        print("  ✗ Failed to create combined workbook")

    # Create single-sheet combined file
    print("\nCreating single-sheet combined file...")
    success = processor.combine_csv_files_to_xlsx(
        output_filename="all_trainers_single_sheet.xlsx", separate_sheets=False
    )

    if success:
        print("  ✓ Single-sheet file created successfully")

    # Show detailed summary
    print("\n" + "=" * 50)
    processor.print_summary()

    # Get data summary for programmatic use
    summary = processor.get_data_summary()

    print(f"\nProgrammatic Summary:")
    print(f"  Total files: {summary['total_files']}")
    print(f"  Total trainers: {summary['total_trainers']}")
    print(
        f"  Average trainers per club: {summary['total_trainers'] / summary['total_files']:.1f}"
    )

    logger.info("Advanced scraping example completed")


if __name__ == "__main__":
    main()
