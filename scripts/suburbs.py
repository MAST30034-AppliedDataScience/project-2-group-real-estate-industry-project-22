import requests
from bs4 import BeautifulSoup
import csv

# URL of the property page
url = "https://www.domain.com.au/1-albert-street-dandenong-vic-3175-17172703"

# User-Agent to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_school_names(soup):
    school_names = []
    # Attempt to locate the relevant section of the page
    # Adjust selectors based on actual content
    for element in soup.find_all(['li', 'p', 'div']):
        if 'km away' in element.get_text():
            school_name = element.get_text(strip=True).split('km away')[0].strip()
            if school_name:
                school_names.append(school_name)
    return school_names

def scrape_school_catchment_zones(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the heading "School Catchment Zones for 1 Albert Street"
    heading = soup.find('h2', string='School Catchment Zones for 1 Albert Street')
    if heading:
        print("Heading found.")
        catchment_section = heading.find_next_sibling('div')  # Adjust if necessary
        if catchment_section:
            print("Catchment section found.")
            school_catchments = extract_school_names(catchment_section)
            print(f"Extracted school names: {school_catchments}")
        else:
            print("Catchment section not found.")
    else:
        print("Heading 'School Catchment Zones for 1 Albert Street' not found.")
    
    return school_catchments

def main():
    school_catchments = scrape_school_catchment_zones(url)
    if school_catchments:
        print(f"Writing {len(school_catchments)} school names to CSV.")
        with open('school_catchments.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['School Name'])
            for school in school_catchments:
                writer.writerow([school])
        print("CSV file created successfully.")
    else:
        print("No school catchments found.")

if __name__ == "__main__":
    main()