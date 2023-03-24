import time
import os
import pandas as pd
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


def scrape(link, driver):
    print("Scraped: " + link)
    try:
        driver.get(link)
        time.sleep(random.randint(1,3))
        source = driver.page_source
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    title = soup.select_one('.product-title__title').text.strip()
    desc = soup.select_one('.product-title__description').text.strip()

    img = str(soup.select_one('div.swiper-slide.swiper-slide-active img')['srcset']).split()[0]

    features = [feat.text.strip() for feat in soup.select('.product-marketing-copy__title')]

    tech_specs_dict = {}
    tech_specs_titles = soup.select(".product-specifications-v2__key")
    for tech_specs_title in tech_specs_titles:
        if tech_specs_title.find_next_sibling().find('ul'):
            tech_specs_values = [value.text.strip() for value in tech_specs_title.find_next_sibling().find_all('li')]
            tech_specs_dict[tech_specs_title.text.strip()] = tech_specs_values
        else:
            tech_specs_values = " ".join(str(tech_specs_title.find_next_sibling().text.strip()).split())
            tech_specs_dict[tech_specs_title.text.strip()] = tech_specs_values

    data = {
        'Link': str(link),
        'Title': title,
        'Description': desc,
        'Image': img,
        'Features': features
    }

    data.update(tech_specs_dict)
    data_df = pd.DataFrame([data])
    return data_df


def main(exec_path, driver_path):
    # Instantiate options
    options = Options()
    # Configure executable path of Chromium browser
    options.binary_location = exec_path

    # Set the location of the webdriver (Webdriver placed in script directory by default)
    ser = Service(driver_path)

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=options, service=ser)
    driver.maximize_window()

    link = 'https://www.philips-hue.com/en-in/products/all-products'
    try:
        driver.get(link)
        time.sleep(random.randint(1, 3))
        source = driver.page_source
    except:
        print("URL not reachable. Recheck URL")
        exit()

    prod_links = []
    page_no = 1

    last_pg_reached = False

    while not last_pg_reached:
        link = f'https://www.philips-hue.com/en-in/products/all-products?page={page_no}&sort=relevance'
        try:
            driver.get(link)
            time.sleep(random.randint(1, 3))
            source = driver.page_source
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        next_btn_class = " ".join(soup.select_one('.button--next')['class'])

        products = [prod['href'] for prod in soup.select('a.product-title')]
        prod_links += products

        if 'disabled' not in next_btn_class:
            page_no += 1
        else:
            last_pg_reached = True

    print(prod_links)

    hue_df = pd.DataFrame()

    for prod_link in prod_links:
        prod_df = scrape(prod_link, driver)
        hue_df = pd.concat([hue_df, prod_df])

    hue_df.to_excel('philips-hue.xlsx', index=False)

    driver.close()


if __name__ == '__main__':
    # Script will run from philips.py
    # To run seperatelu optionally, pass browser and chromedriver executable as parameters to main
    main(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
         r"D:\Desktop\Web Scrapers\chromedriver.exe")

