import re
import requests
import csv
from json import dump, load
from tqdm import tqdm
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import pandas as pd
import pyarrow
import string
import os
import cchardet
import lxml

# Constants
BASE_URL = "https://www.domain.com.au"
VICTORIA_POSTCODES = range(3000, 3001)  # Range of postcodes in Victoria

def start_scrape():
    url_links = []
    property_metadata = defaultdict(dict)

    # Loop through each postcode in Victoria
    for postcode in VICTORIA_POSTCODES:
        page_number = 1
        while True:
            url = f"{BASE_URL}/rent/?postcode={postcode}&sort=price-desc&page={page_number}"
            print(f"Visiting {url}")
            response = urlopen(Request(url, headers={'User-Agent': "Mozilla/5.0"}))
            bs_object = BeautifulSoup(response, "lxml")

            # Find the unordered list (ul) elements which are the results
            try:
                index_links = bs_object.find("ul", {"data-testid": "results"}).findAll(
                    "a", href=re.compile(f"{BASE_URL}/*")
                )
            except AttributeError:
                print(f"No more results for postcode {postcode}. Moving to next postcode.")
                break  # No more results, move to the next postcode

            if not index_links:
                break  # If no links found, exit the loop for this postcode

            for link in index_links:
                # If it's a property address, add it to the list
                if 'address' in link.get('class', []):
                    url_links.append(link['href'])

            page_number += 1  # Increment the page number for the next iteration

    # Scrape basic metadata for each URL
    pbar = tqdm(url_links)
    success_count, total_count = 0, 0

    for property_url in pbar:
        try:
            bs_object = BeautifulSoup(urlopen(Request(property_url, headers={'User-Agent': "Mozilla/5.0"})), "lxml")
            total_count += 1

            # Scrape details
            property_metadata[property_url]['name'] = bs_object.find("h1", {"class": "css-164r41r"}).text.strip()
            property_metadata[property_url]['cost_text'] = bs_object.find("div", {"data-testid": "listing-details__summary-title"}).text.strip()

            # Get rooms and parking
            rooms = bs_object.find("div", {"data-testid": "property-features"}).findAll(
                "span", {"data-testid": "property-features-text-container"}
            )
            property_metadata[property_url]['rooms'] = ", ".join(
                [re.findall(r'\d+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'Bed' in feature.text or 'Bath' in feature.text]
            )
            property_metadata[property_url]['parking'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'Parking' in feature.text]
            )
            property_metadata[property_url]['desc'] = bs_object.find("p").text.strip() if bs_object.find("p") else "N/A"

            success_count += 1

        except AttributeError:
            print(f"Issue with {property_url}")

        pbar.set_description(f"{(success_count / total_count * 100):.0f}% successful")

    # Output to example JSON in data/raw/
    with open('../data/raw/example.json', 'w') as f:
        dump(property_metadata, f)

def convert_to_parquet(filepath: str, output_path: str) -> None:
    """ Function converts a JSON file into a parquet file """
    with open(filepath) as f:
        data = load(f)

    new_data = change_json_format(data)

    # Conversion from JSON -> DataFrame -> Parquet
    df = pd.DataFrame(new_data)
    df.to_parquet(output_path, engine='pyarrow')

    delete_json_file(filepath)

def change_json_format(data: dict) -> dict:
    """ Function renames JSON keys and adds the URL as an item """
    new_data = {}
    for i in data.keys():
        new_name = i.rsplit('/', 1)[-1]
        new_data[new_name] = data[i]
        new_data[new_name]["href"] = i
    return new_data

def delete_json_file(filepath: str) -> None:
    """ Function deletes the JSON file """
    try:
        os.remove(filepath)
        print(f"File '{filepath}' deleted successfully")
    except FileNotFoundError:
        print(f"File '{filepath}' not found")
    except PermissionError:
        print(f"Permission denied: '{filepath}'")
    except Exception as e:
        print(f"An error occurred: {e}")



