import pandas as pd
import requests
import os

# Path to the CSV file and output directory
csv_file_path = 'hamilton_pdf_links.csv'
output_dir = '..\downloads\hamilton'

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(csv_file_path)

titles = df['Title']
urls = df['Link']

def clean_and_truncate_title(title, max_length=100):
    clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
    return clean_title[:max_length]

for title, url in zip(titles, urls):
    response = requests.get(url)
    if response.status_code == 200:
        clean_title = clean_and_truncate_title(title)
        pdf_path = os.path.join(output_dir, f'{clean_title}.pdf')
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {pdf_path}")
    else:
        print(f"Failed to download: {url}")

# List the files in the output directory to verify the downloads
downloaded_files = os.listdir(output_dir)
print(downloaded_files)