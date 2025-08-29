"""
Configuration settings for the AVF Club Scraper.

This module contains all configuration parameters including:
- HTTP headers and authentication
- Club definitions and IDs
- Output settings
- Request timing and rate limiting
"""

import os

# --- HTTP Configuration ---

# Standard headers to mimic a real browser request
HEADERS = [
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language: en-US,en;q=0.5",
    "Connection: keep-alive",
    "Upgrade-Insecure-Requests: 1",
    "Cache-Control: max-age=0",
]

# Cookie string for authentication
# IMPORTANT: This cookie will expire. When the script stops working,
# update this cookie by inspecting network requests in your browser.
COOKIE_STRING = "_cf_bm=3ZsEBG9DOuOl8tqueaWL6zOAVuX8ZdBSNQRvxt8jhzU-1749924924-1.0.1.1-jrrrqrWRYaEJWIuj6iwV1Efhnm1jN5OI9zURllDAmkJloCrpNor1QOOabUfXldMD.MTM0xvWGpqNRdWWKwBjbXkInMg26_3Z.jJn2u1whM; ARRAffinity=06dece71727ab2c9a75506862155277ef8948b1004ad39e70a73eb837c7bf7ad; ARRAffinitySameSite=06dece71727ab2c9a75506862155277ef8948b1004ad39e70a73eb837c7bf7ad; ASP.NET_SessionId=w3b25t5nmdvlhl0zepm2tya5"

# --- URL Configuration ---

BASE_URL = "https://matchcenter.avf-wfv.ch/default.aspx?v={club_id}&oid=17&lng=2&a=tr"

# --- Club Definitions ---

# Dictionary mapping club names to their unique IDs on the AVF website
CLUBS = {
    "FC Vétroz": "1005",
    "FC Conthey": "970",
    "FC Sion": "1000",
    "FC Bramois": "964",
    "FC Châteauneuf": "967",
    "FC Grimisuat": "976",
    "US Ayent-Arbaz": "962",
    "FC Chalais": "1011",
    "FC Riddes": "990",
    "FC Printse-Nendaz": "1006753",
    "FC Erde": "971",
    "FC US Hérens": "1006",
    "FC Sierre": "999",
    "FC Granges": "975",
}

# --- Output Configuration ---

# Directory for output files
OUTPUT_DIR = "data"

# CSV field names in order
CSV_FIELDNAMES = [
    "club",
    "role",
    "name",
    "mobile_phone",
    "private_phone",
    "email",
]

# --- Rate Limiting ---

# Delay between requests in seconds (be respectful to the server)
DELAY_BETWEEN_REQUESTS = 3

# Maximum retry attempts for failed requests
MAX_RETRY_ATTEMPTS = 3

# --- File Paths ---

# Combined output file name
COMBINED_XLSX_FILENAME = "combined_club_trainers.xlsx"

# --- Logging Configuration ---

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# --- Environment Variables ---

# Check for environment variable overrides
if os.getenv("AVF_COOKIE"):
    COOKIE_STRING = os.getenv("AVF_COOKIE")

if os.getenv("AVF_OUTPUT_DIR"):
    OUTPUT_DIR = os.getenv("AVF_OUTPUT_DIR")

if os.getenv("AVF_DELAY"):
    try:
        DELAY_BETWEEN_REQUESTS = int(os.getenv("AVF_DELAY"))
    except ValueError:
        pass  # Keep default value if conversion fails
