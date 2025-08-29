# AVF Club Trainers Scraper

A professional web scraper for extracting trainer and staff information from the AVF (Association Valaisanne de Football) MatchCenter website. This tool efficiently scrapes contact details for football club trainers across multiple Swiss football clubs.

## 🚀 Features

- **Multi-club scraping**: Extracts data from 14 different football clubs
- **Comprehensive data extraction**: Captures trainer names, roles, phone numbers, and email addresses
- **Export flexibility**: Outputs data in both CSV and Excel formats
- **Rate limiting**: Implements polite scraping with configurable delays
- **Error handling**: Robust error handling with detailed logging
- **Cookie-based authentication**: Handles session management for protected content

## 📋 Prerequisites

- Python 3.7+
- curl (must be installed and accessible via command line)
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/abdallahsaber065/avf_scraper.git
    cd avf-scraper
    ```

2. Install required dependencies:

    ```bash
    pip install -r requiremenzts.txt
    ```

3. Ensure curl is installed and accessible from command line

## ⚙️ Configuration

Before running the scraper, you need to update the cookie string in `config.py`:

1. Open the AVF MatchCenter website in your browser
2. Open Developer Tools (F12) → Network tab
3. Navigate to any club's trainer page
4. Copy the Cookie header from a successful request
5. Update the `COOKIE_STRING` in `config.py`

**Note**: Cookies expire regularly and need to be refreshed when the scraper stops working.

## 🚀 Usage

### Basic Usage

Run the scraper for all configured clubs:

```bash
python scrape_clubs.py
```

### Advanced Usage

```python
from scraper.club_scraper import ClubScraper

# Initialize scraper
scraper = ClubScraper()

# Scrape specific clubs
scraper.scrape_clubs(['FC Sion', 'FC Sierre'])

# Convert results to Excel
scraper.combine_csv_to_xlsx()
```

## 📊 Output

The scraper generates:

- **Individual CSV files**: One file per club in the `data/` directory
- **Combined Excel file**: All clubs consolidated into `combined_club_trainers.xlsx`

### Data Structure

Each record contains:

- `club`: Club name
- `role`: Trainer role/position
- `name`: Full name
- `mobile_phone`: Mobile phone number
- `private_phone`: Private phone number  
- `email`: Email address

## 🏗️ Project Structure

```bash
avf_scraper/
├── data/                      # Output directory for scraped data
├── scraper/                   # Main scraper modules
│   ├── __init__.py
│   ├── club_scraper.py       # Core scraping logic
│   └── data_processor.py     # Data processing utilities
├── config.py                 # Configuration settings
├── scrape_clubs.py          # Main execution script
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Configuration Options

Edit `config.py` to customize:

- `DELAY_BETWEEN_REQUESTS`: Delay between requests (default: 3 seconds)
- `OUTPUT_DIR`: Output directory for data files
- `CLUBS`: Dictionary of clubs and their IDs to scrape
- `HEADERS`: HTTP headers for requests

## 🛡️ Rate Limiting & Ethics

This scraper implements responsible scraping practices:

- Configurable delays between requests
- Respect for robots.txt (where applicable)
- Session management to avoid excessive authentication requests
- Error handling to prevent infinite retry loops

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Please ensure you comply with the website's terms of service and applicable laws when using this scraper. The author is not responsible for any misuse of this software.
