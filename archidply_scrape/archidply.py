from bs4 import BeautifulSoup
import requests
import csv
import os
from glob import glob
import pandas as pd


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Scrape function
def scrape(link, fold_name, file_name):
    print("Scraped: " + link)
    try:
        source = requests.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    body = soup.find('div', class_="body-container")

    # Title
    title = body.find('h1').text

    # Image
    img = body.find('div', class_="inner-page-banner")['data-bg']

    # Description
    description = []
    descs = soup.find('h2', string="Introduction").find_next_sibling().find_all('h5')
    for desc in descs:
        description.append(str(desc.text).replace("\n", ""))

    try:
        if soup.find('ul', class_="product-listing").find_all('li'):
            for list_item in soup.find('ul', class_="product-listing").find_all('li'):
                description.append(list_item.text)
    except:
        pass

    # USP
    try:
        usp_list = []
        usps = soup.find('ul', class_="usp-listing").find_all('h6')
        for usp in usps:
            usp_list.append(usp.text)
    except:
        usp_list = ""

    # Standard Size
    try:
        std_size = {}
        size_items = soup.find('ul', class_="size-detail")
        for size_key, size_value in zip(size_items.find_all('h5'), size_items.find_all('h4')):
            std_size[size_key.text] = size_value.text
    except:
        std_size = ""

    # Applications
    try:
        applications = []
        appls = soup.find('ul', class_="application-listing").find_all('h5')
        for appl in appls:
            applications.append(str(appl.text).replace('\xad', ""))
    except:
        applications = ""

    # Technical Specifications
    try:
        specs_img = soup.find('section', id="specification").find('img')['data-src']
    except:
        specs_img = ""

    filepath = f'{fold_name}/{file_name}.csv'

    table_found = False

    # Table
    try:
        if soup.find('section', id="specification").find_all('table'):
            table_found = True
            table = soup.find('section', id="specification").find_all('table')[-1]
            breakss = table.find_all('br')
            for breaks in breakss:
                breaks.extract()
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
            headers.insert(4, "USP")
            headers.insert(5, "Standard size")
            headers.insert(6, "Applications")
            headers.insert(7, "Technical Specifications")

            # Get table data
            for body in table.find_all('tbody'):
                rows = body.find_all('tr')
                for row in rows:
                    items = row.find_all()

                    for item in items:
                        a_temp = str(item.text)
                        a = a_temp.replace("  ", "").replace('\n', "")
                        if a == "":
                            try:
                                a = item.find('img')['src']
                            except:
                                a = ""
                        items[items.index(item)] = str(a)
                    items.insert(0, str(link))
                    items.insert(1, title)
                    items.insert(2, description)
                    items.insert(3, img)
                    items.insert(4, usp_list)
                    items.insert(5, std_size)
                    items.insert(6, applications)
                    items.insert(7, specs_img)

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
        pass

    if not table_found:
        # Sets a flag to indicate if headers have to be written
        if not os.path.exists(filepath):
            flag = 1
        else:
            flag = 0

        # CSV handling
        csv_file = open(filepath, 'a', encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        if flag == 1:
            csv_writer.writerow(["Product Link", "Title", "Image", "Description", "USP", "Standard size", "Applications", "Technical Specifications"])
        csv_writer.writerow([str(link), title, img, description, usp_list, std_size, applications, specs_img])
        csv_file.close()


# Get links from page and formats it as required
def get_links(link):
    # Root Directory naming and creation
    folder_name = link.split('/')[4]
    base = link.split('/')[4]
    create_folder(folder_name)
    try:
        source = requests.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    if soup.find('ul', class_="tab-product").find_all('a'):
        sublinks = soup.find('ul', class_="tab-product").find_all('a')
        for sublink in sublinks:
            folder_name = link.split('/')[4] + "/" + str(sublink['href']).split('/')[5]
            create_folder(folder_name)
            sublink_f = sublink['href']
            try:
                source = requests.get(sublink_f).text
            except:
                print("URL not reachable. Recheck URL")
                exit()

            soup = BeautifulSoup(source, 'lxml')

            product_links = soup.select_one("body > div > section > div > div > div:nth-child(2)").find_all('a')
            for product_link in product_links:
                scrape(product_link['href'], folder_name, str(sublink['href']).split('/')[5])
    else:
        product_links = soup.select_one("body > div > section > div > div > div:nth-child(2)").find_all('a')
        for product_link in product_links:
            scrape(product_link['href'], folder_name, folder_name)

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
    # Replace URL here (Eg:https://www.archidply.com/productcategories/plywood/archidply/)
    # ALWAYS include trailing '/'
    # ---------------------------------------------
    # Single URL
    url = "https://www.archidply.com/productcategories/wpc-board/"
    # ---------------------------------------------

    main = get_links(url)

    # Convert CSV to XLSX
    convert(main)
