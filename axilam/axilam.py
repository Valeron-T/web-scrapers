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
    url = str(url).replace('../../', "")
    if 'https://axilam.com/' not in url:
        new_link = 'https://axilam.com/' + url
    else:
        new_link = url
    return new_link


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
        title = soup.select_one('.product-name h1').text.strip()
    except:
        title = ''

    # SKU
    sku = " ".join(str(soup.select_one(".item-code").text).split()).removeprefix('Item code: ')

    # MRP
    try:
        mrp = " ".join(str(soup.select_one(".old-price > .price").text).split())
    except:
        mrp = " ".join(str(soup.select_one(".regular-price > .price").text).split())

    # Offer price
    try:
        price = " ".join(str(soup.select_one(".special-price > .price").text).split())
    except:
        price = ''

    # Images
    try:
        images = soup.select_one('#product_main_image')['src']
    except:
        images = ""

    # Features
    try:
        features_u = [" ".join(str(feature.text).split()) + '_' for feature in soup.select_one('.short-description .std').contents]
        for x in features_u:
            if x[0] == '_':
                features_u.remove(x)
        features = [str(feat).removesuffix('_') for feat in features_u]
    except:
        features = ''

    # Unit
    unit = soup.select_one('.unit').text.strip().removeprefix('Unit:').strip()

    data = {
        'Link': str(link),
        'Title': title,
        'SKU': sku,
        'MRP': mrp,
        'Offer Price': price,
        'Unit': unit,
        'Images': images,
        'Features': features,
    }

    data_df = pd.DataFrame([data])
    return data_df


def get_links_and_scrape(url):
    folder_name = 'data'
    create_folder(folder_name)
    try:
        source = s.get(url).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    subcategories = soup.select(".sub-heading")

    filename = soup.select_one('.aboutus_textcont h2 span').text.strip()

    subcat_df = pd.DataFrame()
    for subcategory in subcategories:
        products = subcategory.find_next_sibling().select('li')

        for product in products:

            img = make_link(product.select_one('a')['href'])
            sku = product.select_one('span').text
            print(img, sku)

            prod_df = pd.DataFrame([{
                'Link': url,
                'Title': subcategory.text.strip(),
                'Code': sku,
                'Image': img,
            }])

            subcat_df = pd.concat([subcat_df, prod_df])
    subcat_df.to_csv(f"data/{filename}.csv", index=False)


if __name__ == '__main__':
    # Do NOT include trailing '/'
    s = requests.Session()

    # Replace category URL here
    URL = "https://axilam.com/axilam-products/axilam-54/instalam.html"

    get_links_and_scrape(URL)
