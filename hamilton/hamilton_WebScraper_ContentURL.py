import requests
from bs4 import BeautifulSoup as bs
import csv
import time
import random
import re

base_url = 'https://www.hamilton.ca'
kitchener_txt = "hamilton_extracted_content.txt"

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

# Function to extract relevant content
def extract_content(soup):
    content = []
    seen_content = set()

    main = soup.find('main')
    if not main:
        return content

    for tag in main.find_all(['script', 'nav']):
        tag.decompose()

    h1_tag = main.find('h1')
    if h1_tag:
        h1_text = h1_tag.get_text(strip=True)
        if h1_text not in seen_content:
            content.append(h1_text)
            seen_content.add(h1_text)

        next_sibling = h1_tag.find_next(['p', 'ul', 'div'])
        while next_sibling and next_sibling.name in ['p', 'ul', 'div']:
            next_sibling_text = next_sibling.get_text(strip=True)
            if next_sibling_text and next_sibling_text not in seen_content:
                content.append(next_sibling_text)
                seen_content.add(next_sibling_text)
            next_sibling = next_sibling.find_next_sibling(['p', 'ul', 'div'])

    headers = main.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
    for header in headers:
        header_text = header.get_text(strip=True)
        if header_text not in seen_content:
            content.append(header_text)
            seen_content.add(header_text)
        next_sibling = header.find_next_sibling()
        while next_sibling and next_sibling.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
            next_sibling_text = next_sibling.get_text(strip=True)
            if next_sibling_text and next_sibling_text not in seen_content:
                content.append(next_sibling_text)
                seen_content.add(next_sibling_text)
            next_sibling = next_sibling.find_next_sibling()

    tables = main.find_all('table')
    for table in tables:
        rows = []
        for row in table.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
            rows.append("\t".join(cells))
        table_text = "\n".join(rows)
        if table_text not in seen_content:
            content.append(table_text)
            seen_content.add(table_text)

    return content

with open('hamilton_aspx_links.csv', mode='r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    # Open a text file to write the extracted content
    with open(kitchener_txt, mode='w', encoding='utf-8') as output_file:
        for row in csv_reader:
            title, href = row
            print(f"Processing: {title} - {href}")
            soup = fetch_page(href)
            if soup:
                content = extract_content(soup)
                # Need to optimize the keyword list ====Xiaoxin====
                keywords = ['law','bylaw','dsu ', 'dwelling unit', 'additional dwelling unit', 'accessory dwelling unit', 'additional residential unit', 'backyard home', 'basement apartment', 'carriage house', 'coach house' , 'garage suite', 'garden ', 'In-law suite', 'laneway house', 'laneway suite', 'second unit', 'secondary dwelling unit', 'secondary dwelling', 'secondary suite', 'tiny house','development charge reduction', 'development charge', 'pre-approved plan', 'preapproved plan', 'pre approved plan', 'adu prototypes', 'permit streamlining', 'building permit', 'expedited permit processing time', 'permit streamlining', 'License Streamlining', 'zoning ', 'design regulation relief', 'regulations ', 'relief ', 'deed restricted','deed ','dedicated affordable housing','affordable housing', 'amnesty program','legalization ', 'unpermitted unit', 'free pre-application review', 'homeowner loan', "homeowner grant", 'adu financing program', "adu financing"]
                words_re = re.compile("|".join(map(re.escape, keywords)), re.IGNORECASE)
                content_str = " ".join(content)
                if words_re.search(title.lower()) or words_re.search(content_str.lower()):
                    output_file.write(f"Title: {title}\n")
                    output_file.write("\n".join(content))
                    output_file.write("\n\n\n")
                    #output_file.write("\n======End of this article======\n\n\n")
                time.sleep(0.2 + random.random())