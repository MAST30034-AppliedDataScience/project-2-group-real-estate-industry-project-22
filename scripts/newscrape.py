import re
from json import dump, load
from tqdm import tqdm
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import pandas as pd
import os
# import cchardet
import pandas as pd

# Constants
BASE_URL = "https://www.domain.com.au"
N_PAGES = range(1, 2)  # Update this to your liking
delete = []

# Load the suburb and postcode data from a CSV file
suburbs_df = pd.read_csv('../data/raw/postcodes.csv')  # Ensure this CSV contains 'suburb' and 'postcode' columns



def start_scrape():
    url_links = []
    property_metadata = defaultdict(dict)

    #url = r"https://www.domain.com.au" #website url

    # header = { #adding user agent to be get access to the website found by searching my user agent in google
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    # }


    # Loop through each suburb and its postcode
    for index, row in suburbs_df.iterrows():
        suburb = row['locality'].lower().replace(' ', '-')  # Convert to lowercase and hyphenate
        postcode = row['postcode']

        print(f"Scraping data for {suburb} ({postcode})")

            #url = f"{BASE_URL}/rent/?postcode={postcode}&sort=price-desc&page={1}"
            #for page in N_PAGES:
            # Generate the URL for the current suburb and postcode
        url = BASE_URL + f"/rent/{suburb}-vic-{postcode}/?ssubs=0&sort=suburb-asc&page={1}"
        print(f"Visiting {url}")
        response = urlopen(Request(url, headers={'User-Agent': "Mozilla/5.0"}))
        print(response)
        bs_object = BeautifulSoup(response, "lxml")

            # if ((response.status_code == 404)): # 404 is an error code
            #     delete.append(postcode)
            #     print(delete)

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

            #page_number += 1  # Increment the page number for the next iteration

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