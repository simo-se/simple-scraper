# Web Scraper with CAPTCHA Bypass

This Python script is designed to scan websites where content is distributed across a large number of paginated pages, following a simple URL structure of the format `base_url/page_number/`. It searches for a specific keyword in the text body of each page and outputs a list of all URLs where the keyword was successfully found.

The scraper is equipped to handle modern anti-bot protections (such as Cloudflare's "Just a moment" challenge) by starting in a visible (non-headless) browser window. This allows you to manually solve any initial CAPTCHA or challenge, after which the script automatically resumes rapid sequential scraping.

## Key Features
- **Manual CAPTCHA Solving**: The browser opens in a visible window if a Cloudflare challenge is detected, waiting for the user to solve it before scraping.
- **Progress Persistence**: Keeps track of the last scanned page index in `scraper_progress.txt`. If the process is interrupted, it automatically resumes from the last page index on the next run.
- **Language Filtering**: Automatically selects the Italian language filter at the beginning of the scraping session.
- **Auto-detection of Chromium/Chrome Version**: Programmatically detects the major version of the system's Google Chrome or Chromium browser to run the matching ChromeDriver version and prevent session creation issues.

---

## Installation

1. **Prerequisites**: Ensure you have Google Chrome or Chromium installed on your system.
2. **Create a Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration & Customization

You can configure the scraper's settings directly within `scraper.py`:

### Customizing the Search
At the bottom of the file, you'll find the main execution block:

```python
# The keyword to search for on each page
STRINGA_DA_CERCARE = "RuoteClassiche"

# Base delay between requests
RITARDO_IN_SECONDI = 5 

scrape_with_selenium(
    base_url='https://eurekaddl.art/magazines/page/',
    initial_start_page=3,       # Page to start from if no progress log exists
    end_page=143,               # Last page of the scan
    search_string=STRINGA_DA_CERCARE,
    delay_seconds=RITARDO_IN_SECONDI
)
```

### Output Files & State
The following files are generated in the working directory:
- **`found_urls.txt`** (`OUTPUT_FILE`): The file where URLs containing the keyword (`STRINGA_DA_CERCARE`) will be appended.
- **`scraper_progress.txt`** (`LOG_FILE`): Keeps track of the last successfully scanned page index for automatic resuming. If you want to restart the scan from scratch, simply delete this file.

---

## Running the Scraper

Start the script using:
```bash
python scraper.py
```
If a Cloudflare challenge page ("Just a moment" or similar) appears, solve it manually in the opened Chrome window. Once the challenge is bypassed, the script will automatically continue running.
