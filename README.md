# Odisha RERA Project Scraper
(internshala assignment)
This Python script scrapes the first 6 projects listed under the “Projects Registered” section of the [Odisha RERA Website](https://rera.odisha.gov.in/projects/project-list) and extracts the following details:

- RERA Registration Number
- Project Name
- Promoter Name (Company Name under Promoter Details)
- Promoter Address (Registered Office Address)
- GST Number

## Features

- Dynamic scraping using Selenium WebDriver
- Extracts data from multiple tabs per project
- Saves output in CSV, JSON, and Excel formats
- Detailed logging for each step
- Configurable number of projects (default is 6)

## Repository Contents

- `rera_scraper.py` – Main script for scraping
- `odisha_rera_projects_fixed.csv` – Output data in CSV format
- `odisha_rera_projects_fixed.json` – Output data in JSON format
- `odisha_rera_projects_fixed.xlsx` – Output data in Excel format
- `scraper.log` – Logs from scraping execution
- `README.md` – Project documentation

## Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/jhanaviii/WebScraping.git
cd WebScraping
```

2. **Install dependencies**
```bash
pip install selenium pandas openpyxl
```

3. **Download and configure ChromeDriver**
- Download ChromeDriver from: https://sites.google.com/a/chromium.org/chromedriver/downloads
- Make sure it matches your installed version of Google Chrome.
- Update the `chromedriver_path` variable in `rera_scraper.py`:
```python
driver = webdriver.Chrome(executable_path="/your/path/to/chromedriver", options=options)
```

4. **Run the scraper**
```bash
python rera_scraper.py
```

## Output

The script generates:
- `odisha_rera_projects_fixed.csv`
- `odisha_rera_projects_fixed.json`
- `odisha_rera_projects_fixed.xlsx`
- `scraper.log`

All files will be saved in the same directory.

## Notes

- Default project count is 6. You can modify this in the script:
```python
max_projects = 6
```

## License

MIT License
