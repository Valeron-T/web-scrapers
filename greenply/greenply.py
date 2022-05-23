import time
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv
import os
from glob import glob
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Create full link from partial link
def make_link(url):
    new_link = 'https://www.greenply.com' + url
    return new_link


# Scrape function
def scrape(link):
    print("Scraped: " + link)
    try:
        source = requests.get(link, verify=False)
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source.content.decode('utf-8'), 'lxml')

    # Title
    title = " ".join(str(soup.find('div',class_="product__detail__title").text).split())

    # Description
    description = " ".join(str(soup.find('div',class_="product__detail__info").text).split())

    # Features
    feature_list = []
    features = soup.find_all('div', class_="product__feature__title")

    for feature in features:
        feature_list.append(feature.text)

    # Images
    images = []
    for img in soup.find('ul', class_="zoom-slider").find_all('li'):
        img_f = img.find('a')['for']
        images.append(make_link(img_f))

    # Data to be written
    data = {
        "Product Link": str(link),
        "Title": title,
        "Description": description,
        "Features": feature_list,
        "Images": images
    }

    # Tabs
    tabs = soup.find_all('div', class_="ui_custome__type")
    # Bases on content in tab, scrape correctly
    for tab in tabs:
        if tab.find('ul'):
            specifications = []
            specs = tab.find_all('li')
            for spec in specs:
                specifications.append(spec.text)
            data["Specifications"] = specifications
        elif tab.find('table'):
            price_list = {}
            sizes = soup.select_one("div > div > table > thead > tr:nth-child(1)").find_all('td')
            prices = soup.select_one("div > div > table > thead > tr:nth-child(2)").find_all('td')
            if str(sizes[0].text) == "Size":
                sizes.pop(0)
                prices.pop(0)
            for size, price in zip(sizes, prices):
                price_list[size.text] = price.text
            data["Prices"] = price_list
        else:
            try:
                add_details = tab.find('p').text
                if add_details != "":
                    data["Additional Details"] = add_details
            except:
                pass

    # Write to CSV
    fold_name = link.split('/')[3]
    file_name = link.split('/')[-2]
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
        csv_writer.writerow(data.keys())
    csv_writer.writerow(data.values())
    csv_file.close()


# Get links from page and formats it as required
def get_links(link):
    # Root Directory naming and creation
    folder_name = link.split('/')[3]
    base = link.split('/')[3]
    create_folder(folder_name)
    try:
        source = requests.get(link, verify=False).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    link_list = []
    links = soup.find('div', class_="our_product_slider_section").find('div', class_="our_product_slider").find_all('a')
    for link_a in links:
        a = make_link(link_a['href'])
        if a != link:
            link_list.append(a)

    for sublink in link_list:
        # Load the HTML page
        try:
            driver.maximize_window()
            driver.get(sublink)
        except Exception as e:
            print(e)

        # Wait untill button to load all products is rendered
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'button__all__product')))

        # Close pop up
        try:
            driver.find_element(By.XPATH, '/html/body/main/div[10]/div/a[2]').click()
        except:
            time.sleep(2)
            driver.find_element(By.XPATH, '/html/body/main/div[10]/div/a[2]').click()

        view_all_products = driver.find_element(By.XPATH, '/html/body/main/div[8]/div/a')

        # Scroll view all products button into view and then click until it disappears
        driver.execute_script("arguments[0].scrollIntoView(true);", view_all_products)
        view_all_products.click()

        try:
            while driver.find_element(By.XPATH, '/html/body/main/div[9]/div/div[2]/a'):
                driver.find_element(By.XPATH, '/html/body/main/div[9]/div/div[2]/a').click()
                time.sleep(1)
        except(NoSuchElementException, StaleElementReferenceException):
            pass

        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Scrape obtained links
        for product_link in soup.find_all('div', class_="prodcut__btn__wrap"):
            product_link_f = make_link(product_link.find('a')['href'])
            scrape(product_link_f)

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
    # Replace category URL here (Eg: https://www.greenply.com/decorative-veneers, https://www.greenply.com/pvc-products)
    # Do not include trailing "/"
    # ------------------------------------
    URL = "https://www.greenply.com/speciality-plywood"
    # ------------------------------------

    # Hide Expired SSL warnings
    disable_warnings(InsecureRequestWarning)
    # Instantiate options
    opts = Options()

    # Configure executable path of chromium browser
    opts.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    # Ignore No SSL in selenium
    opts.add_argument('ignore-certificate-errors')

    # Set the location of the webdriver (Webdriver placed in script directory)
    s = Service(os.getcwd() + r"\chromedriver.exe")

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts, service=s)

    # Get links and scrape
    main_func = get_links(URL)

    # Close browser window
    driver.quit()

    # Convert CSV to XLSX
    convert(main_func)
