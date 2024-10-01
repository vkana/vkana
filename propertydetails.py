import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor

# The list of subdivisions
subdivisions = [
    "9668/77-81 - NCB 14861 (STEUBING FARM UT-7)",
    "20001/694 - NCB 14861 (STEUBING FARM UT-4)",
    "9716/87-92 - NCB 14861 (STEUBING FARM TRACT 2 (ENCLAVE))",
    "9700/46-49 - NCB 14861 (STEUBING FARM UT-3A (ENCLAVE))",
    "9692/142-1 - NCB 14861 (STEUBING FARM UT-3B)"
]

# Function to fetch property data based on subdivision
def fetch_property_data(subdivision):
    url = f"https://esearch.bcad.org/Search/SearchResults?&pageSize=200&keywords=Subdivision:\"{subdivision}\""
    
    # Send a GET request to the API
    response = requests.get(url)
    
    if response.status_code == 200:
        content = response.json()
        properties = content.get("resultsList", [])
        
        for item in properties:
            property_id = item['propertyId']
            propurl = f"https://bexar.trueautomation.com/clientdb/Property.aspx?cid=110&prop_id={property_id}"
            prop_response = requests.get(propurl)

            if prop_response.status_code == 200:
                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(prop_response.content, 'html.parser')

                # Extracting Living Area, Value, and Address
                try:
                    address = soup.find('td', string="Address:").next.next.next.string
                    living_area = soup.find('td', string=re.compile("sqft")).string.split(' ')[0]
                    homesite_value = soup.find('th', string="Value:").next.next.string
                    
                    print(f"{property_id}, {address}, {living_area}, {homesite_value.replace(',', '').replace('$', '')}")
                except Exception as e:
                    pass
                    #print(f"Error parsing data for property ID {property_id}: {e}")

            else:
                print(f"Failed to fetch property details for ID {property_id}. Status code: {prop_response.status_code}")
    else:
        print(f"Failed to fetch data for subdivision '{subdivision}'. Status code: {response.status_code}")

# Use ThreadPoolExecutor to make simultaneous requests
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(fetch_property_data, subdivisions)
