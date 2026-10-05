# GMIU College Circular Scraper API

## Project Overview
This project is a web scraping API that collects circular information from the GMIU website and provides it in JSON format.

## Technologies Used
- Python
- Flask
- BeautifulSoup
- Requests
- SQLite
- REST API

## Features
- Scrapes circular titles, dates, and links.
- Provides circular information in JSON format.
- Stores circular data in an SQLite database.
- Supports searching circulars by title.
- Updates existing circular records.

## API Endpoints

### Home
GET /

Returns the API status.

### All Circulars
GET /api/circulars

Returns circular information in JSON format.

### Search Circulars
GET /api/circulars?search=exam

Returns circulars matching the search keyword.

## Project Structure

college-scraper-api/
- app.py
- scraper.py
- database.py
- gmiu.db
- README.md
- venv/

## How to Run

1. Activate the virtual environment.
2. Install the required packages.
3. Run the Flask application using:

python app.py

4. Open http://127.0.0.1:5000 in a browser.
