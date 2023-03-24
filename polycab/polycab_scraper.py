import re
from bs4 import BeautifulSoup
import requests
import csv
import os
from glob import glob
import pandas as pd


# Creates folder
def create_folder():
    if not os.path.exists(f'{folder_name}'):
        os.mkdir(f'{folder_name}')


# General scrape function. Will execute if no edge cases are matched.
def scrape(link):
    try:
        source = requests.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    # Title
    try:
        try:
            try:
                title = soup.select_one('div > div > div > div.boc_heading.al_left.bgr_dotted > span').text
            except:
                title = soup.select_one('div > div > div > div > div > div > div > h1.boc_heading.al_left > span').text

        except:
            try:
                title = soup.select_one('div > div > div > div > div > div > div > h2.boc_heading.bg_none > span').text
            except:
                title = soup.select_one('div > div > div > div > div > div > div > h2.boc_heading.al_left.bgr_multidotted > span').text
    except:
        try:
            title = soup.select_one('div > div > div > div > div > div > div > h2.boc_heading.al_left.bgr_dotted > span').text
        except:
            title = ""

    # Color
    try:
        color = soup.select_one('div[class=ms-info] > h3').text
    except:
        color = ''

    # Alternate Color
    try:
        try:
            alt_color = soup.select_one('img.vc_single_image-img.attachment-large').attrs['src']
        except:
            alt_color = soup.select_one('img.vc_single_image-img.attachment-boc_medium').attrs['src']
    except:
        alt_color = ''

    # Specification table
    try:
        spec_table = {}
        for (h, data) in zip(soup.select('thead > th'), soup.select('tbody > td')):
            spec_table[h.text] = data.text
    except:
        spec_table = ''

    # Features
    try:
        features_list = []
        features = soup.select('div.wpb_text_column.wpb_content_element > div > p')
        features.pop(0)
        for feature in features:
            try:
                ar = feature.find_previous_sibling('h3').text
                ar = ar + ":"
                features_list.append(ar)
            except:
                pass

            try:
                img2 = feature.find_parent().find_parent().find_parent().find('img')['nitro-lazy-src']
                img2 = "Image link: " + img2
                features_list.append(img2)
            except:
                pass

            features_list.append(feature.text)
    except:
        features_list = []

    # Feature list / Other features
    if soup.select('div.wpb_text_column.wpb_content_element > div > ul > li'):
        try:
            features_li = []
            feat = soup.select('div.wpb_text_column.wpb_content_element > div > ul > li')
            for feature in feat:
                features_li.append(feature.text)
        except:
            features_li = []
    else:
        try:
            features_li = []
            #feat = soup.find_all("div", class_="wpb_column vc_column_container vc_col-sm-4")
            for feature in soup.find_all("div", class_=["wpb_column vc_column_container vc_col-sm-4", "wpb_column vc_column_container vc_col-sm-3"]):
                try:
                    a = feature.find("div", class_="text").text
                    features_li.append(" ".join(str(a).split()))
                except:
                    pass
        except:
            features_li = []

    # Image link
    try:
        try:
            try:
                try:
                    img = soup.select_one('.master-slider.ms-skin-default> div > img:nth-child(1)')['data-src']
                except:
                    img = soup.select_one('.master-slider.ms-skin-default> div > img:nth-child(1)')['src']
            except:
                img = soup.select_one('.product_slider .attachment-full')['src']
        except:
            try:
                img = soup.find("div", class_=re.compile("vc_row wpb_row vc_inner vc_row-fluid lumi-list")).find('img')['data-src']
            except:
                img = soup.find("div", class_=re.compile("vc_row wpb_row vc_inner vc_row-fluid lumi-list")).find('img')['src']
    except:
        img = ''

    # Get name for file from category displayed on website
    try:
        if link[-1] != "/":
            link = link + "/"
        filename1 = link.split('/')[-3]
    except:
        filename1 = 'Uncategorized'

    filepath = f'{folder_name}/{filename1}.csv'

    # Sets a flag to indicate if headers have to be written
    if not os.path.exists(filepath):
        flag = 1
    else:
        flag = 0

    # CSV handling
    csv_file = open(filepath, 'a', encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    if flag == 1:
        csv_writer.writerow(['Link', 'Title', 'Color', 'Alternate colors', 'Technical Specifications', 'Features', 'Other Features', 'Image Link'])
    csv_writer.writerow([str(link), title, color, alt_color, spec_table, features_list, features_li, img])
    csv_file.close()


# If initial page contains products instead of categories, this function is executed.
def scrape_direct(soup, link):
    try:
        category = soup.select_one('div > div > div > div > div > div > div > h1 > span').text
    except:
        category = 'Uncategorised'

    filename = category
    filepath = f'{folder_name}/{filename}.csv'

    # Title
    if 'purocoat' in link:
        products = [prod['href'] for prod in soup.select('.carousel-slider__item > a')]
        print(products)
        for prod in products:
            scrape(prod)
    elif soup.find_all("div", class_=re.compile("wpb_column vc_column_container vc_col-sm-9")) or soup.find_all("div", class_=["wpb_column vc_column_container vc_col-sm-6", "wire-box wpb_column vc_column_container vc_col-sm-6", "black-right wpb_column vc_column_container vc_col-sm-6"]):
        for x in soup.find_all("div", class_=re.compile("wpb_column vc_column_container vc_col-sm-9")):
            title = x.find('h4').text
            feature = x.find('p').text
            img = x.find_previous_sibling().find('img')["src"]
            # Sets a flag to indicate if headers have to be written
            if not os.path.exists(filepath):
                flag = 1
            else:
                flag = 0
            # CSV handling
            csv_file = open(filepath, 'a', encoding="utf-8")
            csv_writer = csv.writer(csv_file)
            if flag == 1:
                csv_writer.writerow(['Product Link', 'Title', 'Feature', 'Image link'])
            csv_writer.writerow([str(link), title, feature, img])
            csv_file.close()
        for m in soup.find_all("div", class_=["wpb_column vc_column_container vc_col-sm-6", "wire-box wpb_column vc_column_container vc_col-sm-6", "black-right wpb_column vc_column_container vc_col-sm-6"]):
            try:
                title1 = m.find('h4').text
                feature1 = m.find('p').text
                img1 = m.find('img')['src']
            except:
                title1 = ""
                feature1 = ""
                img1 = ""

            # Sets a flag to indicate if headers have to be written
            if not os.path.exists(filepath):
                flag = 1
            else:
                flag = 0

            # CSV handling
            csv_file = open(filepath, 'a', encoding="utf-8")
            csv_writer = csv.writer(csv_file)
            if flag == 1:
                csv_writer.writerow(['Product Link', 'Title', 'Feature', 'Image link'])
            csv_writer.writerow([str(link), title1, feature1, img1])
            csv_file.close()
    else:
        for x in soup.find_all("div", class_=re.compile("wpb_column vc_column_container vc_col-sm-8")):
            try:
                title = x.find('h2').text
            except:
                title = link.split("/")[-2]

            try:
                feature = x.find('ul').text
            except:
                feature = ""

            try:
                img = x.find_previous_sibling().find('img')["src"]
            except:
                img = ""

            # Sets a flag to indicate if headers have to be written
            if not os.path.exists(filepath):
                flag = 1
            else:
                flag = 0
            # CSV handling
            csv_file = open(filepath, 'a', encoding="utf-8")
            csv_writer = csv.writer(csv_file)
            if flag == 1:
                csv_writer.writerow(['Product Link', 'Title', 'Feature', 'Image link'])
            csv_writer.writerow([str(link), title, feature, img])
            csv_file.close()


# Get links and return them as a list
def get_links(link):
    try:
        source = requests.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    links = soup.select('div > div.wpb_single_image.wpb_content_element.vc_align_center > figure > a')

    link_list = []
    
    # Checks if page is product page
    is_prod = soup.select('div > div > div > h2 > span')

    try:
        is_prod.pop(0)
        for x in is_prod:
            if "Features" in x:
                is_prod.remove(x)
        if '/appliances/' or '/conduits-accessories/' in link:
            is_prod = []
    except:
        is_prod = []

    if is_prod: # executes if product is detected (No sub-categories)
        scrape_direct(soup, link)
    else:
        for link1 in links:
            link1 = link1.attrs['href']
            if 'https://' not in link1:
                link1 = 'https://polycab.com' + str(link1)
            if link1 != "https://polycab.com#":
                link_list.append(link1)

        # Checks for edge cases and runs required code, else will execute general scrape function
        if "https://polycab.com/products/switches/accessories" in link:
            if link != "https://polycab.com/products/switches/accessories":
                try:
                    category = soup.select_one('div > div > div > div > div > div > div > h1 > span').text
                except:
                    category = 'Uncategorised'

                filename = category
                filepath = f'{folder_name}/{filename}.csv'

                title = soup.select('div > div > div > div > div > div > div > div.boc_heading > span')
                for x in title:
                    try:
                        head = x.text
                    except:
                        pass

                    try:
                        img3 = x.find_parent().find_previous_sibling().find('img')['src']
                    except:
                        img3 = ""
                    # Sets a flag to indicate if headers have to be written
                    if not os.path.exists(filepath):
                        flag = 1
                    else:
                        flag = 0
                    # CSV handling
                    csv_file = open(filepath, 'a', encoding="utf-8")
                    csv_writer = csv.writer(csv_file)
                    if flag == 1:
                        csv_writer.writerow(["Product Link", 'Title', 'Image'])
                    csv_writer.writerow([str(link), head, img3])
                    csv_file.close()
        elif "https://polycab.com/products/switches/ir-touch-switches/" in link:
            try:
                category = soup.select_one('div > div > div > div > div > div > div > h1 > span').text
            except:
                category = 'Uncategorised'

            filename = category
            filepath = f'{folder_name}/{filename}.csv'

            container = soup.find_all('div', class_="wpb_column vc_column_container vc_col-sm-3")

            for x in soup.find_all('div', class_="wpb_column vc_column_container vc_col-sm-3"):
                try:
                    title = x.find('span').text
                    img4 = x.find('img')['src']
                    # Sets a flag to indicate if headers have to be written
                    if not os.path.exists(filepath):
                        flag = 1
                    else:
                        flag = 0
                    # CSV handling
                    csv_file = open(filepath, 'a', encoding="utf-8")
                    csv_writer = csv.writer(csv_file)
                    if flag == 1:
                        csv_writer.writerow(['Product Link', 'Title', 'Image'])
                    try:
                        csv_writer.writerow([str(link), title, img4])
                    except:
                        pass
                    csv_file.close()
                except:
                    pass
        elif "https://polycab.com/products/conduits-accessories/" in link:
            if link != "https://polycab.com/products/conduits-accessories/":
                try:
                    category = soup.select_one('div > div > div > div > div > div > div > h1 > span').text
                except:
                    category = 'Uncategorised'

                filename = category
                filepath = f'{folder_name}/{filename}.csv'

                if category == "POLYCAB CONDUITS & ACCESSORIES":
                    for x in soup.find_all('table'):
                        try:
                            img = x.find("img")["src"]
                        except:
                            img = ""

                        try:
                            name = x.find("th", class_="greybox").text
                        except:
                            name = ""

                        # Sets a flag to indicate if headers have to be written
                        if not os.path.exists(filepath):
                            flag = 1
                        else:
                            flag = 0
                        # CSV handling
                        csv_file = open(filepath, 'a', encoding="utf-8")
                        csv_writer = csv.writer(csv_file)
                        if flag == 1:
                            csv_writer.writerow(['Product Link', 'Title', 'Image'])
                        try:
                            csv_writer.writerow([str(link), name, img])
                        except:
                            pass
                        csv_file.close()
                else:
                    for x in soup.find_all('div', class_="luminate-box wpb_column vc_column_container vc_col-sm-8"):
                        try:
                            name = x.find_parent().find_previous_sibling().find("span").text
                        except:
                            name = ""

                        try:
                            features = x.find("ul").text
                        except:
                            features = ""

                        try:
                            img = x.find_previous_sibling().find("img")["nitro-lazy-src"]
                        except:
                            img = ""

                        # Sets a flag to indicate if headers have to be written
                        if not os.path.exists(filepath):
                            flag = 1
                        else:
                            flag = 0
                        # CSV handling
                        csv_file = open(filepath, 'a', encoding="utf-8")
                        csv_writer = csv.writer(csv_file)
                        if flag == 1:
                            csv_writer.writerow(['Product Link', 'Title', 'Features', 'Image'])
                        try:
                            csv_writer.writerow([str(link), name, features, img])
                        except:
                            pass
                        csv_file.close()
        elif "https://polycab.com/products/switchgear/" in link:
            if link != "https://polycab.com/products/switchgear/":
                try:
                    category = soup.select_one('div > div > div > div > div > div > div > h1 > span').text
                except:
                    category = 'Uncategorised'

                filename = category
                filepath = f'{folder_name}/{filename}.csv'

                try:
                    img = soup.find('img', class_=re.compile("vc_single_image-img attachment-medium"))['src']
                except:
                    img = ""

                features = []
                if soup.find_all('div', class_="space-on-top-head wpb_column vc_column_container vc_col-sm-9"):
                    for x in soup.find_all('div', class_="space-on-top-head wpb_column vc_column_container vc_col-sm-9"):
                        try:
                            feat = x.find('h2').text
                            features.append(feat + ":")
                            desc = x.find('p').text
                            features.append(desc)
                        except:
                            pass
                else:
                    for x in soup.find_all('img', class_=re.compile("vc_single_image-img attachment-full")):
                        image = x['src']
                        features.append(image)

                # Sets a flag to indicate if headers have to be written
                if not os.path.exists(filepath):
                    flag = 1
                else:
                    flag = 0
                # CSV handling
                csv_file = open(filepath, 'a', encoding="utf-8")
                csv_writer = csv.writer(csv_file)
                if flag == 1:
                    csv_writer.writerow(['Product link', 'Name', 'Image', 'Features'])
                try:
                    csv_writer.writerow([str(link), category, img, features])
                except:
                    pass
                csv_file.close()
        elif "https://polycab.com/products/lighting-luminaires/" in link:
            if link != "https://polycab.com/products/lighting-luminaires/":
                try:
                    source = requests.get(link).text
                except:
                    print("URL not reachable. Recheck URL")
                    exit()

                soup = BeautifulSoup(source, 'lxml')

                container = soup.select('div.wpb_text_column.wpb_content_element > div > h3')

                for x in container:
                    try:
                        title = x.text
                    except:
                        title = ""

                    try:
                        if x.find_next_siblings('p'):
                            desc = ""
                            desc_temp = x.find_next_siblings('p')
                            for description in desc_temp:
                                desc = desc + " " + description.text
                        else:
                            desc_temp = x.find_next_sibling().find_all('p')
                            for description in desc_temp:
                                desc = desc + " " + description.text
                    except:
                        desc = ""

                    try:
                        try:
                            img = x.find_parent('div', class_=re.compile("wpb_text_column wpb_content_element")).find_previous_sibling('div', class_=re.compile("wpb_single_image wpb_content_element vc_align_center")).find('img')['src']
                        except:
                            pass
                            img = x.find_parent('div', class_=re.compile("wpb_text_column wpb_content_element")).find_parent('div',class_=re.compile("wpb_text_column wpb_content_element")).find_previous_sibling().find('img')['src']
                    except:
                        img = ""

                    filename = link.split("/")[-2]
                    filepath = f'{folder_name}/{filename}.csv'

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
                            ['Link', 'Title', 'Description', 'Image link'])
                    csv_writer.writerow(
                        [str(link), title, desc, img])
                    csv_file.close()

        elif soup.find_all('div', class_='feature_class wpb_column vc_column_container vc_col-sm-8'):
            try:
                category = soup.select_one('div > div > div > div > div > div > div > h2 > span').text
            except:
                category = 'Uncategorised'

            filename = category
            filepath = f'{folder_name}/{filename}.csv'

            for x in soup.find_all('span', string="Features"):
                try:
                    img = x.parent.parent.parent.parent.find_previous_sibling().find('img')['src']
                except:
                    img = ""

                try:
                    feat1 = x.find_parent().find_next_sibling('div', class_=re.compile('wpb_single_image wpb_content_element vc_align_left')).find('img')['src']
                except:
                    feat1 = ""

                try:
                    try:
                        feat2 = x.find_parent().find_next_sibling('div', class_=re.compile('wpb_single_image wpb_content_element vc_align_left')).find_next_sibling().find('img')['nitro-lazy-src']
                    except:
                        feat2 = x.find_parent().find_next_sibling().find('ul').text
                except:
                    feat2 = ""

                # Sets a flag to indicate if headers have to be written
                if not os.path.exists(filepath):
                    flag = 1
                else:
                    flag = 0
                # CSV handling
                csv_file = open(filepath, 'a', encoding="utf-8")
                csv_writer = csv.writer(csv_file)
                if flag == 1:
                    csv_writer.writerow(['Product Link', "Title", 'Product image','Feature', 'Alternate features'])
                csv_writer.writerow([str(link),category, img, feat1, feat2])
                csv_file.close()
        elif soup.select_one('div.wpb_column.vc_column_container.vc_col-sm-8 > div > div > div > div > ul'):
            scrape_direct(soup, link)
        elif soup.find_all("div", class_="wpb_column vc_column_container vc_col-sm-6"):
            scrape_direct(soup, link)
        elif not link_list:
            scrape(link)

    return link_list


# Special function to scrape HOHM category of website
def hohm(base_link):
    base_link = "https://polycab.com/hohm/shop/page/"
    pg_no = 1
    links = []
    product_links_list = []
    exist = True

    # Loop to get links of all pages by incrementing page nos and stopping if it doesnt exist
    while exist:
        link = base_link + str(pg_no)
        try:
            source = requests.get(link).text
        except:
            print("URL not reachable. Recheck URL")
        soup = BeautifulSoup(source, 'lxml').find('title')
        # Checks if page title shows not found
        if "Page not found – HOHM" in soup.text:
            exist = False
        if exist:
            links.append(link)
        pg_no += 1
    print(links)

    # Scrape links from pages
    for link in links:
        try:
            source = requests.get(link).text
        except:
            print("URL not reachable. Recheck URL")
        soup = BeautifulSoup(source, 'lxml')

        product_links = soup.find('ul', class_="products columns-3").find_all('a')
        for prod in product_links:
            a = prod['href']
            product_links_list.append(a)

    filename = "Hohm"
    filepath = f'{folder_name}/{filename}.csv'

    print(product_links_list)
    # Scrape products
    for link_p in product_links_list:
        print(link_p)
        try:
            source = requests.get(link_p).text
        except:
            print("URL not reachable. Recheck URL")
        soup = BeautifulSoup(source, 'lxml')

        # Title
        try:
            title = soup.find('h1', class_="product_title entry-title").text
        except:
            title = ""

        # Features
        features = []
        try:
            for x in soup.find('div', class_="features").find_all('div', class_="text"):
                features.append(x.text)
        except:
            features = []

        # Image
        try:
            img = soup.find('div', class_="images").find('img')['src']
        except:
            img = ''

        # Sets a flag to indicate if headers have to be written
        if not os.path.exists(filepath):
            flag = 1
        else:
            flag = 0
        # CSV handling
        csv_file = open(filepath, 'a', encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        if flag == 1:
            csv_writer.writerow(['Link', 'Title', 'Feature', 'Image link'])
        csv_writer.writerow([link_p, title, features, img])
        csv_file.close()


# Used to get names for directories
def head_search(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source, 'lxml')
    heading = soup.select('div > div > div > h2 > span')
    try:
        heading.pop(0)
    except:
        heading = []
    return heading


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

        # Checks and deletes inccorectly generated file
        if "polycab.com" in csv_x:
            os.remove(csv_x)

        if "lighting-luminaires.xlsx" in csv_x:
            os.remove(csv_x)

    print("Conversion complete")


if __name__ == '__main__':
    # Replace URL here (Eg:https://polycab.com/products/fans/)
    # Always include trailing '/'
    # ---------------------------------------------
    url = 'https://polycab.com/products/fans/'
    # ---------------------------------------------
    print("Input URL: " + url)
    folder_name = url.split('/')[-2]
    base = url.split('/')[-2]

    if '/hohm/' in url:
        # Scrapes HOHM products (Special Case)
        folder_name = "hohm"
        create_folder()
        hohm(url)
        convert(folder_name)
    else:
        create_folder()

        main_site = get_links(url)

        # Loop to scrape and correctly place files in folders
        for i in main_site:
            specs1 = head_search(i)
            if not specs1:
                folder_name = base + "/" + i.split('/')[5]
                create_folder()
            a = get_links(i)
            for j in a:
                print(j)
                b = get_links(j)
                for k in b:
                    print(k)
                    c = get_links(k)

        # Convert csv to xlsx
        convert(base)
