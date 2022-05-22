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
from selenium.webdriver.support.wait import WebDriverWait

# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Scrolls the webpage
def scroll(b, ignore):
    while b:
        try:
            loadMoreButton = driver.find_element(By.XPATH, '//*[@id="more"]')
            time.sleep(2)
            loadMoreButton.click()
            time.sleep(5)
        except Exception as e:
            print(e)
            break
    print("Complete")


# Scrape function
def scrape(link):
    print("Scraped: " + link)
    # Load the HTML page
    try:
        driver.get(link)
        driver.maximize_window()
    except Exception as e:
        print(e)

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'details-header')))

    soup = BeautifulSoup(driver.page_source, 'lxml')

    title = soup.find('div', class_="details-header").find('h1').text

    try:
        description = soup.find('div', id="exhibitor_details_description").find('p').text
    except:
        description = ""

    sectors_list = []

    try:
        sectors = soup.select_one("#exhibitor-details > div > div.row > div.col-md-8 > div:nth-child(3) > div").find_all('span')
        for sector in sectors:
            sectors_list.append(sector.text)

        sectors_string = "; ".join(sectors_list)
    except:
        sectors_string = ""

    try:
        email = soup.find('div', id="exhibitor_details_email").find('a').text
        print(email)
    except:
        email = ""

    name = str(email).split("@")[0]

    try:
        telephone = soup.find('div', id="exhibitor_details_phone").find('a').text
    except:
        telephone = ""

    data = {
        'Company Name': title,
        'Description': description,
        'Sectors': sectors_string,
        'Email': email,
        'Telephone': telephone
    }

    print(data)

    # Write to CSV
    fold_name = link.split('/')[4].removesuffix(".html")
    filepath = f'{fold_name}/pollutec.csv'

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
    links = []
    # Root Directory naming and creation
    folder_name = link.split('/')[4].removesuffix(".html")
    create_folder(folder_name)
    # Load the HTML page
    try:
        driver.get(link)
        driver.maximize_window()
    except Exception as e:
        print(e)

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'company-info')))

    soup = BeautifulSoup(driver.page_source, 'lxml')

    for link in soup.find_all('div', class_="company-info"):
        links.append(link.find('a')['href'])

    return links


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
    # Replace URL here
    URL = "https://www.pollutec.com/fr-fr/liste-exposants.html"

    # Instantiate options
    opts = Options()

    # Configure executable path of chromium browser
    opts.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    # Set the location of the webdriver (Webdriver placed in script directory)
    s = Service(os.getcwd() + r"\chromedriver.exe")

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts, service=s)
    #
    # main_func = get_links(URL)
    # print(main_func)
    #
    # # Calls scrape function
    # # scrape("https://www.pollutec.com/fr-fr/liste-exposants/profil.org-6669ef69-6697-4d84-ae8a-534a9754d95a.html#/")
    # for link in main_func:
    #     scrape(link)

    # Close browser window
    driver.quit()

    # Converts csv to xlsx
    base = URL.split('/')[4].removesuffix(".html")
    convert(base)
