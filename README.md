# cunybotv2: College Course Data Scraper

## Overview

The College Course Data Scraper is a Python application that automates the process of scraping course data from the CUNY Global Search Tool. It allows users to select colleges, terms, subjects, and careers, and then extracts relevant course information, saving it in both JSON and CSV formats. The application also manages user preferences and cleans up old data files.

## Features

- **User Preferences**: Saves and loads user preferences for college, term, subject, and career selections.
- **Data Scraping**: Utilizes Playwright to navigate the CUNY Global Search Tool and extract course data.
- **Data Storage**: Saves scraped data in JSON and CSV formats for easy access and analysis.
- **Data Cleanup**: Automatically deletes old data files to maintain a clean working directory.

## Requirements

- Python 3.7 or higher
- Required Python packages:
  - `playwright`
  - `beautifulsoup4`
  - `aiofiles`
  - `csv`
  - `json`
  - `datetime`
  - `os`
  - `logging`

You can install the required packages using pip:

```bash
pip install playwright beautifulsoup4 aiofiles
```

Make sure to install the Playwright browsers as well:

```bash
playwright install
```

## File Structure

```
.
├── clean.py               # Script to clean up old CSV and JSON files
├── ClassStatus.py         # Script to read and filter course data from CSV files
├── scrap.py               # Main scraping script using Playwright
├── preferences.py         # Module for saving and loading user preferences
└── officialScrap.py       # Main application logic for scraping and data management
```

## Usage

1. **Run the Scraper**: Execute the `officialScrap.py` script to start the scraping process.

   ```bash
   python officialScrap.py
   ```

2. **Select Options**: Follow the prompts to select your college, term, subject, and career.

3. **View Results**: The scraped data will be saved in the `collegeCourseData` directory, organized into `csvFiles` and `jsonFiles` subdirectories.

4. **Check Course Status**: Use the `ClassStatus.py` script to check the status of specific courses.

   ```bash
   python ClassStatus.py
   ```

5. **Clean Up Old Files**: Run the `clean.py` script to remove old data files that are no longer needed.

   ```bash
   python clean.py
   ```

## Configuration

- User preferences are saved in a JSON file named `userPreference.json`. This file stores the last selected college, term, subject, and career, allowing for quicker access in future runs.

## Logging

The application uses Python's built-in logging module to log important events and errors. Logs are printed to the console and can be modified to save to a file if needed.
