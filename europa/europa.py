import time
from bs4 import BeautifulSoup
import requests
import csv
import os
from glob import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Create full img link from partial link
def make_img_link(url):
    if 'https://europalocks.com/assets/images/product_details/' not in url:
        new_link = 'https://europalocks.com/assets/images/product_details/' + url
    else:
        new_link = url
    return new_link


# Scrape function
def scrape(link, fold_name):
    print("Scraped: " + link)
    try:
        driver.get(link)
    except:
        print("URL not reachable. Recheck URL")

    soup = BeautifulSoup(driver.page_source, 'lxml')

    if soup.find('section', class_="product_details"):
        container = soup.find('section', class_="product_details")

        # Title
        title = container.find('div', class_="col-md-5").find('h2', class_="font-family").text

        # SKU
        sku = container.find('div', class_="col-md-5").find('h2', class_="font-family mb-4 sku-title").text

        # Description
        try:
            desc = container.find('div', class_="col-md-5").find('p', class_="mb-4").text
        except:
            desc = ""

        # Iterates through different colors
        color_containers = container.find_all('div', class_="form-check-inline")
        for color_container in color_containers:
            main_selector = color_container.find('input')
            # Color
            color = main_selector['data-finish']

            # Image
            img = make_img_link(str(main_selector['data-img']).split(",")[0])

            # Price
            price = main_selector['data-price']

            driver.find_element(By.XPATH, f"//input[@data-finish='{color}']").click()
            soup = BeautifulSoup(driver.page_source, 'lxml')

            # Specifications
            specifications = {}
            specs = soup.find('div', id="technical_info")
            specs_keys_container = specs.find_all('div', class_='col-md-5')
            specs_values_container = specs.find_all('div', class_='col-md-7')
            for specs_key_container, specs_values_container in zip(specs_keys_container, specs_values_container):
                specs_key = specs_key_container.find('p').text
                try:
                    specs_value = specs_values_container.find('p').text
                except:
                    specs_value = specs_values_container.find('span').text
                specifications[specs_key] = str(specs_value).replace("\n", " ")

            # Features and alternate features
            features_list = []
            alt_features_list = []
            feats = soup.find('div', id="special_features").find_all('div', class_="row")
            for feat in feats:
                if feat.find('img'):
                    features = feat.find_all('p')
                    for feature in features:
                        features_list.append(feature.text)
                else:
                    alt_features = feat.find_all('li')
                    for alt_feature in alt_features:
                        alt_features_list.append(alt_feature.text)

            # Applications
            application = []
            appls = soup.find('div', id="applications").find_all('p')
            for appl in appls:
                application.append(appl.text)

            if soup.find('div', id="applications").find_all('li'):
                appls_list = soup.find('div', id="applications").find_all('li')
                for appl_list in appls_list:
                    application.append(appl_list.text)

            file_name = str(link).split("?")[0].split("/")[-1]
            filepath = f'{fold_name}/{file_name}.csv'

            # Sets a flag to indicate if headers have to be written
            if not os.path.exists(filepath):
                flag = 1
            else:
                flag = 0

            # CSV handling
            csv_file = open(filepath, 'a', encoding="utf-8")
            csv_writer = csv.writer(csv_file)
            if flag == 1:
                csv_writer.writerow(
                    ['Product link', 'Title', "SKU", "Description", "Color", "Image", "Price", "Specifications",
                     "Features", "Alt. features", "Applications"])
            csv_writer.writerow(
                [str(link), title, sku, desc, color, img, price, specifications, features_list, alt_features_list,
                 application])
            csv_file.close()
    else:
        try:
            # Title
            title = soup.select_one("section.position-relative > div > div > div > h1").text

            # Description
            description = []
            descs = soup.find_all('p', class_="mb-4")
            for desc in descs:
                description.append(str(desc.text).replace("\n", "").replace("  ", ""))

            # Images
            images = []
            imgs = soup.find_all('section', class_="pt-5")[1].find_all('img', class_="img-fluid")
            for img in imgs:
                images.append(img['src'])

            # Table
            table = soup.find('table')
            # Get table headers
            headers = []
            headers_temp = table.find('thead').find('tr').find_all('th')
            for header_temp in headers_temp:
                header = header_temp.text
                headers.append(header)

            headers.insert(0, "Product Link")
            headers.insert(1, "Title")
            headers.insert(2, "Description")
            headers.insert(3, "Image")

            # Get table data
            for body in table.find_all('tbody'):
                rows = body.find_all('tr')
                for row in rows:
                    items = row.find_all('td')
                    for item in items:
                        a = str(item.text).replace("  ", "")
                        if a == "":
                            try:
                                a = item.find('img')['src']
                            except:
                                a = ""
                        items[items.index(item)] = str(a)
                    items.insert(0, str(link))
                    items.insert(1, title)
                    items.insert(2, description)
                    items.insert(3, images)

                    filepath = f'{fold_name}/{title}.csv'

                    # Sets a flag to indicate if headers have to be written
                    if not os.path.exists(filepath):
                        flag = 1
                    else:
                        flag = 0

                    # CSV handling
                    csv_file = open(filepath, 'a', encoding="utf-8")
                    csv_writer = csv.writer(csv_file)
                    if flag == 1:
                        csv_writer.writerow(headers)
                    csv_writer.writerow(items)
                    csv_file.close()
        except:
            # Title
            title = soup.select_one("main > a > section > div > div > div > h3").text

            # Images
            images = []
            images_temp = soup.find('div', id="pills-tabContent").find_all('img')
            for image_temp in images_temp:
                image = image_temp['src']
                images.append(image)
            try:
                add_img = soup.find('h4', string="Key Evolution of Key").find_parent().find_next_sibling().find('img')[
                    'src']
                images.append(add_img)
            except:
                pass

            filepath = f'{fold_name}/{title}.csv'

            # Sets a flag to indicate if headers have to be written
            if not os.path.exists(filepath):
                flag = 1
            else:
                flag = 0

            # CSV handling
            csv_file = open(filepath, 'a', encoding="utf-8")
            csv_writer = csv.writer(csv_file)
            if flag == 1:
                csv_writer.writerow(["Product link", "Title", "Images"])
            csv_writer.writerow([str(link), title, images])
            csv_file.close()


# Get links from page and formats it as required
def get_links(link):
    # Root Directory naming and creation
    folder_name = link.split('/')[-1]
    base = link.split('/')[-1]
    create_folder(folder_name)
    try:
        source = requests.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    links = []

    try:
        containers = soup.find('ul', id="productTab").find_all('a')

        for container in containers:
            link = container['href']
            links.append(link)

        for link in links:
            try:
                source = requests.get(link).text
            except:
                print("URL not reachable. Recheck URL")
                exit()

            soup = BeautifulSoup(source, 'lxml')

            prod_containers = soup.find('section', class_="cd-gallery").find_all('a')
            for prod_container in prod_containers:
                product_link = str(prod_container['href']).replace(" ", "%20").replace("\n", "")
                folder_name = base + "/" + str(product_link).split("?")[0].split("/")[-1]
                create_folder(folder_name)
                scrape(product_link, folder_name)
    except:
        containers = soup.find('div', class_="services").find_all('a')
        for container in containers:
            link = container['href']
            links.append(link)

        for link in links:
            folder_name = base + "/" + str(link).split("/")[-1]
            create_folder(folder_name)
            scrape(link, folder_name)
    return base


# Converts all csv files to xlsx and deletes csv
def convert(base_file):
    print("Beginning conversion")
    PATH = fr"{os.getcwd()}\{base_file}"
    EXT = "*.csv"
    all_csv_files = [file
                     for path, subdir, files in os.walk(PATH)
                     for file in glob(os.path.join(path, EXT))]

    for x in all_csv_files:
        read_file = pd.read_csv(fr'{x}')
        csv_x = x.replace(".csv", ".xlsx")
        read_file.to_excel(fr'{csv_x}', index=None, header=True)
        os.remove(x)

    print("Conversion complete")


if __name__ == '__main__':
    # Replace URL here (Eg: https://europalocks.com/main_door_locks)
    # Do NOT include trailing '/'
    # ---------------------------------------------
    url = 'https://europalocks.com/kms'
    # ---------------------------------------------

    # Instantiate options
    opts = Options()

    # Configure executable path of Chromium browser
    opts.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    opts.add_argument("--disable-gpu");

    # Set the location of the webdriver (Webdriver placed in script directory)
    s = Service(os.getcwd() + r"\chromedriver.exe")

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts, service=s)
    driver.set_page_load_timeout(100)
    driver.maximize_window()

    # Get links and scrape
    main_site = get_links(url)

    # Close browser window
    driver.close()

    # Convert CSV to XLSX
    convert(main_site)
