import requests
from bs4 import BeautifulSoup as bs
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import re
import csv
from urllib.parse import urljoin, urlparse

base_url = 'https://www.hamilton.ca'
start_url = base_url

visited_urls = set()
all_aspx_links = set()
all_pdf_links = set()
lock = threading.Lock()
max_depth = 3  # Maximum depth to prevent infinite recursion

# Function to fetch and parse a web page
def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for _ in range(5):  # Retry up to 5 times
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return bs(response.content, 'html.parser')
            else:
                print(f"Failed to retrieve the page {url}. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying...")
            time.sleep(2 ** _ + random.random())
    return None

# Function to extract links from a single page
def extract_links(soup):
    aspx_links = set()
    pdf_links = set()
    a_tags = soup.find_all('a', href=True)
    base_domain = urlparse(base_url).netloc
    keywords = [
        'law','bylaw','dsu', 'dwelling-unit', 'additional-dwelling-unit', 'accessory-dwelling-unit', 
        'additional-residential-unit', 'backyard-home', 'basement-apartment', 'carriage-house', 
        'coach-house' , 'garage-suite', 'garden', 'In-law-suite', 'laneway-house', 'laneway-suite', 
        'second-unit', 'secondary-dwelling-unit', 'secondary-dwelling', 'secondary-suite', 'tiny-house',
        'development-charge-reduction', 'development-charge', 'pre-approved-plan', 'preapproved-plan', 
        'pre-approved-plan', 'adu-prototypes', 'permit-streamlining', 'building-permit', 
        'expedited-permit-processing-time', 'permit-streamlining', 'License-Streamlining', 'zoning', 
        'design-regulation-relief', 'regulations', 'relief', 'deed-restricted','deed','dedicated-affordable-housing',
        'affordable-housing', 'amnesty-program','legalization', 'unpermitted-unit', 'free-pre-application-review', 
        'homeowner-loan', "homeowner-grant", 'adu-financing program', "adu-financing"
    ]
    words_re = re.compile("|".join(map(re.escape, keywords)), re.IGNORECASE)
    for a_tag in a_tags:
        href = a_tag['href']
        title = a_tag.get_text(strip=True)
        # Skip JavaScript-based links and malformed URLs
        if 'javascript:' in href.lower() or 'String.fromCharCode' in href:
            continue
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)
        if parsed_url.netloc == base_domain:
            if href.endswith('.pdf') and (words_re.search(href) or words_re.search(title)):
                pdf_links.add((title.lower(), full_url))
            elif words_re.search(href) or words_re.search(title):
                aspx_links.add((title.lower(), full_url))
    return aspx_links, pdf_links

# Function to visit and collect links recursively
def visit_page(url, depth):
    if depth > max_depth:
        return
    with lock:
        if url in visited_urls:
            return
        visited_urls.add(url)
    time.sleep(0.5 + random.random())
    soup = fetch_page(url)
    if soup is not None:
        aspx_links, pdf_links = extract_links(soup)
        with lock:
            all_aspx_links.update(aspx_links)
            all_pdf_links.update(pdf_links)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(visit_page, link[1], depth + 1) for link in aspx_links]
            for future in as_completed(futures):
                future.result()

# Start the link collection process
visit_page(start_url, 0)

# Save the collected .aspx links to a CSV file
with open('hamilton_aspx_links.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Link"])
    for link in all_aspx_links:
        writer.writerow(link)

# Save the collected .pdf links to a CSV file
with open('hamilton_pdf_links.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Link"])
    for link in all_pdf_links:
        writer.writerow(link)

print("Collected .aspx and .pdf links from 'https://www.hamilton.ca/' have been saved to CSV files.")
