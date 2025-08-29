"""
Data processing utilities for AVF Club Scraper.

This module provides functionality for:
- Converting CSV files to Excel format
- Combining multiple CSV files into a single Excel workbook
- Data validation and cleaning
- Export format management
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from config import COMBINED_XLSX_FILENAME, CSV_FIELDNAMES, OUTPUT_DIR


class DataProcessor:
    """
    Handles data processing and export operations for scraped club data.

    This class provides methods for:
    - Converting CSV to Excel formats
    - Combining multiple files
    - Data validation and cleaning
    """

    def __init__(self, output_dir: str = OUTPUT_DIR):
        """
        Initialize the DataProcessor.

        Args:
            output_dir: Directory containing data files
        """
        self.output_dir = Path(output_dir)
        self.logger = self._setup_logger()

        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)

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

    def get_csv_files(self) -> List[Path]:
        """
        Get list of all CSV files in the output directory.

        Returns:
            List of Path objects for CSV files
        """
        csv_files = list(self.output_dir.glob("*.csv"))
        self.logger.debug(f"Found {len(csv_files)} CSV files")
        return csv_files

    def validate_csv_structure(self, csv_file: Path) -> bool:
        """
        Validate that a CSV file has the expected structure.

        Args:
            csv_file: Path to the CSV file

        Returns:
            True if valid, False otherwise
        """
        try:
            df = pd.read_csv(csv_file)

            # Check if required columns exist
            missing_columns = set(CSV_FIELDNAMES) - set(df.columns)
            if missing_columns:
                self.logger.warning(
                    f"CSV file {csv_file.name} missing columns: {missing_columns}"
                )
                return False

            # Check if file has data
            if df.empty:
                self.logger.warning(f"CSV file {csv_file.name} is empty")
                return False

            self.logger.debug(f"CSV file {csv_file.name} validated successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error validating CSV file {csv_file.name}: {e}")
            return False

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize scraped data.

        Args:
            df: DataFrame containing scraped data

        Returns:
            Cleaned DataFrame
        """
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()

        # Standardize N/A values
        cleaned_df = cleaned_df.fillna("N/A")
        cleaned_df = cleaned_df.replace("", "N/A")

        # Strip whitespace from string columns
        string_columns = ["club", "role", "name", "email"]
        for col in string_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()

        # Standardize phone number formatting
        phone_columns = ["mobile_phone", "private_phone"]
        for col in phone_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                # Remove extra spaces in phone numbers
                cleaned_df[col] = cleaned_df[col].str.replace(r"\s+", " ", regex=True)

        # Remove completely empty rows
        cleaned_df = cleaned_df.dropna(how="all")

        self.logger.debug(f"Cleaned data: {len(df)} -> {len(cleaned_df)} rows")
        return cleaned_df

    def convert_csv_to_xlsx(
        self, csv_file: Path, output_file: Optional[Path] = None
    ) -> bool:
        """
        Convert a single CSV file to Excel format.

        Args:
            csv_file: Path to the CSV file
            output_file: Optional output path. If None, uses same name with .xlsx extension

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate input file
            if not self.validate_csv_structure(csv_file):
                return False

            # Read and clean data
            df = pd.read_csv(csv_file)
            df = self.clean_data(df)

            # Determine output file
            if output_file is None:
                output_file = csv_file.with_suffix(".xlsx")

            # Write to Excel
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Trainers")

                # Auto-adjust column widths
                worksheet = writer.sheets["Trainers"]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter

                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            self.logger.info(f"Converted {csv_file.name} to {output_file.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error converting {csv_file.name} to Excel: {e}")
            return False

    def combine_csv_files_to_xlsx(
        self,
        output_filename: str = COMBINED_XLSX_FILENAME,
        separate_sheets: bool = True,
    ) -> bool:
        """
        Combine all CSV files into a single Excel workbook.

        Args:
            output_filename: Name of the output Excel file
            separate_sheets: If True, each club gets its own sheet.
                           If False, all data goes into one sheet.

        Returns:
            True if successful, False otherwise
        """
        csv_files = self.get_csv_files()
        if not csv_files:
            self.logger.warning("No CSV files found to combine")
            return False

        output_path = self.output_dir / output_filename

        try:
            if separate_sheets:
                return self._combine_to_separate_sheets(csv_files, output_path)
            else:
                return self._combine_to_single_sheet(csv_files, output_path)

        except Exception as e:
            self.logger.error(f"Error combining CSV files: {e}")
            return False

    def _combine_to_separate_sheets(
        self, csv_files: List[Path], output_path: Path
    ) -> bool:
        """Combine CSV files into separate sheets of an Excel workbook."""
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for csv_file in csv_files:
                if not self.validate_csv_structure(csv_file):
                    continue

                try:
                    df = pd.read_csv(csv_file)
                    df = self.clean_data(df)

                    # Use club name as sheet name (remove .csv extension)
                    sheet_name = csv_file.stem

                    # Excel sheet names have limitations
                    sheet_name = self._sanitize_sheet_name(sheet_name)

                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    # Auto-adjust column widths
                    worksheet = writer.sheets[sheet_name]
                    self._adjust_column_widths(worksheet)

                    self.logger.debug(f"Added {csv_file.name} to sheet '{sheet_name}'")

                except Exception as e:
                    self.logger.error(f"Error processing {csv_file.name}: {e}")
                    continue

        self.logger.info(f"Combined {len(csv_files)} files into {output_path.name}")
        return True

    def _combine_to_single_sheet(
        self, csv_files: List[Path], output_path: Path
    ) -> bool:
        """Combine all CSV files into a single sheet."""
        all_data = []

        for csv_file in csv_files:
            if not self.validate_csv_structure(csv_file):
                continue

            try:
                df = pd.read_csv(csv_file)
                df = self.clean_data(df)
                all_data.append(df)

            except Exception as e:
                self.logger.error(f"Error processing {csv_file.name}: {e}")
                continue

        if not all_data:
            self.logger.error("No valid data to combine")
            return False

        # Combine all DataFrames
        combined_df = pd.concat(all_data, ignore_index=True)

        # Sort by club name for better organization
        combined_df = combined_df.sort_values(["club", "role", "name"])

        # Write to Excel
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            combined_df.to_excel(writer, sheet_name="All Clubs", index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets["All Clubs"]
            self._adjust_column_widths(worksheet)

        total_records = len(combined_df)
        self.logger.info(
            f"Combined {total_records} records from {len(csv_files)} files into {output_path.name}"
        )
        return True

    def _sanitize_sheet_name(self, name: str) -> str:
        """
        Sanitize a string to be used as an Excel sheet name.

        Args:
            name: Original name

        Returns:
            Sanitized name suitable for Excel sheet
        """
        # Remove invalid characters
        invalid_chars = ["[", "]", "*", "?", ":", "/", "\\"]
        for char in invalid_chars:
            name = name.replace(char, "")

        # Limit length (Excel limit is 31 characters)
        if len(name) > 31:
            name = name[:31]

        # Ensure it's not empty
        if not name:
            name = "Sheet"

        return name

    def _adjust_column_widths(self, worksheet) -> None:
        """Auto-adjust column widths for better readability."""
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass

            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all scraped data.

        Returns:
            Dictionary containing data statistics
        """
        csv_files = self.get_csv_files()
        summary = {
            "total_files": len(csv_files),
            "total_trainers": 0,
            "clubs": [],
            "files_with_errors": [],
        }

        for csv_file in csv_files:
            try:
                if self.validate_csv_structure(csv_file):
                    df = pd.read_csv(csv_file)
                    club_name = df["club"].iloc[0] if not df.empty else csv_file.stem
                    trainer_count = len(df)

                    summary["clubs"].append(
                        {
                            "name": club_name,
                            "trainers": trainer_count,
                            "file": csv_file.name,
                        }
                    )
                    summary["total_trainers"] += trainer_count
                else:
                    summary["files_with_errors"].append(csv_file.name)

            except Exception as e:
                self.logger.error(f"Error reading {csv_file.name}: {e}")
                summary["files_with_errors"].append(csv_file.name)

        return summary

    def print_summary(self) -> None:
        """Print a formatted summary of the scraped data."""
        summary = self.get_data_summary()

        print("\n" + "=" * 50)
        print("AVF CLUB SCRAPER - DATA SUMMARY")
        print("=" * 50)
        print(f"Total files: {summary['total_files']}")
        print(f"Total trainers: {summary['total_trainers']}")
        print(f"Files with errors: {len(summary['files_with_errors'])}")

        if summary["clubs"]:
            print("\nClubs successfully scraped:")
            print("-" * 30)
            for club in sorted(summary["clubs"], key=lambda x: x["name"]):
                print(f"  {club['name']:<20} | {club['trainers']:>3} trainers")

        if summary["files_with_errors"]:
            print(f"\nFiles with errors:")
            print("-" * 20)
            for file in summary["files_with_errors"]:
                print(f"  - {file}")

        print("=" * 50 + "\n")
