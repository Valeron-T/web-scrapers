import requests
import pandas as pd
from bs4 import BeautifulSoup
import os


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Scrape function
def scrape(link, sku, img):
    print("Scraped: " + link)
    try:
        source = s.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    try:
        title = soup.select_one("h1.page-title").text
    except:
        title = soup.select_one(".product-title").find_next_sibling('h1').text.strip()

    if soup.select('#features-pro .col-txt h3'):
        features = [feature.text for feature in soup.select('#features-pro .col-txt h3')]
    elif soup.select('.sldr-tits'):
        features = [feature.text.strip() for feature in soup.select('.sldr-tits')]
    elif soup.select('.prd-info-col .group h2'):
        features = [feature.text.strip() for feature in soup.select('.prd-info-col .group h2')]
    elif soup.find('div', string="FEATURES & BENEFITS"):
        features = [" ".join(str(feat.text).split()) for feat in soup.find('div', string="FEATURES & BENEFITS").find_next_sibling().find_all(['h2','li'])]
    else:
        features = ''

    if soup.select('#specific-pro li'):
        specs = [" ".join(str(spec.text).split()) for spec in soup.select('#specific-pro li')]
    elif soup.find('div', string="SPECIFICATIONS"):
        specs = [" ".join(str(spec.text).split()) for spec in soup.find('div', string="SPECIFICATIONS").find_next_sibling().find_all('li')]
    else:
        specs = ''

    # Delete span tag in appl
    if soup.select('#best_suited_for-data-pro li div.text span'):
        for x in soup.select('#best_suited_for-data-pro li div.text span'):
            x.extract()
        appl = [" ".join(str(spec.text).split()) for spec in soup.select('#best_suited_for-data-pro li div.text')]
    else:
        appl = [" ".join(str(spec.text).split()) for spec in soup.select('h3 + ul li')]

    data = {
        'Link': link,
        'Title': title,
        'SKU': sku,
        'Image': img,
        'Features': features,
        'Specifications': specs,
        'Applications': appl
    }

    minimal_df = pd.DataFrame([data])

    tables_df = pd.DataFrame()

    if soup.find('table'):
        tables = pd.read_html(link)
        for table in tables:
            tables_df = pd.concat([tables_df, table])
        output_df = pd.concat([minimal_df, tables_df])
    else:
        output_df = minimal_df

    return output_df


# Returns all product links and scrapes
def get_links(link):
    try:
        source = s.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    categories = [category['href'] for category in soup.select('.prd-box-item a')]

    if not categories:
        try:
            source = s.get(link).text
        except:
            print("URL not reachable. Recheck URL")
            exit()
        soup = BeautifulSoup(source, 'lxml')

        products = {}

        for product in soup.select('.title-txt a'):
            sku = product.find_parent().find_next_sibling().text
            img = product.find_previous().find_previous_sibling().find('img')['src']
            products[product['href']] = [sku, img]

        ignore_urls = ["https://www.wiprolighting.com/products/indoor/high-bay-mid-bay-luminaires/maxx",
                       "https://www.wiprolighting.com/products/indoor/cold-storage/frostline"]
        all_prod_df = pd.DataFrame()
        for product in products.keys():
            if str(product) in ignore_urls:
                break
            prod_df = scrape(product, products[product][0], products[product][1])
            all_prod_df = pd.concat([all_prod_df, prod_df])
        filename = f"{root}/{link.split('/')[-1]}.xlsx"
        all_prod_df.to_excel(filename, index=False)
    else:
        for category in categories:
            try:
                source = s.get(category).text
            except:
                print("URL not reachable. Recheck URL")
                exit()
            soup = BeautifulSoup(source, 'lxml')

            products = {}

            for product in soup.select('.title-txt a'):
                sku = product.find_parent().find_next_sibling().text
                img = product.find_previous().find_previous_sibling().find('img')['src']
                products[product['href']] = [sku, img]

            ignore_urls = ["https://www.wiprolighting.com/products/indoor/high-bay-mid-bay-luminaires/maxx","https://www.wiprolighting.com/products/indoor/cold-storage/frostline"]
            all_prod_df = pd.DataFrame()
            for product in products.keys():
                if str(product) in ignore_urls:
                    break
                prod_df = scrape(product, products[product][0], products[product][1])
                all_prod_df = pd.concat([all_prod_df, prod_df])

            filename = f"{root}/{category.split('/')[-1]}.xlsx"
            all_prod_df.to_excel(filename, index=False)


if __name__ == '__main__':
    # Replace category URL here
    # Eg: https://www.wiprolighting.com/products/lighting-controls
    # Eg: https://www.wiprolighting.com/products/outdoor
    # Do NOT include trailing '/'
    URL = "https://www.wiprolighting.com/products/lighting-controls"

    # Initialise requests session
    s = requests.Session()

    root = "Wipro"
    create_folder(root)

    # Get links and scrape
    get_links(URL)