import requests
from bs4 import BeautifulSoup
import os
import pandas as pd


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Create full link from partial link
def make_link(url_l):
    new_link = url_l
    if 'https://www.rrkabel.com' not in new_link:
        new_link = 'https://www.rrkabel.com' + url_l
    return new_link


# Scrape function
def scrape(link):
    print("Scraped: " + link)
    try:
        source = s.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    # Remove certificate info tag to parse details correctly
    try:
        soup.select_one(".certificate-info").extract()
    except:
        pass

    # Details Container
    container = soup.select_one(".prctcont").find_all(recursive=False)

    images = []

    data_df = pd.DataFrame()

    # Images
    for img in soup.select(".size-full"):
        images.append(make_link(img['src']))

    # Data dict
    data = {
        'Link': str(link),
        'Title': soup.find('h1').text,
        'Images': images,
    }

    current_heading = ''
    data_to_write = []

    # Loop to write data after every tage with class="title" into the dictionary. ALso ignore tables.
    for item in container:
        if item.has_attr('class'):
            if item['class'][0] == 'title':
                if data_to_write:
                    data[str(current_heading)] = data_to_write
                current_heading = item.text
                data_to_write = []
        elif item.name == 'div':
            pass
        elif item.name == 'p' or item.name == 'ul':
            cur_strong_heading = ''
            strong_data = []
            # if p contains strong tags then split each subheading into seperate dictionary entry
            if item.find('strong'):
                for element in item:
                    if element.name == 'strong':
                        if strong_data:
                            strong_data = [i for i in strong_data if i]
                            data[cur_strong_heading] = strong_data
                        cur_strong_heading = str(element.text).removesuffix(" :")
                        strong_data = []
                    else:
                        strong_data.append(str(element.text).strip())
            else:
                data_to_write.append(" ".join(str(item.text).split()))
    df_dictionary = pd.DataFrame([data])
    data_df = pd.concat([data_df, df_dictionary], ignore_index=True)

    # Scrape tables if exist
    try:
        tables = pd.read_html(soup.prettify())
        formatted_df = pd.DataFrame()
        for table in tables:
            try:
                formatted_df = pd.concat([formatted_df, table])
            except:
                table = table.reset_index(inplace=True, drop=True)
                formatted_df = pd.concat([formatted_df, table], axis=1)

        data_df = pd.concat([data_df, formatted_df], ignore_index=True)
    except:
        pass

    print(data_df)
    return data_df


# Returns all product links
def get_links(link):
    try:
        source = s.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    categories = []

    # Get categories
    for category in soup.select(".multi-column-dropdown a"):
        cat_link = make_link(category['href'])
        categories.append(cat_link)

    categories.pop(-1)

    for cat in categories:
        try:
            source = s.get(cat).text
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        cat_df = pd.DataFrame()

        # get and scrape products
        for product in soup.select(".product-sub-heading a"):
            product_df = scrape(make_link(product['href']))
            cat_df = pd.concat([cat_df, product_df], ignore_index=True)

        folder_name = cat.split('/')[2] + "/" + cat.split('/')[3]
        cat_df.to_excel(fr"{folder_name}.xlsx", index=False)


if __name__ == '__main__':
    # Replace URL here
    # Do NOT include trailing '/'
    URL = "https://www.rrkabel.com"

    # Initialise requests session
    s = requests.Session()

    # Create root folder
    create_folder(URL.split('/')[2])

    # Get links and scrape
    get_links(URL)
