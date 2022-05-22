import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv
import os
from glob import glob
import pandas as pd


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Create full link from partial link
def make_link(url):
    new_link = 'https://shop.bajajelectricals.com' + url
    return new_link


# Scrape function
def scrape(base_link, fold_name):
    # Load the HTML page
    try:
        driver.get(base_link)
    except Exception as e:
        print(e)
    # Continue execution after page count is loaded on webpage
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'page-count')))

    # Parse processed webpage with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    # Get last page
    pages = soup.find('p', class_="page-count")
    last_pg = int(str(pages.text).split()[-1])
    
    # Base link to which we append page nos
    base_link_w_pg = base_link + "?page="
    pg_no = 1
    links = []
    product_links_list = []

    # Loop to get links of all pages
    while pg_no <= last_pg:
        f_link = base_link_w_pg + str(pg_no)
        links.append(f_link)
        pg_no += 1

    # Scrape links from pages
    for link in links:
        # Load the HTML page
        driver.get(link)
        # Continue execution after products are loaded on webpage
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'width20')))

        # Parse processed webpage with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'lxml')

        product_containers = soup.find_all('div', class_="width20")

        for product_container in product_containers:
            product_link = make_link(product_container.find("a")['href'])
            product_links_list.append(product_link)

    for product_link in product_links_list:
        print(product_link)
        # Load the HTML page
        driver.get(product_link)
        # Continue execution after price is loaded on webpage
        WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, 'price')))

        time.sleep(2)
        # Parse processed webpage with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Contains title and price
        container = soup.find('div', class_="product_summary")

        # Title
        title = container.find('h1').text

        # Price
        price_temp = container.find('div', class_="price").find('p')
        try:
            price_temp.find('span').extract()
            price = price_temp.text
        except:
            price = container.find('div', class_="price").find('p').text

        # Image
        img_temp = soup.select_one('div.simplebar-content > a > img')['src']
        img = make_link(img_temp)

        # Highlights
        try:
            highlights = []
            highlights_list = soup.find('div', class_="highlight_ul").find_all('li')
            for highlight in highlights_list:
                highlights.append(highlight.text)
        except:
            highlights = ""

        # Specifications
        try:
            specifications = []
            specs_list = soup.find('div', id="specifications").find_all('div', class_="clear spec_tr")
            for specs in specs_list:
                spec_title = specs.find('div', class_="width60 mobilewidth60").text
                spec_value = specs.find('div', class_="width30 mobilewidth30").text
                formatted_spec = str(spec_title) + "-" + str(spec_value).strip()
                specifications.append(formatted_spec)
        except:
            specifications = ""

        file_name = base_link.split("/")[-1].removesuffix('.html')
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
            csv_writer.writerow(['Product link', 'Title', 'Price', "Image link", "Highlights", "Specifications"])
        csv_writer.writerow([str(product_link), title, price, img, highlights, specifications])
        csv_file.close()


# Get links from page and formats it as required
def get_links(link):
    # Load the HTML page
    driver.get(link)

    # Parse processed webpage with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')

    menu_containers = soup.find_all('div', class_="width16")

    for menu_container in menu_containers:
        menu = menu_container.find('div', class_="menu_links")

        links = menu.find_all('a')

        # Name folder based on subcategory
        main_cat_folder = links[0].text
        folder_name = base + "/" + main_cat_folder

        # Delete main category from list
        links.pop(0)
        create_folder(folder_name)

        links_final = []

        # Creates directories and executes scrape function as required
        for link in links:
            if "Catalogue" in str(link):
                links.pop(links.index(link))
            elif "Shop More" in str(link):
                links.pop(links.index(link))
            elif "Spares" in str(link):
                links.pop(links.index(link))
            elif "submenu" in str(link.find_next_sibling()):
                links_temp = link.find_next_sibling().find_all('a')
                for link_temp in links_temp:
                    folder_name = base + "/" + main_cat_folder + "/" + link_temp.text
                    create_folder(folder_name)
                    f_link = make_link(link_temp['href'])
                    links_final.append(f_link)
            else:
                if link.text not in links_final:
                    folder_name = base + "/" + main_cat_folder + "/" + link.text
                    create_folder(folder_name)
                    f_link = make_link(link['href'])
                    links_final.append(f_link)
                    scrape(f_link, folder_name)


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
    # https://shop.bajajelectricals.com/home is starting URL for Bajaj products
    # Do NOT include trailing '/'
    # ---------------------------------------------
    url = 'https://shop.bajajelectricals.com/home'
    # ---------------------------------------------
    print("Input URL: " + url)

    # Instantiate options
    opts = Options()

    # Configure executable path of chromium browser
    opts.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    # Set the location of the webdriver (Webdriver placed in script directory)
    s = Service(os.getcwd() + r"\chromedriver.exe")

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts, service=s)

    folder_name = "Bajaj"
    base = "Bajaj"

    create_folder(folder_name)

    get_links(url)

    # Close browser window
    driver.close()

    # Convert csv to xlsx
    convert(base)
