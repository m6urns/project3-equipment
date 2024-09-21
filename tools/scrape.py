import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, datetime, timedelta
import re
import os

base_russia_url = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
base_ukraine_url = "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"

def get_archive_urls(url, start_date, end_date):
    print(f"Fetching archive URLs for {url}")
    cdx_api_url = f"https://web.archive.org/cdx/search/cdx"
    
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
        print(f"Error fetching archive URLs: {e}")
        return []
    
    # Skip the first element as it contains column headers
    archive_urls = [f"https://web.archive.org/web/{item[0]}/{item[1]}" for item in data[1:]]
    print(f"Found {len(archive_urls)} archive URLs within the date range")
    return archive_urls

def scrape_data(url, country, scrape_date):
    print(f"Scraping data from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')
    materiel = soup.select('article li')

    print(f"Found {len(materiel)} items to process")

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

    print(f"Processed {len(data)} entries")
    return pd.DataFrame(data)

def create_data(start_date, end_date):
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    print(f"Fetching data from {start} to {end}")

    russia_urls = get_archive_urls(base_russia_url, start, end)
    ukraine_urls = get_archive_urls(base_ukraine_url, start, end)

    for url in russia_urls + ukraine_urls:
        country = "Russia" if "documenting-equipment.html" in url else "Ukraine"
        # Extract the full timestamp from the URL
        timestamp = url.split('/')[4]
        # Parse the timestamp, including hours, minutes, and seconds
        scrape_date = datetime.strptime(timestamp, '%Y%m%d%H%M%S').date()
        
        data = scrape_data(url, country, scrape_date)
        
        if not data.empty:
            filename = f"outputfiles/{country.lower()}_{scrape_date}.csv"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            data.to_csv(filename, index=False)
            print(f"Data saved for {country} on {scrape_date}")
        else:
            print(f"No data found for {country} on {scrape_date}")

if __name__ == "__main__":
    start_date = "2024-01-04"
    end_date = "2024-01-04"
    create_data(start_date, end_date)