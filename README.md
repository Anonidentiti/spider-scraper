# Spider Scraper

Spider Scraper is a powerful and versatile web scraping tool designed to efficiently extract data from websites. <br>Whether you're gathering data for research, analysis, or other purposes, Spider Scraper provides a simple yet effective way to scrape the web.

## Features

- Efficiently scrape web pages and follow links<br>
- Handle JavaScript-based links and external scripts<br>
- Option to save scraped links to a file<br>
- Aggressive scan mode for faster scraping<br>

## Installation
1. `git clone https://github.com/Anonidentiti/spider-scraper.git `<br>
2 install the required dependencies, run:<br>
  `pip install -r requirements.txt`<br>
  or<br>
  `pip3 install -r requirements.txt` <br>

## Options
Command-Line Options<br>
`-u <url>`: The URL of the website you want to scrape.<br>
`-s <output_file>`: (Optional) The name of the file where the scraped links will be saved.<br>
`-A <aggressive_level>`: (Optional) The level of aggressiveness for the scan. Higher values increase speed but may use more resources.<br>
`f, --forms`: Enables the detection of forms on the page.

## Full usage
`python3 spider.py -u <url> -s <output_file> -A <aggressive_level_in_number> -f `



