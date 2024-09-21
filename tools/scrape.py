import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, datetime, timedelta
import re
import os
import time
import logging
from typing import List, Dict
from collections import defaultdict

base_russia_url = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
base_ukraine_url = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"

logging.basicConfig(filename='logs/scraper.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_archive_urls(url: str, start_date: date, end_date: date) -> Dict[date, str]:
    logging.info(f"Fetching archive URLs for {url}")
    cdx_api_url = "https://web.archive.org/cdx/search/cdx"
    
    params = {
        'url': url,
        'matchType': 'exact',
        'from': start_date.strftime('%Y%m%d'),
        'to': end_date.strftime('%Y%m%d'),
        'output': 'json',
        'fl': 'timestamp,original'
    }
    
    try:
        response = requests.get(cdx_api_url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching archive URLs: {e}")
        return {}
    
    # Skip the first element as it contains column headers
    daily_urls = defaultdict(list)
    for item in data[1:]:
        timestamp = item[0]
        original_url = item[1]
        archive_date = datetime.strptime(timestamp, '%Y%m%d%H%M%S').date()
        daily_urls[archive_date].append((timestamp, original_url))
    
    # Get the last URL for each day
    last_daily_urls = {date: f"https://web.archive.org/web/{sorted(urls)[-1][0]}/{sorted(urls)[-1][1]}" 
                       for date, urls in daily_urls.items()}
    
    logging.info(f"Found {len(last_daily_urls)} days with archive URLs")
    return last_daily_urls

def scrape_data(url: str, country: str, scrape_date: date) -> pd.DataFrame:
    logging.info(f"Scraping data from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')
    materiel = soup.select('article li')

    logging.info(f"Found {len(materiel)} items to process")

    data = []

    for item in materiel:
        system = item.get_text().split(':')[0].strip()
        origin_img = item.find('img')
        if origin_img and 'src' in origin_img.attrs:
            origin = origin_img['src'].split('/')[-1].replace('Flag_of_the_', '').replace('Flag_of_', '').replace('.png', '').replace('_', ' ')
        else:
            origin = 'Unknown'
        
        for status_link in item.find_all('a'):
            status = re.findall(r'destroyed|captured|abandoned|damaged', status_link.text.lower())
            if status:
                data.append({
                    'country': country,
                    'origin': origin,
                    'system': system,
                    'status': status[0],
                    'url': status_link['href'],
                    'date_recorded': scrape_date
                })

    logging.info(f"Processed {len(data)} entries")
    return pd.DataFrame(data)

def create_data(start_date: str, end_date: str, pause_time: int = 15):
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    logging.info(f"Fetching data from {start} to {end}")

    russia_urls = get_archive_urls(base_russia_url, start, end)
    time.sleep(pause_time) 
    ukraine_urls = get_archive_urls(base_ukraine_url, start, end)

    for country, urls in [("Russia", russia_urls), ("Ukraine", ukraine_urls)]:
        for scrape_date, url in urls.items():
            data = scrape_data(url, country, scrape_date)
            time.sleep(pause_time)
            
            if not data.empty:
                filename = f"outputfiles/daily/{country.lower()}_{scrape_date}.csv"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                data.to_csv(filename, index=False)
                logging.info(f"Data saved for {country} on {scrape_date}")
            else:
                logging.info(f"No data found for {country} on {scrape_date}")

if __name__ == "__main__":
    start_date = "2024-01-04"
    end_date = "2024-01-04"
    create_data(start_date, end_date)