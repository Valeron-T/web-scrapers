from bs4 import BeautifulSoup
import requests
import re
import os
import csv


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


def data_creator(lst, txt):
    list_txt = txt.split("\n")
    lst_data = []
    for i in range(len(lst)):
        list_txt[i] = list_txt[i].replace(lst[i], "")
        lst_data.append(lst[i] + " : " + list_txt[i])
    return lst_data


# Scrape products
def scrape(url_pages, fold_name):
    # url_pages = 'https://www.kutchina.com/product-category/chimney-and-cooktop/'
    initial_link = url_pages

    file_name = fold_name + '/' + initial_link.split('/')[-2] + '.csv'

    csv_file = open(file_name, 'w', newline='', encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(
        ['Url', 'Name', 'Price', "Short description", "Code", 'Category', 'Description', "Additional Information ",
         'Size', 'Technical specification', "USP", "Power", 'Image links'])

    # csv_writer.writerow([product_url, product_name, product_price,product_short_desc,product_code,product_Categories,product_desc
    #         , product_additional_info,product_size,product_tech_spec,product_usp,product_power,product_img])

    # class="page last"

    # url_pages='https://www.kutchina.com/product-category/large-kitchen-appliances/kitchen-hob-and-stove/'

    html_text_pages = requests.get(url_pages).text

    soup_pages = BeautifulSoup(html_text_pages, 'lxml')

    try:
        pages_finding = soup_pages.find_all("a", class_="page-numbers")
        total_pages = int(pages_finding[-2].text)

    except Exception as e:
        try:
            pages_finding = soup_pages.find_all("a", class_="page-numbers")
            total_pages = int(pages_finding[-3].text)
        except:
            total_pages = 1

    print(f"---->Total-pages={total_pages}\n")

    # class="product-item large  category1"
    # class="products-grid-wrapper isotope-wrapper"

    for i in range(1, total_pages + 1):
        print(f"---->page{i}<------")
        url_page_by_page = url_pages + f'page/{i}/'

        html_text_page_by_page = requests.get(url_page_by_page).text

        soup_page_by_page = BeautifulSoup(html_text_page_by_page, 'lxml')

        try:
            all_items_div = soup_page_by_page.find("div", class_="shop-products")
            all_items_product_div = all_items_div.find_all("div", class_="item-col")
        except Exception as e:
            print("----->No products in the page ")
            print(f"Error :{e}")
            break

        for item in all_items_product_div:
            try:
                url_single_item = item.find("div", class_="vgwc-image-block").find("a")["href"]
            except Exception as e:
                print("---->Item page not found")
                break
            try:
                title = item.find("div", class_="vgwc-image-block").find("a")["title"]
            except:
                title = ""

            html_text_single_item = requests.get(url_single_item).text
            soup_single_item = BeautifulSoup(html_text_single_item, 'lxml')

            try:
                images = []
                div_images = soup_single_item.find("div", class_="single-product-image")
                try:
                    div_owl_item = div_images.find_all("div", class_="woocommerce-product-gallery__image")
                    if not div_owl_item:
                        img_link = div_images.find("a")["href"]
                        images.append(img_link)
                    for owl_item in div_owl_item:
                        img_link = owl_item["data-thumb"].replace("-100x100", "")
                        images.append(img_link)
                except:
                    try:
                        img_link = div_images.find("a")["href"]
                        images.append(img_link)
                    except:
                        images = []
            except:
                images = []
                print("No images sry....")

            try:
                div_price = soup_single_item.find("div", class_="col-summary").find_all("span",
                                                                                        class_="woocommerce-Price-amount amount")
                actual_price = div_price[0].find("bdi").text
                discounted_price = div_price[1].find("bdi").text
            except:
                actual_price = ""
                discounted_price = ""

            short_desc = ""
            try:
                div_short_desc = soup_single_item.find("div", class_="short-description")
                short_desc = div_short_desc.text.strip()
                # print(short_desc)
                # print()
            except:
                short_desc = ""

            try:
                div_meta = soup_single_item.find("div", class_="product_meta")
                try:
                    product_code = div_meta.find("span", class_="sku").text
                except:
                    product_code = ""
                try:
                    product_Categories = str(div_meta.find("span", class_="posted_in").text).removeprefix('Category:').removeprefix('Categories:').replace('All Products,', '').strip()

                except:
                    product_Categories = ""
            except:
                pass

            product_desc = []
            product_additional_info = []
            product_tech_spec = []
            product_usp = []
            product_size = []
            product_power = []

            try:
                div_details = soup_single_item.find("div", class_="woocommerce-tabs")
                div_product_details = div_details.find_all("div", class_="panel entry-content")
            except:
                break

            for each_panel in div_product_details:
                try:
                    id_panel = each_panel["id"]
                    # print(id_panel)
                except:
                    id_panel = ""
                if id_panel == "tab-additional_information" or id_panel == "tab-additional-information":
                    if not product_additional_info:
                        try:
                            details = each_panel.find_all("tr", class_="woocommerce-product-attributes-item")
                            if details:

                                for each_details in details:
                                    th_data = each_details.find("th").text
                                    td_data = each_details.find("td").text
                                    data = th_data + " : " + td_data.replace("\n", "")
                                    product_additional_info.append(data)
                            if not product_additional_info:
                                try:
                                    details = each_panel.find("p")
                                    temp_data = details.text
                                    strong_text = []
                                    strong_details = details.find_all("strong")

                                    if len(strong_details) > 1:
                                        for each_strong in strong_details:
                                            strong_text.append(each_strong.text)
                                        product_additional_info = data_creator(strong_text, temp_data)
                                except:
                                    product_additional_info = []

                        except:
                            product_additional_info = []
                        if not product_additional_info:
                            try:
                                details = each_panel.find("p")
                                temp_data = details.text
                                product_additional_info = temp_data.split("\n")
                            except:
                                pass

                elif id_panel == "tab-description":
                    try:
                        details = each_panel.find_all("ul")
                        for each_details in details:
                            data = each_details.text.replace("\n", "")
                            product_desc.append(data)
                        if not details:
                            try:
                                details = each_panel.find("p")
                                temp_data = details.text
                                strong_text = []
                                strong_details = details.find_all("strong")

                                if len(strong_details) > 1:
                                    for each_strong in strong_details:
                                        strong_text.append(each_strong.text)
                                    product_desc = data_creator(strong_text, temp_data)
                            except:
                                product_desc = []

                            try:
                                details = each_panel.find_all("p")
                                if not product_desc:
                                    for each_details in details:
                                        try:
                                            temp_data = each_details.text
                                            # print(temp_data)
                                            try:
                                                temp_data_strong = each_details.find("strong").text
                                            except:
                                                temp_data_strong = ""
                                            if temp_data_strong != "":
                                                data = temp_data_strong + " : " + temp_data.replace(temp_data_strong,
                                                                                                    "")
                                            else:
                                                data = temp_data
                                            product_desc.append(data)
                                        except:
                                            pass

                            except:
                                product_desc = []
                    except:
                        product_desc = []
                    if not product_desc:
                        try:
                            details = each_panel.find("p")
                            temp_data = details.text
                            product_desc = temp_data.split("\n")
                        except:
                            pass
                elif id_panel == "tab-technical-specification":
                    try:
                        details = each_panel.find_all("tr")
                        for each_details in details:
                            td_1_data = each_details.find_all("td")[0].text
                            td_2_data = each_details.find_all("td")[1].text
                            data = td_1_data + " : " + td_2_data.replace("\n", "")
                            product_tech_spec.append(data)
                        if not details:
                            try:
                                details = each_panel.find("p")
                                temp_data = details.text
                                strong_text = []
                                strong_details = details.find_all("strong")

                                if len(strong_details) > 1:
                                    for each_strong in strong_details:
                                        strong_text.append(each_strong.text)
                                    product_tech_spec = data_creator(strong_text, temp_data)
                            except:
                                product_tech_spec = []

                            try:
                                details = each_panel.find_all("p")
                                if not product_tech_spec:
                                    for each_details in details:
                                        try:
                                            temp_data = each_details.text
                                            temp_data_strong = each_details.find("strong").text
                                            data = temp_data_strong + " : " + temp_data.replace(temp_data_strong, "")
                                            product_tech_spec.append(data)
                                        except:
                                            pass

                            except:
                                product_tech_spec = []
                            try:
                                details = each_panel.find_all("li")
                                if details != [] and product_tech_spec == []:
                                    for each_details in details:
                                        try:
                                            temp_data = each_details.text
                                            temp_data_strong = each_details.find("strong").text
                                            data = temp_data_strong + " : " + temp_data.replace(temp_data_strong, "")
                                            product_tech_spec.append(data)
                                        except:
                                            pass
                            except:
                                product_tech_spec = []

                    except:
                        product_tech_spec = []
                    if not product_tech_spec:
                        try:
                            temp_p = each_panel.find("p").text
                            temp_list = temp_p.split("\n")
                            product_tech_spec = temp_list
                        except:
                            pass
                elif id_panel == "tab-product-usp":
                    try:
                        details = each_panel.find("p")
                        product_usp = details.text.split("\n")
                    except:
                        pass

                elif id_panel == "tab-size-dimensions":
                    try:
                        details = each_panel.find("p")
                        temp_data = details.text
                        strong_text = []
                        strong_details = details.find_all("strong")

                        for each_strong in strong_details:
                            strong_text.append(each_strong.text)
                        product_size = data_creator(strong_text, temp_data)
                    except:
                        pass
                    if not product_size:
                        try:
                            details = each_panel.find("p")
                            temp_data = details.text
                            product_size = temp_data.split("\n")
                        except:
                            pass
                elif id_panel == "tab-power-consumption":
                    try:
                        details = each_panel.find("p")
                        temp_data = details.text
                        strong_text = []
                        strong_details = details.find_all("strong")

                        for each_strong in strong_details:
                            strong_text.append(each_strong.text)
                        product_power = data_creator(strong_text, temp_data)
                    except:
                        pass
                    if not product_power:
                        try:
                            details = each_panel.find("p")
                            temp_data = details.text
                            product_power = temp_data.split("\n")
                        except:
                            pass
            product_url = url_single_item
            product_img = images
            product_name = title
            product_price = discounted_price
            product_short_desc = short_desc.replace("\n", "")

            csv_writer.writerow(
                [product_url, product_name, product_price, product_short_desc, product_code, product_Categories,
                 product_desc, product_additional_info, product_size, product_tech_spec, product_usp, product_power,
                 product_img])


if __name__ == "__main__":
    s = requests.Session()

    # No changes required. Just run the script
    link = 'https://www.kutchina.com/product-category/combo-set/'
    base = link.split('/')[2]

    create_folder(base)

    print("Got categories from " + link)
    try:
        source = s.get(link).text
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    categories = []

    links_uf = soup.select_one('.product-categories').find_all('a')

    # Unwanted categories keywords
    ignore_cats = ["All Products", "and", "Combo", "Corporate", "Checkout"]
    words_re = re.compile("|".join(ignore_cats))

    for link_uf in links_uf:
        if not words_re.search(link_uf.text):
            categories.append(link_uf['href'])

    for category in categories:
        print("Scraped: " + category)
        try:
            source = s.get(category).text
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')

        active_cat = soup.select_one(".current-cat")

        if active_cat:
            active_cat_classes = active_cat['class']
            if "cat-parent" in active_cat_classes:
                create_folder(base + '/' + category.split('/')[4])
                subcat_links = [link['href'] for link in active_cat.find('ul').find_all('a')]
                for link in subcat_links:
                    try:
                        source = s.get(link).text
                    except:
                        print("URL not reachable. Recheck URL")
                        exit()

                    soup = BeautifulSoup(source, 'lxml')

                    subsubcat = soup.select_one('.product-categories').find('a', href=link).find_next_sibling('ul')

                    if subsubcat:
                        folder_name = base + '/' + category.split('/')[4] + '/' + link.split('/')[5]
                        create_folder(folder_name)
                        subsubcats_links = [li['href'] for li in subsubcat.find_all('a')]
                        for sublink in subsubcats_links:
                            scrape(sublink, folder_name)
                    else:
                        folder_name = base + '/' + category.split('/')[4]
                        scrape(link, folder_name)
            else:
                folder_name = base
                scrape(category, folder_name)
