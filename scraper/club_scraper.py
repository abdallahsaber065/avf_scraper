"""
Core scraping functionality for AVF Club data.

This module contains the main ClubScraper class that handles:
- HTTP requests with proper headers and authentication
- HTML parsing and data extraction
- Error handling and retry logic
- Rate limiting and polite scraping
"""

import csv
import logging
import os
import re
import subprocess
import time
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from config import (
    BASE_URL,
    CLUBS,
    COOKIE_STRING,
    CSV_FIELDNAMES,
    DELAY_BETWEEN_REQUESTS,
    HEADERS,
    MAX_RETRY_ATTEMPTS,
    OUTPUT_DIR,
)


class ClubScraper:
    """
    Main scraper class for extracting trainer data from AVF MatchCenter.

    This class handles the complete scraping workflow including:
    - Making authenticated HTTP requests
    - Parsing HTML content
    - Extracting trainer information
    - Saving data to CSV files
    """

    def __init__(self, output_dir: str = OUTPUT_DIR):
        """
        Initialize the ClubScraper.

        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        self.logger = self._setup_logger()

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")

    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def fetch_html_with_curl(
        self, url: str, retries: int = MAX_RETRY_ATTEMPTS
    ) -> Optional[str]:
        """
        Execute a curl command with specific headers and cookies to fetch a webpage.

        Args:
            url: The URL to fetch
            retries: Number of retry attempts for failed requests

        Returns:
            HTML content as string or None if it fails
        """
        self.logger.info(f"Fetching URL: {url}")

        command = ["curl", "--location", "--silent", url]
        for header in HEADERS:
            command.extend(["--header", header])
        command.extend(["--header", f"Cookie: {COOKIE_STRING}"])

        for attempt in range(retries + 1):
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",
                    timeout=30,  # 30 second timeout
                )

                if result.stdout.strip():
                    self.logger.debug(f"Successfully fetched {url}")
                    return result.stdout
                else:
                    self.logger.warning(f"Empty response from {url}")

            except subprocess.CalledProcessError as e:
                self.logger.error(
                    f"Curl command failed for {url} with exit code {e.returncode}. "
                    f"Stderr: {e.stderr.strip()}"
                )

            except subprocess.TimeoutExpired:
                self.logger.error(f"Request timeout for {url}")

            except FileNotFoundError:
                self.logger.error(
                    "curl command not found. Please ensure curl is installed and in your system's PATH."
                )
                return None

            if attempt < retries:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                self.logger.info(
                    f"Retrying in {wait_time} seconds... (attempt {attempt + 1}/{retries})"
                )
                time.sleep(wait_time)

        self.logger.error(f"Failed to fetch {url} after {retries + 1} attempts")
        return None

    def parse_trainer_data(
        self, html_content: str, club_name: str
    ) -> List[Dict[str, Any]]:
        """
        Parse HTML content to extract trainer data.

        Args:
            html_content: Raw HTML content from the webpage
            club_name: Name of the club being processed

        Returns:
            List of dictionaries containing trainer information
        """
        if not html_content:
            self.logger.warning(f"No HTML content provided for {club_name}")
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        all_trainers_data = []

        # Find all trainer sections
        heading_rows = soup.select("div.liste div.row.heading")
        self.logger.debug(f"Found {len(heading_rows)} trainer sections for {club_name}")

        for heading_row in heading_rows:
            trainer_data = self._extract_trainer_info(heading_row, club_name)
            if trainer_data:
                all_trainers_data.append(trainer_data)

        self.logger.info(
            f"Extracted {len(all_trainers_data)} trainer records for {club_name}"
        )
        return all_trainers_data

    def _extract_trainer_info(
        self, heading_row, club_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract individual trainer information from a heading row.

        Args:
            heading_row: BeautifulSoup element containing trainer heading
            club_name: Name of the club

        Returns:
            Dictionary with trainer information or None if extraction fails
        """
        try:
            # Get the data row following the heading
            data_row = heading_row.find_next_sibling("div", class_="row")
            if not data_row:
                return None

            # Extract role and name
            role = self._extract_role(heading_row)
            name = self._extract_name(data_row)

            if not name:
                return None

            # Initialize trainer info
            trainer_info = {
                "club": club_name,
                "role": role,
                "name": name,
                "mobile_phone": "N/A",
                "private_phone": "N/A",
                "email": "N/A",
            }

            # Extract email
            trainer_info["email"] = self._extract_email(data_row)

            # Extract phone numbers
            phones = self._extract_phone_numbers(data_row)
            trainer_info.update(phones)

            return trainer_info

        except Exception as e:
            self.logger.error(f"Error extracting trainer info: {e}")
            return None

    def _extract_role(self, heading_row) -> str:
        """Extract trainer role from heading row."""
        role_element = heading_row.select_one("h5")
        return role_element.get_text(strip=True) if role_element else "N/A"

    def _extract_name(self, data_row) -> Optional[str]:
        """Extract trainer name from data row."""
        name_tag = data_row.select_one("span.ftName")
        return name_tag.get_text(strip=True) if name_tag else None

    def _extract_email(self, data_row) -> str:
        """Extract email address from data row."""
        email_tag = data_row.select_one("a[href*='javascript:openMess']")
        if email_tag:
            href = email_tag.get("href", "")
            match = re.search(r"openMess\('([^']*)',\s*'([^']*)'\)", href)
            if match:
                domain, user = match.groups()
                return f"{user}@{domain}"
        return "N/A"

    def _extract_phone_numbers(self, data_row) -> Dict[str, str]:
        """Extract phone numbers from data row."""
        phones = {"mobile_phone": "N/A", "private_phone": "N/A"}

        contact_column_divs = data_row.select("div.col-md-6")
        if len(contact_column_divs) > 1:
            contact_text = contact_column_divs[1].get_text(separator=" ", strip=True)

            # Extract private phone
            private_match = re.search(r"Tél privé\s*:\s*(\+[\d\s\(\)]+)", contact_text)
            if private_match:
                phones["private_phone"] = private_match.group(1).strip()

            # Extract mobile phone
            mobile_match = re.search(r"Mobile\s*:\s*(\+[\d\s\(\)]+)", contact_text)
            if mobile_match:
                phones["mobile_phone"] = mobile_match.group(1).strip()

        return phones

    def save_to_csv(self, trainers_data: List[Dict[str, Any]], club_name: str) -> bool:
        """
        Save trainer data to CSV file.

        Args:
            trainers_data: List of trainer dictionaries
            club_name: Name of the club

        Returns:
            True if successful, False otherwise
        """
        if not trainers_data:
            self.logger.warning(f"No trainer data to save for {club_name}")
            return False

        # Sanitize club name for filename
        safe_club_name = re.sub(r'[\\/*?:"<>|]', "", club_name)
        filepath = os.path.join(self.output_dir, f"{safe_club_name}.csv")

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
                writer.writeheader()
                writer.writerows(trainers_data)

            self.logger.info(f"Saved {len(trainers_data)} records to {filepath}")
            return True

        except IOError as e:
            self.logger.error(f"Could not write to file {filepath}. Reason: {e}")
            return False

    def scrape_club(self, club_name: str, club_id: str) -> bool:
        """
        Scrape data for a single club.

        Args:
            club_name: Name of the club
            club_id: Unique ID of the club

        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Processing: {club_name}")

        # Construct URL
        target_url = BASE_URL.format(club_id=club_id)

        # Fetch HTML
        html = self.fetch_html_with_curl(target_url)
        if not html:
            return False

        # Parse data
        trainers_data = self.parse_trainer_data(html, club_name)

        # Save to CSV
        return self.save_to_csv(trainers_data, club_name)

    def scrape_all_clubs(
        self, clubs: Optional[Dict[str, str]] = None
    ) -> Dict[str, bool]:
        """
        Scrape data for all configured clubs.

        Args:
            clubs: Optional dictionary of clubs to scrape. If None, uses default CLUBS.

        Returns:
            Dictionary mapping club names to success status
        """
        if clubs is None:
            clubs = CLUBS

        results = {}
        total_clubs = len(clubs)

        self.logger.info(f"Starting scrape of {total_clubs} clubs")

        for i, (club_name, club_id) in enumerate(clubs.items(), 1):
            self.logger.info(f"[{i}/{total_clubs}] Processing {club_name}")

            success = self.scrape_club(club_name, club_id)
            results[club_name] = success

            # Rate limiting - wait between requests
            if i < total_clubs:  # Don't wait after the last request
                self.logger.debug(f"Waiting {DELAY_BETWEEN_REQUESTS} seconds...")
                time.sleep(DELAY_BETWEEN_REQUESTS)

        # Log summary
        successful = sum(results.values())
        self.logger.info(
            f"Scraping complete: {successful}/{total_clubs} clubs successful"
        )

        if successful < total_clubs:
            failed_clubs = [club for club, success in results.items() if not success]
            self.logger.warning(f"Failed clubs: {', '.join(failed_clubs)}")

        return results
