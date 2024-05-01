import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

def download_file(session, file_url, save_dir):
    local_filename = file_url.split('/')[-1]
    file_path = os.path.join(save_dir, local_filename)
    with session.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    print(f"Downloaded {local_filename}")

def download_files_from_year(session, year_url, save_dir):
    response = session.get(year_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    file_links = [link for link in soup.find_all('a', href=True) if link['href'].endswith('.nc')]
    with ThreadPoolExecutor(max_workers=5) as executor:
        for file_link in file_links:
            file_url = urljoin(year_url, file_link['href'])
            executor.submit(download_file, session, file_url, save_dir)

# Set up a session
session = requests.Session()
base_url = 'https://www.ncei.noaa.gov/data/sea-surface-temperature-whoi/access/'
save_dir = '/Users/samagra/INCOIS/SST 1988'

# Make sure the save_dir exists
os.makedirs(save_dir, exist_ok=True)

# Get the list of year directories
response = session.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')
year_links = [link for link in soup.find_all('a', href=True) if link['href'].count('/') == 1 and not link.text.startswith('Parent Directory')]

# Download files year by year
for year_link in year_links:
    year_url = urljoin(base_url, year_link['href'])
    print(f"Downloading files from {year_link.text}...")
    download_files_from_year(session, year_url, save_dir)