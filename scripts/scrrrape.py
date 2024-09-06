import csv

# List of suburbs and postcodes in Victoria
suburbs = [
    {"name": "Melbourne", "postcode": "3000"},
    {"name": "Richmond", "postcode": "3121"},
    {"name": "Geelong", "postcode": "3220"},
    {"name": "Brunswick", "postcode": "3056"},
    {"name": "Dandenong", "postcode": "3175"},
    {"name": "Fitzroy", "postcode": "3065"},
    # Add more suburbs here
]

# Function to generate URLs from the suburb list
def generate_domain_urls(suburbs):
    base_url = "https://www.domain.com.au/rent/"
    urls = []
    
    for suburb in suburbs:
        suburb_name = suburb["name"].lower().replace(" ", "-")
        postcode = suburb["postcode"]
        suburb_url = f"{base_url}{suburb_name}-vic-{postcode}/"
        urls.append({"suburb": suburb["name"], "url": suburb_url})
    
    return urls

# Generate URLs
urls = generate_domain_urls(suburbs)

# Store the URLs in a CSV file
csv_file = "victoria_suburb_urls.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["suburb", "url"])
    writer.writeheader()
    writer.writerows(urls)

print(f"URLs successfully saved to {csv_file}")
