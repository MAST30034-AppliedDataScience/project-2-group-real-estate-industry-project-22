# built-in imports
import re
import requests
import csv
from json import dump
from tqdm import tqdm
from collections import defaultdict
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

# constants
BASE_URL = "https://www.domain.com.au"
N_PAGES = range(1, 2)  # Update this to your liking

# begin code
url_links = []
property_metadata = defaultdict(dict)

# Open the CSV file once before the loop
with open('test.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    headers = ['url', 'name', 'cost_text', 'rooms', 'parking', 'desc', 'listingid',
               'street', 'suburb', 'postcode', 'propertyType', 'schools', 'features',
               'loan', 'summary', 'suburbInsights']
    writer.writerow(headers)

    # generate list of urls to visit
    for page in N_PAGES:
        url = BASE_URL + f"/rent/melbourne-region-vic/?sort=price-desc&page={page}"
        print(f"Visiting {url}")
        bs_object = BeautifulSoup(urlopen(Request(url, headers={'User-Agent': "PostmanRuntime/7.6.0"})), "lxml")

        # find the unordered list (ul) elements which are the results, then
        # find all href (a) tags that are from the base_url website.
        index_links = bs_object.find("ul", {"data-testid": "results"}).findAll(
            "a", href=re.compile(f"{BASE_URL}/*")  # the `*` denotes wildcard any
        )

        for link in index_links:
            # if it's a property address, add it to the list
            if 'address' in link.get('class', []):
                url_links.append(link['href'])

    # for each url, scrape some basic metadata
    pbar = tqdm(url_links)
    success_count, total_count = 0, 0

    for property_url in pbar:
        try:
            bs_object = BeautifulSoup(urlopen(Request(property_url, headers={'User-Agent': "PostmanRuntime/7.6.0"})), "lxml")
            total_count += 1

            # looks for the header class to get property name
            property_metadata[property_url]['name'] = bs_object.find("h1", {"class": "css-164r41r"}).text.strip()

            # looks for the div containing a summary title for cost
            property_metadata[property_url]['cost_text'] = bs_object.find(
                "div", {"data-testid": "listing-details__summary-title"}
            ).text.strip()

            # get rooms and parking
            rooms = bs_object.find("div", {"data-testid": "property-features"}).findAll(
                "span", {"data-testid": "property-features-text-container"}
            )

            # rooms
            property_metadata[property_url]['rooms'] = ", ".join(
                [re.findall(r'\d+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'Bed' in feature.text or 'Bath' in feature.text]
            )

            # parking
            property_metadata[property_url]['parking'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'Parking' in feature.text]
            )

            # listingID:
            property_metadata[property_url]['listingid'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'listingId' in feature.text]
            )

            # street:
            property_metadata[property_url]['street'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'street' in feature.text]
            )

            # suburb:
            property_metadata[property_url]['suburb'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'suburb' in feature.text]
            )

            # postcode:
            property_metadata[property_url]['postcode'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'postcode' in feature.text]
            )

            # property type:
            property_metadata[property_url]['propertyType'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'apartment' in feature.text 
                 or 'unit' in feature.text or 'house' in feature.text or 'flat' in feature.text]
            )

            # schools:
            property_metadata[property_url]['school'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'school' in feature.text]
            )

            # features:
            property_metadata[property_url]['features'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'feature' in feature.text]
            )

            # loanfinder:
            property_metadata[property_url]['loan'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'loan' in feature.text]
            )

            # listingSummary:
            property_metadata[property_url]['listingsummary'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'summary' in feature.text]
            )

            # suburb insights:
            property_metadata[property_url]['suburbInsights'] = ", ".join(
                [re.findall(r'\S+\s[A-Za-z]+', feature.text)[0] for feature in rooms if 'suburbInsights' in feature.text]
            )

            # property description
            property_metadata[property_url]['desc'] = bs_object.find("p").text.strip() if bs_object.find("p") else "N/A"

            # Write each row to the CSV
            writer.writerow([
                property_url,
                property_metadata[property_url]['name'],
                property_metadata[property_url]['cost_text'],
                property_metadata[property_url]['rooms'],
                property_metadata[property_url]['parking'],
                property_metadata[property_url]['desc'],
                property_metadata[property_url]['listingid'],
                property_metadata[property_url]['street'],
                property_metadata[property_url]['suburb'],
                property_metadata[property_url]['postcode'],
                property_metadata[property_url]['propertyType'],
                property_metadata[property_url]['school'],
                property_metadata[property_url]['features'],
                property_metadata[property_url]['loan'],
                property_metadata[property_url]['listingsummary'],
                property_metadata[property_url]['suburbInsights']
            ])

            success_count += 1

        except AttributeError:
            print(f"Issue with {property_url}")

        pbar.set_description(f"{(success_count / total_count * 100):.0f}% successful")
