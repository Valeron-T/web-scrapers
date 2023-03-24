import requests
import os
from bs4 import BeautifulSoup
import csv
import pandas as pd


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


def scrape(link, name_format = None):
    url_pages = link

    # set appropriate path to csv file
    file_name = base_name + '/' + url_pages.split('/')[-2] + '.csv'

    if name_format:
        file_name = base_name + '/' + name_format + '-' + url_pages.split('/')[-2] + '.csv'

    csv_file = open(file_name, 'w', newline='', encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['url', 'name', 'Catalogue No.', 'description', 'mrp', 'colors', 'image links', 'Size'])

    html_text_pages = requests.get(url_pages).text

    soup_pages = BeautifulSoup(html_text_pages, 'lxml')

    try:
        pages_finding = soup_pages.find("ul", class_="page-numbers").find_all("a", class_="page-numbers")
        total_pages = int(pages_finding[-2].text)

    except Exception as e:
        try:
            pages_finding = soup_pages.find("ul", class_="page-numbers").find_all("a", class_="page-numbers")
            total_pages = int(pages_finding[-3].text)
        except AttributeError:
            total_pages = 1

    print(f"---->Total-pages={total_pages}\n")

    for i in range(1, total_pages + 1):
        print(f"---->page{i}<------")
        url_page_by_page = url_pages + f'/page/{i}/'
        html_text_page_by_page = requests.get(url_page_by_page).text

        soup_page_by_page = BeautifulSoup(html_text_page_by_page, 'lxml')

        try:
            all_items_div = soup_page_by_page.find("div", class_="justify-content-center")
            all_items_product_div = all_items_div.find_all("div", class_="product")
        except Exception as e:
            print("----->No products in the page ")
            print(f"Error :{e}")
            break

        for item in all_items_product_div:
            try:
                url_single_item = item.find("a", class_="woocommerce-LoopProduct-link woocommerce-loop-product__link")[
                    "href"]
            except Exception as e:
                print("---->Item page not found")
                break

            try:
                img_url_find = \
                    item.find("a", class_="woocommerce-LoopProduct-link woocommerce-loop-product__link").find("img")[
                        "src"]
                img_url_single_item = (img_url_find.replace("-430x392", "")).replace("-430x430", "")
            except Exception as e:
                img_url_single_item = ""

            colour_names = []
            try:
                colour_find = item.find("div", class_="wc_color_attibutes").find_all("span")
                for color_index in range(1, len(colour_find)):
                    colour_names.append(colour_find[color_index]["data-title"])
            except Exception as e:
                print(f"---->Error: {e}")
            html_text_single_item = requests.get(url_single_item).text

            soup_single_item = BeautifulSoup(html_text_single_item, 'lxml')

            try:
                div_details = soup_single_item.find("div", class_="summary")
            except:
                break
            try:
                product_name = div_details.find("h1", class_="product_title").text
                # print(product_name)
            except:
                product_name = ""

            product_price = div_details.find("p", class_="price").find("span", class_="woocommerce-Price-amount").find(
                "bdi").text
            # print(product_price)

            try:
                product_desc = soup_single_item.find("div",
                                                     class_="woocommerce-product-details__short-description").find(
                    "p").text
                # print(product_desc)
            except:
                product_desc = ""

            try:
                product_details_section = soup_single_item.find_all("div", class_="attributesSection")

                try:
                    product_code = product_details_section[0].find("div", class_="value").text
                except:
                    product_code = ""

                try:
                    for attr in product_details_section:
                        if attr.find("h6", class_="title").text == "Size":
                            product_size = attr.find("div", class_="value").text
                        else:
                            product_size = ""
                except:
                    product_size = ""

            except Exception as e:
                print(f"----->Error : {e}")

            product_url = url_single_item
            product_colour = colour_names
            product_img = img_url_single_item
            csv_writer.writerow(
                [product_url, product_name, product_code, product_desc, product_price, product_colour, product_img,
                 product_size])


def shower_enclosures(link):
    try:
        source = s.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    product_links = []

    for product_container in soup.find('section', id="blogtypes-2").find_all('div', class_="type-wrapper"):
        product_link = product_container.find('a')['href']
        product_links.append(product_link)

    print(product_links)

    data_df = pd.DataFrame()

    for prod_link in product_links:
        try:
            source = s.get(prod_link).text
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        title = soup.select_one('.entry-title').text

        try:
            desc = soup.select_one(".woocommerce-product-details__short-description p").text
        except:
            desc = ""

        try:
            imgs = soup.select_one('.woocommerce-product-gallery__wrapper').find_all('img')
            imgs = [img['src'] for img in imgs]
        except Exception as e:
            imgs = ""

        try:
            opt_features = soup.select_one(".optional_list").find_all('li')
            opt_features = [feat.text for feat in opt_features]
        except:
            opt_features = ""

        data = {
            'Link': str(link),
            'Title': title,
            'Description': desc,
            'Images':imgs,
            'Features': opt_features
        }

        df_dictionary = pd.DataFrame([data])
        data_df = pd.concat([data_df, df_dictionary], ignore_index=True)

        table = pd.read_html(source)[0]

        data_df = pd.concat([data_df, table], ignore_index=True)

    data_df.to_csv((base_name + '/' + 'shower_enclosures.csv'), index=False)


if __name__ == '__main__':
    s = requests.Session()
    url = 'https://hindware.com/product-category/faucets/'
    base_name = url.split('/')[2]
    create_folder(base_name)
    if url == "https://hindware.com/product-category/shower_enclosure/":
        shower_enclosures(url)
    else:
        print("Scraped: " + url)
        try:
            source = s.get(url).text
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        links = soup.select_one('#cattypes').find_all('a')
        links = [link['href'] for link in links]
        print(links)

        for link in links:
            if link == "https://hindware.com/product-category/faucets/hues-by-hindware/":
                try:
                    source = s.get(link).text
                except:
                    print("URL not reachable. Recheck URL")
                    exit()

                soup = BeautifulSoup(source, 'lxml')

                for sublink_container in soup.select_one("#types").find_all('a'):
                    scrape(sublink_container['href'], 'hues')
            else:
                scrape(link)
