import requests
from bs4 import BeautifulSoup
import selenium

# Defining the scraper function --> price, attributes, address
def scrape_page(target_url):
    head={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"}
        
    #requesting the webpage 
    try:
        resp = requests.get(target_url, headers=head)
        print(resp.status_code)
    except Exception as e:
        print(f"Request failed: {e}")

    #parse the webpage
    soup = BeautifulSoup(resp.content, 'html.parser')

    #find the price of property 
    final_prices = []
    try:
        prices = soup.find_all('div', class_='statsValue price')
        for price in prices:    
            final_prices.append(price.get_text())
    except Exception as e:
        print(f"Error finding prices: {e}")

    #find the address of property 
    final_addresses = []
    try:
        addresses = soup.find_all('div', class_='street-address')
        for address in addresses:
            final_addresses.append(address.get_text())
    except Exception as e:
        print(f"Error finding addresses: {e}")
        
    #find property attributes
    final_attributes = []
    try:
        attribute = soup.find_all('div', class_='secondary-stats')
        for attr in attribute:
            final_attributes.append(attr.get_text())
    except Exception as e:
        print(f"Error finding attributes: {e}")

    #download images from the listing
    image = soup.find_all('img')[0]
    image_link = image.get('src')
    
    summary = {
        "price" : final_prices,
        "address" : final_addresses,
        "attributes" : final_attributes,
    }

    return summary, image_link

def scrape_all_links(urls_list):
    properties = []
    images = []
    for url in urls_list:
        property_summary, property_image = scrape_page(url)
        properties.append(property_summary)
        images.append(property_image)

    return properties, images

def image_downloader(image_link):
    r = requests.get(image_link).content
    with open(f"./temp.jpg", "wb+") as f:
        f.write(r)