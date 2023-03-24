import json
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Scrape function
def scrape(link):
    print("Scraped: " + link)
    try:
        source = s.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    title = soup.select_one('.entry-title').text
    desc = soup.select_one('div.product-desc > p').text
    features = [feat.text for feat in soup.select('.font-weight-bold p')]
    data = {
        'Link': link,
        'Title': title,
        'Description': desc,
        'Features': features,
    }

    prod_df = pd.DataFrame()

    # Check if multiple variations exist for product and scrape accordingly
    if len(soup.select("ul[role='radiogroup'] li")) > 1:
        product_vars = json.loads(soup.select_one('form.variations_form')['data-product_variations'])
        for product_var in product_vars:
            price = product_var['display_price']
            data['Price'] = price
            var_id = product_var['variation_id']

            url = "https://www.aosmithindia.com/wp-admin/admin-ajax.php"

            payload = f"action=update_variation_specifications&variation_id={var_id}"
            headers = {
                "authority": "www.aosmithindia.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.6",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://www.aosmithindia.com",
                "referer": "https://www.aosmithindia.com/product/water-heater/storage-water-heater/heatbot-wifi/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1"
            }

            source = requests.request("POST", url, data=payload, headers=headers).text

            soup = BeautifulSoup(source, 'lxml')

            image = soup.select_one('img')['src']
            data['Image'] = image

            headers = soup.select('h5')
            for header in headers:
                value = " ".join(header.find_next_sibling().text.split())
                data[" ".join(header.text.split()).replace('"','')] = value

            var_df = pd.DataFrame([data])
            prod_df = pd.concat([prod_df, var_df])
    else:
        try:
            data['Price'] = soup.select_one('.product-details-wrapper bdi').text
        except:
            pass
        image = soup.select_one('div.woocommerce-product-gallery__image img')['src']
        data['Image'] = image
        headers = soup.select('#product-specification h5')
        for header in headers:
            value = " ".join(header.find_next_sibling().text.split())
            data[" ".join(header.text.split()).replace('"', '')] = value
        var_df = pd.DataFrame([data])
        prod_df = pd.concat([prod_df, var_df])

    return prod_df


if __name__ == '__main__':
    # Initialise request session
    s = requests.Session()

    # Replace category url here
    # Do not include trailing '/'
    URL = 'https://www.aosmithindia.com/product-category/water-heater'

    try:
        source = s.get(URL).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    links = soup.select('#product-listing .tab-pane.active a[href^="https://www.aosmithindia.com/product/"]')

    master_df = pd.DataFrame()
    for link in links:
        product_df = scrape(link['href'])
        master_df = pd.concat([master_df, product_df])

    master_df.to_excel(f"{URL.split('/')[-1]}.xlsx", index=False)
