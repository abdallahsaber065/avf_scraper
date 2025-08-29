#!/usr/bin/env python3
"""
AVF Club Trainers Scraper

A professional web scraper for extracting trainer and staff information
from the AVF (Association Valaisanne de Football) MatchCenter website.

This script scrapes contact details for football club trainers across
multiple Swiss football clubs and exports the data in CSV and Excel formats.

Author: Your Name
Email: your.email@example.com
Version: 1.0.0
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import CLUBS, OUTPUT_DIR
from scraper import ClubScraper, DataProcessor


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.

    Args:
        verbose: Enable debug logging if True
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("avf_scraper.log")],
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Scrape trainer data from AVF MatchCenter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Scrape all clubs
  %(prog)s --clubs "FC Sion" "FC Sierre"  # Scrape specific clubs
  %(prog)s --xlsx                    # Also generate Excel files
  %(prog)s --verbose                 # Enable debug logging
        """,
    )

    parser.add_argument(
        "--clubs",
        nargs="+",
        help="Specific clubs to scrape (space-separated)",
        metavar="CLUB",
    )

    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help=f"Output directory for data files (default: {OUTPUT_DIR})",
        metavar="DIR",
    )

    parser.add_argument(
        "--xlsx", action="store_true", help="Generate Excel files in addition to CSV"
    )

    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine all CSV files into a single Excel workbook",
    )

    parser.add_argument(
        "--summary", action="store_true", help="Show data summary after scraping"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose (debug) logging"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    return parser.parse_args()


def validate_clubs(club_names: list) -> dict:
    """
    Validate that specified club names exist in configuration.

    Args:
        club_names: List of club names to validate

    Returns:
        Dictionary of valid clubs

    Raises:
        ValueError: If any club names are invalid
    """
    if not club_names:
        return CLUBS

    valid_clubs = {}
    invalid_clubs = []

    for club_name in club_names:
        if club_name in CLUBS:
            valid_clubs[club_name] = CLUBS[club_name]
        else:
            invalid_clubs.append(club_name)

    if invalid_clubs:
        available_clubs = ", ".join(CLUBS.keys())
        raise ValueError(
            f"Invalid club names: {', '.join(invalid_clubs)}\n"
            f"Available clubs: {available_clubs}"
        )

    return valid_clubs


def main() -> int:
    """
    Main function to orchestrate the scraping process.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Set up logging
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)

        logger.info("Starting AVF Club Scraper v1.0.0")

        # Validate club selection
        try:
            clubs_to_scrape = validate_clubs(args.clubs)
        except ValueError as e:
            logger.error(str(e))
            return 1

        logger.info(f"Selected {len(clubs_to_scrape)} clubs to scrape")

        # Initialize scraper and data processor
        scraper = ClubScraper(args.output_dir)
        processor = DataProcessor(args.output_dir)

        # Perform scraping
        logger.info("Starting scrape operation...")
        results = scraper.scrape_all_clubs(clubs_to_scrape)

        # Check results
        successful_clubs = sum(results.values())
        total_clubs = len(results)

        if successful_clubs == 0:
            logger.error("No clubs were successfully scraped")
            return 1

        logger.info(
            f"Scraping completed: {successful_clubs}/{total_clubs} clubs successful"
        )

        # Generate Excel files if requested
        if args.xlsx:
            logger.info("Generating individual Excel files...")
            csv_files = processor.get_csv_files()
            for csv_file in csv_files:
                processor.convert_csv_to_xlsx(csv_file)

        # Combine files if requested
        if args.combine:
            logger.info("Combining CSV files into Excel workbook...")
            success = processor.combine_csv_files_to_xlsx()
            if success:
                logger.info("Successfully created combined Excel workbook")
            else:
                logger.warning("Failed to create combined Excel workbook")

        # Show summary if requested
        if args.summary:
            processor.print_summary()

        logger.info("AVF Club Scraper completed successfully")
        return 0

    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
