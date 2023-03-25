import random
import re
import time
import requests
import pandas as pd
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

    # Title
    try:
        title = soup.select_one('.product-name').text.strip()
    except:
        title = ''

    # SKU
    sku = soup.find('h3', string=re.compile("SKU:")).text.removeprefix("SKU:").strip()

    # Images
    try:
        images = soup.select_one('.main-image img')['src']
    except:
        images = ""

    data = {
        'Link': str(link),
        'Title': title,
        'SKU': sku,
        'Images': images,
    }

    # Features
    try:
        features_keys = soup.select_one('#product-attribute-specs-table').select('strong')
        for feature_keys in features_keys:
            data[feature_keys.text.replace(":", "").strip()] = feature_keys.find_next_sibling().text
    except:
        pass

    print(data)
    data_df = pd.DataFrame([data])
    return data_df


# Returns all product links from all pages
def get_all_products(url):
    # Delay to prevent getting blocked
    time.sleep(random.randint(0, 1))
    try:
        source = s.get(url).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    # Fetch last pg
    try:
        last_pg = int(soup.select_one('.page.last span:nth-of-type(2)').text)
    except AttributeError:
        last_pg = int(soup.select_one('ul.items.pages-items').find_all('li')[-2].select_one('span:nth-of-type(2)').text)

    all_products_df = pd.DataFrame()

    # Iterate over all pages and scrape
    for x in range(1, last_pg + 1):
        url_n = url.removesuffix('#') + f'?p={x}'
        try:
            source = s.get(url_n).text
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        products = soup.select('.product-item-link')

        for product in products:
            prod_df = scrape(product['href'])
            all_products_df = pd.concat([all_products_df, prod_df])

    return all_products_df


def get_links_and_scrape(url):
    folder_name = "data"
    create_folder(folder_name)
    try:
        source = s.get(url).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    categories = soup.select('.navtext')

    for category in categories:
        # If no subcategories then scrape directly
        if category.find() is None:
            print(category['href'])
            all_products_for_category = get_all_products(category['href'])
            all_products_for_category.to_excel(f"data/{category['href'].split('/')[-1].removesuffix('.html')}.xlsx",
                                               index=False)
        # If multiple filters are available then scrape by categories
        elif category.find_next_sibling().find('a', string="Categories"):
            subcat_links = [cat['href'] for cat in
                            category.find_next_sibling().find('a', string="Categories").find_next_sibling().select(
                                'li a')]
            print(subcat_links)

            for subcat in subcat_links:
                all_products_for_category = get_all_products(subcat)
                all_products_for_category.to_excel(
                    f"data/{subcat.split('/')[-2]}_{subcat.split('/')[-1].removesuffix('.html')}.xlsx", index=False)

        # Scrape by subcategories
        elif category.find_next_sibling().find('a'):
            subcat_links = [cat['href'] for cat in category.find_next_sibling().select('li a')]
            print(subcat_links)

            for subcat in subcat_links:
                all_products_for_category = get_all_products(subcat)
                all_products_for_category.to_excel(
                    f"data/{subcat.split('/')[-2]}_{subcat.split('/')[-1].removesuffix('.html')}.xlsx", index=False)

        else:
            print("Invalid!")


if __name__ == '__main__':
    # Replace URL here
    # Do NOT include trailing '/'
    s = requests.Session()

    URL = "https://www.somanyceramics.com/tiles/wall/ceramic-tiles.html#"

    get_links_and_scrape(URL)
    # scrape(URL)
