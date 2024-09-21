import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, datetime, timedelta
import re
import os

base_russia_url = "https://web.archive.org/web/*/https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
base_ukraine_url = "https://web.archive.org/web/*/https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"

def get_archive_urls(base_url, start_date, end_date):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select('a[href^="/web/"]')
    
    archive_urls = []
    for link in links:
        try:
            url_date = datetime.strptime(link['href'].split('/')[2], '%Y%m%d%H%M%S')
            if start_date <= url_date.date() <= end_date:
                archive_urls.append(f"https://web.archive.org{link['href']}")
        except (ValueError, IndexError):
            continue
    
    return archive_urls

def scrape_data(url, country, scrape_date):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    materiel = soup.select('article li')

    data = []

    for item in materiel:
        system = item.get_text().split(':')[0].strip()
        origin = item.find('img')['src'].split('/')[-1].replace('Flag_of_the_', '').replace('Flag_of_', '').replace('.png', '').replace('_', ' ')
        
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

    return pd.DataFrame(data)

def create_data(start_date, end_date):
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    russia_urls = get_archive_urls(base_russia_url, start, end)
    ukraine_urls = get_archive_urls(base_ukraine_url, start, end)

    for url in russia_urls + ukraine_urls:
        country = "Russia" if "documenting-equipment.html" in url else "Ukraine"
        scrape_date = datetime.strptime(url.split('/')[4], '%Y%m%d%H%M%S').date()
        
        data = scrape_data(url, country, scrape_date)
        
        if not data.empty:
            filename = f"outputfiles/daily/{country.lower()}_{scrape_date}.csv"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            data.to_csv(filename, index=False)
            print(f"Data saved for {country} on {scrape_date}")

if __name__ == "__main__":
    # start_date = input("Enter start date (YYYY-MM-DD): ")
    # end_date = input("Enter end date (YYYY-MM-DD): ")
    start_date = "2022-03-24"
    end_date = "2022-04-20"
    create_data(start_date, end_date)