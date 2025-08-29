# API Documentation

## ClubScraper Class

The main scraper class for extracting trainer data from AVF MatchCenter.

### Constructor

```python
ClubScraper(output_dir: str = "data")
```

**Parameters:**

- `output_dir` (str): Directory to save output files. Default: "data"

### Methods

#### `scrape_club(club_name: str, club_id: str) -> bool`

Scrape data for a single club.

**Parameters:**

- `club_name` (str): Name of the club
- `club_id` (str): Unique ID of the club on AVF website

**Returns:**

- `bool`: True if successful, False otherwise

**Example:**

```python
scraper = ClubScraper()
success = scraper.scrape_club("FC Sion", "1000")
```

#### `scrape_all_clubs(clubs: Optional[Dict[str, str]] = None) -> Dict[str, bool]`

Scrape data for multiple clubs.

**Parameters:**

- `clubs` (dict, optional): Dictionary mapping club names to IDs. If None, uses all configured clubs.

**Returns:**

- `Dict[str, bool]`: Dictionary mapping club names to success status

**Example:**

```python
scraper = ClubScraper()
results = scraper.scrape_all_clubs()
```

#### `fetch_html_with_curl(url: str, retries: int = 3) -> Optional[str]`

Fetch HTML content from a URL using curl.

**Parameters:**

- `url` (str): The URL to fetch
- `retries` (int): Number of retry attempts. Default: 3

**Returns:**

- `Optional[str]`: HTML content or None if failed

#### `parse_trainer_data(html_content: str, club_name: str) -> List[Dict[str, Any]]`

Parse HTML content to extract trainer information.

**Parameters:**

- `html_content` (str): Raw HTML content
- `club_name` (str): Name of the club

**Returns:**

- `List[Dict[str, Any]]`: List of trainer dictionaries

## DataProcessor Class

Handles data processing and export operations.

### Constructor

```python
DataProcessor(output_dir: str = "data")
```

**Parameters:**

- `output_dir` (str): Directory containing data files. Default: "data"

### Methods

#### `convert_csv_to_xlsx(csv_file: Path, output_file: Optional[Path] = None) -> bool`

Convert a CSV file to Excel format.

**Parameters:**

- `csv_file` (Path): Path to the CSV file
- `output_file` (Path, optional): Output path. If None, uses same name with .xlsx extension

**Returns:**

- `bool`: True if successful, False otherwise

**Example:**

```python
processor = DataProcessor()
success = processor.convert_csv_to_xlsx(Path("data/FC Sion.csv"))
```

#### `combine_csv_files_to_xlsx(output_filename: str = "combined_club_trainers.xlsx", separate_sheets: bool = True) -> bool`

Combine all CSV files into a single Excel workbook.

**Parameters:**

- `output_filename` (str): Name of the output Excel file
- `separate_sheets` (bool): If True, each club gets its own sheet

**Returns:**

- `bool`: True if successful, False otherwise

**Example:**

```python
processor = DataProcessor()
success = processor.combine_csv_files_to_xlsx("combined.xlsx", separate_sheets=True)
```

#### `get_data_summary() -> Dict[str, Any]`

Get a summary of all scraped data.

**Returns:**

- `Dict[str, Any]`: Dictionary containing statistics

**Example:**

```python
processor = DataProcessor()
summary = processor.get_data_summary()
print(f"Total trainers: {summary['total_trainers']}")
```

#### `print_summary() -> None`

Print a formatted summary of the scraped data to console.

**Example:**

```python
processor = DataProcessor()
processor.print_summary()
```

## Data Structure

Each trainer record contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `club` | str | Club name |
| `role` | str | Trainer role/position |
| `name` | str | Full name |
| `mobile_phone` | str | Mobile phone number or "N/A" |
| `private_phone` | str | Private phone number or "N/A" |
| `email` | str | Email address or "N/A" |

## Configuration

The scraper uses several configuration parameters defined in `config.py`:

### HTTP Configuration

- `HEADERS`: List of HTTP headers to send with requests
- `COOKIE_STRING`: Authentication cookie (must be updated regularly)

### Club Configuration

- `CLUBS`: Dictionary mapping club names to their IDs
- `BASE_URL`: URL template for club pages

### Output Configuration

- `OUTPUT_DIR`: Default output directory
- `CSV_FIELDNAMES`: Column names for CSV files
- `COMBINED_XLSX_FILENAME`: Default name for combined Excel file

### Rate Limiting

- `DELAY_BETWEEN_REQUESTS`: Delay between requests in seconds
- `MAX_RETRY_ATTEMPTS`: Maximum retry attempts for failed requests

## Error Handling

The scraper implements comprehensive error handling:

- **Network errors**: Automatic retries with exponential backoff
- **Parsing errors**: Graceful handling of malformed HTML
- **File I/O errors**: Detailed error messages and logging
- **Missing data**: Substitution with "N/A" values

## Logging

The scraper provides detailed logging at multiple levels:

- **INFO**: General progress and status messages
- **DEBUG**: Detailed execution information
- **WARNING**: Non-fatal issues and missing data
- **ERROR**: Errors that prevent operation completion

Configure logging level in your application:

```python
import logging
logging.basicConfig(level=logging.INFO)
```
