import requests
import pandas as pd
from bs4 import BeautifulSoup
import os


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Create full link from partial link
def make_link(url):
    if 'https://www.kohler.co.in' not in url:
        new_link = 'https://www.kohler.co.in' + url
    else:
        new_link = url
    return new_link


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
        title = soup.select_one('.koh-product-name').text.replace('&nbsp', ' ')
    except:
        title = ''

    # Description
    description = soup.select_one(".koh-product-short-description").text

    # SKU
    sku = soup.select_one(".koh-product-skus-colors .koh-product-sku").text

    # Price
    price = soup.select_one(".koh-discounted-price").text

    # color
    color = soup.select_one(".koh-product-color").text

    # Images
    try:
        images = [str('https:' + str(img['src'])) for img in soup.select('.koh-product-img')]
    except:
        images = ""

    # Features
    try:
        features = [feature.text for feature in soup.select('.koh-product-features-general li')]
    except:
        features = ''

    if not title:
        try:
            title = description
        except:
            title = ''

    data = {
        'Link': str(link),
        'Title': title,
        'Description': description,
        'SKU': sku,
        'Price': price,
        'Color': color,
        'Images': images,
        'Features': features,
    }

    # Details
    details_headers = soup.select('.koh-product-col-title')
    for details_header in details_headers:
        details_value = details_header.find_next_sibling().text.replace('&nbsp', ' ')
        data[details_header.text] = details_value

    data_df = pd.DataFrame([data])
    print(data_df)
    return data_df


# Returns all product links
def get_links_and_scrape(url):
    folder_name = url.split('/')[-1]
    create_folder(folder_name)
    try:
        source = s.get(url).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    subcategories = [make_link(subcategory['href']) for subcategory in soup.select("ul.koh-available-filters span a")]

    for subcategory in subcategories:
        print(subcategory)
        try:
            source = s.get(subcategory).text
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        prod_links = [make_link(product.find('a')['href']) for product in soup.select('.koh-product-tile')]
        print(prod_links)

        all_data_df = pd.DataFrame()
        for product_link in prod_links:
            prod_df = scrape(product_link)
            all_data_df = pd.concat([all_data_df, prod_df], ignore_index=True)

        all_data_df.to_excel(f"{folder_name}/{str(subcategory).split('/')[-1]}.xlsx", index=False)


if __name__ == '__main__':
    # Replace URL here
    # Eg: "https://www.kohler.co.in/browse/Kitchen"
    # Do NOT include trailing '/'
    s = requests.Session()

    URL = "https://www.kohler.co.in/browse/Kitchen"

    get_links_and_scrape(URL)




