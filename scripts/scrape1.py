import re
from json import dump
from tqdm import tqdm
from collections import defaultdict
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import os
import pandas as pd  # Import pandas to read CSV

# constants
BASE_URL = "https://www.domain.com.au"
N_PAGES = range(1, 2)  # Change this as needed

# Load the suburb and postcode data from a CSV file
suburbs_df = pd.read_csv('suburbs.csv')  # Ensure this CSV contains 'suburb' and 'postcode' columns

# begin code
property_metadata = defaultdict(dict)

# Loop through each suburb and its postcode
for index, row in suburbs_df.iterrows():
    suburb = row['suburb'].lower().replace(' ', '-')  # Convert to lowercase and hyphenate
    postcode = row['postcode']

    print(f"Scraping data for {suburb} ({postcode})")

    for page in N_PAGES:
        # Generate the URL for the current suburb and postcode
        url = BASE_URL + f"/rent/{suburb}-vic-{postcode}/?ssubs=0&sort=suburb-asc&page={page}"
        print(f"Visiting {url}")

        try:
            response = urlopen(Request(url, headers={'User-Agent': "PostmanRuntime/7.6.0"}))
            bs_object = BeautifulSoup(response, "lxml")
        except Exception as e:
            print(f"Error visiting {url}: {e}")
            break

        # Find the unordered list (ul) elements which are the results, then
        # find all href (a) tags that are from the base_url website.
        try:
            index_links = bs_object \
                .find("ul", {"data-testid": "results"}) \
                .findAll("a", href=re.compile(f"{BASE_URL}/*"))
        except AttributeError:
            print(f"No more pages after {page - 1} for {suburb} ({postcode})")
            break  # No more pages available

        if not index_links:
            print(f"No more listings found on page {page} for {suburb} ({postcode}). Stopping...")
            break  # Break if no listings found

        # Process each listing link
        url_links = []
        for link in index_links:
            if 'address' in link['class']:
                url_links.append(link['href'])

        print(f"Total URLs collected for {suburb}: {len(url_links)}")

        # For each URL, scrape the property-specific metadata
        for property_url in tqdm(url_links):
            print(f"Visiting property: {property_url}")
            try:
                property_page = urlopen(Request(property_url, headers={'User-Agent': "PostmanRuntime/7.6.0"}))
                property_soup = BeautifulSoup(property_page, "lxml")

                # Scrape property-specific data here
                property_metadata[property_url]['name'] = property_soup \
                    .find("h1", {"class": "css-164r41r"}) \
                    .text.strip()

                property_metadata[property_url]['cost_text'] = property_soup \
                    .find("div", {"data-testid": "listing-details__summary-title"}) \
                    .text.strip()

                rooms = property_soup \
                    .find("div", {"data-testid": "property-features"}) \
                    .findAll("span", {"data-testid": "property-features-text-container"})

                # Scrape rooms
                property_metadata[property_url]['rooms'] = [
                    re.findall(r'\d+\s[A-Za-z]+', feature.text)[0] for feature in rooms
                    if 'Bed' in feature.text or 'Bath' in feature.text
                ]
                # Scrape parking
                property_metadata[property_url]['parking'] = [
                    re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms
                    if 'Parking' in feature.text
                ]

                # Scrape property description
                property_metadata[property_url]['desc'] = re.sub(r'<br\/>', '\n', str(property_soup.find("p"))).strip('</p>')

            except Exception as e:
                print(f"Error scraping property {property_url}: {e}")

# Write the data to a JSON file
output_dir = os.getcwd()  # Current working directory
output_path = os.path.join(output_dir, 'example.json')

if property_metadata:
    with open(output_path, 'w') as f:
        dump(property_metadata, f)
    print(f"Scraped data written to {output_path}")
else:
    print("No data scraped; JSON file not created.")
