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
def scrape(link, fold_name):
    print("Scraped: " + link)
    try:
        source = requests.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    # Title
    title = soup.find('h1', class_="page_title").text

    # Description
    description = []
    #
    if soup.select_one("body > div.body_wrap > div > div.page_content_wrap.page_paddings_yes > div > div > article > section > div:nth-child(2) > div:nth-child(1) > div > div > div > div"):
        descs = soup.select_one("body > div.body_wrap > div > div.page_content_wrap.page_paddings_yes > div > div > article > section > div:nth-child(2) > div:nth-child(1) > div > div > div > div")
    else:
        descs = soup.find('section', class_="post_content").find_all('span')

    for desc in descs:
        description.append(" ".join(str(desc.text).split()))

    # Images
    images = []
    if soup.find('div', class_="vc_item"):
        imgs = soup.find_all('div', class_="vc_item")
        for img in imgs:
            image = img.find('img')['src']
            images.append(image)
    else:
        try:
            img = soup.find('img', class_="vc_single_image-img")['src']
            images.append(img)
        except:
            pass

    data = {
        "Link": str(link),
        "Title": title,
        "Description": description,
        "Images": images
    }

    # Optional details
    try:
        details = soup.select_one("section > div.vc_row.wpb_row.vc_row-fluid.head-pad > div > div > div > div > div > div").find_all(recursive=False)
    except:
        try:
            details = soup.select_one(
                "body > div.body_wrap > div > div.page_content_wrap.page_paddings_yes > div > div > article > section > div:nth-child(2) > div:nth-child(1) > div > div > div.vc_row.wpb_row.vc_inner.vc_row-fluid > div > div > div > div > div").find_all(
                recursive=False)
        except:
            try:
                details = soup.select_one("section > div:nth-child(3) > div > div > div > div > div").find_all(recursive=False)
            except:
                details = ""

    if details != "":
        for detail in details:
            if detail.name == 'h5':
                head = detail.text
            elif detail.name == 'p':
                if head in data:
                    data[str(head)].append(" ".join(str(detail.text).split()))
                else:
                    data[head] = [detail.text]
            elif detail.name == 'ul':
                list_items = detail.find_all('li')
                details_list = []
                for list_item in list_items:
                    details_list.append(list_item.text)
                if head in data:
                    data[str(head)].append(details_list)
                else:
                    data[head] = details_list

    # Table
    if soup.find('div', class_="divTableBody"):
        table = soup.find('div', class_="divTableBody")
        breakss = table.find_all('br')
        for breaks in breakss:
            breaks.extract()
        # Get table headers
        headers = []
        headers_temp = table.find('div', 'divTableRow').find_all('div', class_="divTableCell")
        for header_temp in headers_temp:
            header = " ".join(str(header_temp.text).split())
            headers.append(header)
        table.find('div', 'divTableRow').extract()

        # Get table data
        for row in table.find_all('div', 'divTableRow'):
            items = row.find_all('div', class_="divTableCell")

            for item in items:
                a_temp = str(item.text)
                a = a_temp.replace("  ", "").replace('\n', "")
                if a == "":
                    try:
                        a = item.find('img')['src']
                        if a:
                            a = "Available"
                    except:
                        a = ""
                items[items.index(item)] = str(a)

            combined_headers = list(data.keys()) + headers
            combined_values = list(data.values()) + items

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
                csv_writer.writerow(combined_headers)
            csv_writer.writerow(combined_values)
            csv_file.close()
    else:
        # Write to CSV
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
            csv_writer.writerow(data.keys())
        csv_writer.writerow(data.values())
        csv_file.close()


# Get links from page and formats it as required
def get_links(link):
    # Root Directory naming and creation
    folder_name = link.split('/')[2]
    base = link.split('/')[2]
    create_folder(folder_name)
    try:
        source = requests.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    categories = soup.find('span', string="Products").find_parent().find_next_sibling('ul').find_all('li',recursive=False)

    for category in categories:
        cat_title = category.find('a').find('span').text
        folder_name = link.split('/')[2] + "/" + str(cat_title).strip()
        create_folder(folder_name)
        # If subcategories are detected then scrape those links, else scrape category
        if category.find('ul'):
            subcategories = category.find('ul').find_all('a')
            for subcategory in subcategories:
                subcat_title = str(subcategory.text).replace("/", " ")
                sub_link = str(subcategory['href'])
                if subcat_title:
                    if sub_link != "#":
                        folder_name = link.split('/')[2] + "/" + str(cat_title).strip() + "/" + str(subcat_title).strip()
                        create_folder(folder_name)
                        scrape(sub_link, folder_name)
        else:
            sub_link = category.find('a')['href']
            scrape(sub_link, folder_name)
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
    # Do NOT include trailing '/'
    # ---------------------------------------------
    url = "http://simla.co.in"
    # ---------------------------------------------

    # Get links and scrape
    main = get_links(url)

    # Convert CSV to XLSX
    convert(main)
