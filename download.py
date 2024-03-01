import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

def download_file(session, base_url, file_url, save_dir):
    local_filename = file_url.split('/')[-1]
    file_path = os.path.join(save_dir, local_filename)
    with session.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded {file_url}")

def download_files_from_year(session, year_url, save_dir):
    response = session.get(year_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    file_links = [link for link in soup.find_all('a', href=True) if link['href'].endswith('.nc')]
    for file_link in file_links:
        file_url = urljoin(year_url, file_link['href'])
        download_file(session, base_url, file_url, save_dir)

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

with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(download_files_from_year, session, urljoin(base_url, year_link['href']), save_dir): year_link for year_link in year_links}

for future in as_completed(future_to_url):  # Corrected line here
    year_link = future_to_url[future]
    try:
        data = future.result()
    except Exception as exc:
        print(f'{year_link.text} generated an exception: {exc}')
