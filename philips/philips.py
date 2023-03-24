import random
import philipshue
import consumerlighting
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os


# Create full link from partial link
def make_link(url):
    if 'https://www.philips.co.in' not in url:
        new_link = 'https://www.philips.co.in' + url
    else:
        new_link = url
    return new_link


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Scrape function
def scrape(link):
    print("Scraped: " + link)
    try:
        source = requests.get(link).text
        time.sleep(random.randint(3, 5))
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    title = soup.select_one('.p-sub-title').text
    sku = soup.select_one('.p-product-ctn').text
    try:
        desc = str(
            soup.select_one('.p-version-elements.p-s-hidden.p-xs-hidden .p-body-copy-02').text).strip().removesuffix(
            ", See all benefits")
    except:
        desc = ""

    img = soup.select_one(".p-is-zoomable img")['src']
    try:
        benefits = [benefit.text for benefit in soup.select("#see-all-benefits li")]
    except:
        benefits = ""
    features = [feature.text for feature in soup.select(".p-feature-title")]

    data = {
        'Link': str(link),
        'Title': title,
        'SKU': sku,
        'Description': desc,
        'Image': img,
        'Benefits': benefits,
        'Features': features
    }

    data_df = pd.DataFrame([data])

    tech_specs_dict = {}
    tech_specs_titles = soup.select(".p-s08__main-list-title")
    for tech_specs_title in tech_specs_titles:
        if tech_specs_title.find_next_sibling().find('ul'):
            tech_specs_values = [value.text.strip() for value in tech_specs_title.find_next_sibling().find_all('li')]
            tech_specs_dict[tech_specs_title.text.strip()] = tech_specs_values
        else:
            tech_specs_values = " ".join(str(tech_specs_title.find_next_sibling().text.strip()).split())
            tech_specs_dict[tech_specs_title.text.strip()] = tech_specs_values

    tech_df = pd.DataFrame([tech_specs_dict])
    data_df = pd.concat([data_df, tech_df], axis=1)
    data_df.to_excel('test.xlsx', index=False)
    return data_df


# Returns all product links and scrapes
def get_links(link):
    try:
        source = requests.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    categories = [str(link['href']) for link in soup.select("li > div > div > ul > li > div > div > ul > li > a") if
                  str(link['href']) not in ['#', 'https://www.philips.co.in/c-w/promotions.html']]
    categories = list(map(lambda x: x.replace(x, (str(x) + '/latest#layout=96')), categories))

    categories = [category for category in categories if '#filter' not in category]

    for category in categories:
        if category == 'https://www.philips.co.in/c-m-au/car-lights/car-air-purifier/latest#layout=96':
            categories.pop(categories.index(category))
            category = 'https://www.philips.co.in/c-m-au/automotive-health-and-wellness/car-air-purifier/latest#layout=96'
            categories.append(category)
        elif category == 'https://www.philips.co.in/c-e/pe/electric-toothbrushes.html/latest#layout=96':
            categories.pop(categories.index(category))
            category = 'https://www.philips.co.in/c-m-pe/electric-toothbrushes/latest#layout=96'
            categories.append(category)
        elif category == 'https://www.philips-hue.com//latest#layout=96':
            categories.pop(categories.index(category))
            philipshue.main(exec_bin, chromedriver_loc)
        elif category == 'https://www.lighting.philips.co.in/consumer/latest#layout=96':
            categories.pop(categories.index(category))
            consumerlighting.main(exec_bin, chromedriver_loc)

    print(categories)
    for category in categories:
        filename = f"{root}/{category.split('/')[-2]}"
        try:
            driver.get(category)
            time.sleep(random.randint(1, 3))
            source = driver.page_source
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        all_products = []

        if soup.find('h3', string="The page you requested can not be found"):
            category = str(category).removesuffix("/latest#layout=96")
            try:
                driver.get(category)
                time.sleep(random.randint(1, 3))
                source = driver.page_source

                soup = BeautifulSoup(source, 'lxml')
            except:
                print("URL not reachable. Recheck URL")
                exit()

        if soup.select_one('.p-product-ctn'):
            filename = f"{root}/{category.split('/')[-1]}"
            master_df = scrape(category)
            print(master_df)
            master_df.to_excel(f"{filename}.xlsx", index=False)
        else:
            try:
                pages = int(soup.select_one('.p-d06__total-pages').text)
            except:
                print("Skipping " + category)
                continue

            for page in range(pages):
                print("Page: " + str(page))
                page_link = category + "&page=" + str(page)
                driver_p = webdriver.Chrome(options=options, service=ser)
                driver_p.maximize_window()
                try:
                    driver_p.get(page_link)
                    time.sleep(random.randint(1, 3))
                    WebDriverWait(driver_p, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'p-pc05v2__card-image-section')))
                    source = driver_p.page_source
                except:
                    print("URL not reachable. Recheck URL")
                    exit()

                soup = BeautifulSoup(source, 'lxml')
                products = [make_link(prod['href']) for prod in soup.select('.p-pc05v2__card-view-product-link')]
                print(len(products), products)
                all_products += products
                driver_p.close()

            print(len(all_products))

            master_df = pd.DataFrame()

            for product in all_products:
                prod_df = scrape(product)
                prod_df = prod_df.loc[:, ~prod_df.columns.duplicated()].copy()
                master_df = pd.concat([master_df, prod_df])

            master_df.to_excel(f"{filename}.xlsx", index=False)


if __name__ == '__main__':
    URL = "https://www.philips.co.in/"

    root = "Philips"
    create_folder(root)

    # Instantiate options
    options = Options()
    # Configure executable path of Chromium browser
    exec_bin = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    options.binary_location = exec_bin

    # Set the location of the webdriver (Webdriver placed in script directory by default)
    chromedriver_loc = r"D:\Desktop\Web Scrapers\chromedriver.exe"
    ser = Service(chromedriver_loc)

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=options, service=ser)
    driver.maximize_window()

    # Get links and scrape
    get_links(URL)
