import requests
import pandas as pd
from bs4 import BeautifulSoup
import os


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


def get_links(url):
    folder_name = url.split('/')[-2]
    create_folder(folder_name)
    try:
        headers = {
            "authority": "graffitilaminates.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-GB,en;q=0.5",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }

        source = s.request("GET", url, headers=headers).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    subcategories = [subcategory['href'] for subcategory in soup.select("#menu-vienna-menu a") if
                     subcategory['href'][-1] != '#']

    if not subcategories:
        subcategories = [subcategory['href'] for subcategory in soup.select("#menu-graffix a") if
                         subcategory['href'][-1] != '#']

    print(subcategories)

    for subcategory in subcategories:
        print(f"Scraped: {subcategory}")
        try:
            headers = {
                "authority": "graffitilaminates.com",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-GB,en;q=0.5",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "sec-gpc": "1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
            }

            source = s.request("GET", subcategory, headers=headers).text
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        data_containers = soup.select('.bwg_lightbox_0')

        master_df = pd.DataFrame()
        for data_container in data_containers:
            title = data_container.select_one('.bwg_title_spun2_0').text.strip()
            img = data_container.find('img')['src']

            data = {
                'Link': subcategory,
                'Title': title,
                'Image': img,
            }

            data_df = pd.DataFrame([data])
            master_df = pd.concat([master_df, data_df])

        master_df.to_excel(f'{folder_name}/{subcategory.split("/")[-2]}.xlsx', index=False)


if __name__ == '__main__':
    s = requests.Session()

    # Replace category URL here
    URL = "https://graffitilaminates.com/graffix/"

    get_links(URL)
