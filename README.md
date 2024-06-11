# Spider Scraper

Spider Scraper is a powerful and versatile web scraping tool designed to efficiently extract data from websites. Whether you're gathering data for research, analysis, or other purposes, Spider Scraper provides a simple yet effective way to scrape the web.

## Features

- Efficiently scrape web pages and follow links
- Handle JavaScript-based links and external scripts
- Option to save scraped links to a file
- Aggressive scan mode for faster scraping

## Installation
1. git clone https://github.com/Anonidentiti/spider-scraper.git
2 install the required dependencies, run:
  pip install -r requirements.txt
  or
  pip3 install -r requirements.txt

## options
Command-Line Options
'-u <url>': The URL of the website you want to scrape.
'-s <output_file>': (Optional) The name of the file where the scraped links will be saved.
'-A <aggressive_level>': (Optional) The level of aggressiveness for the scan. Higher values increase speed but may use more resources.

## usage
python3 spider.py -u <url> -s <output_file> -A <aggressive_level_in_number>



