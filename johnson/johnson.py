import csv
import os
from bs4 import BeautifulSoup
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor


def scrape(category):
    url_pages = f'https://www.johnson-tiles.com/catalog/search/categories/{category}/'
    file = str(url_pages).split('/')[-2]
    file_name = file + ".csv"

    csv_file = open(file_name, 'w', newline='', encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(
        ['url', 'name', 'Recycle % ', 'Range', 'Short Code', "Colour ", "Finish", "Rectified Edge", 'Wall Suitability'
            , 'Floor Suitability', "Wet Barefoot", "Material", "Classification", "Light Reflectance Value", "CSV",
         "PTV (4S)", "PTV (TRL)",
         'R Value', 'Wet Ramp', "PEI", "Traffic", "Grout Suggestions", "Size", "Size With Full Product Code",
         "Size images"
            , "Additional Fittings", "Full product code(Additional Fittings)", 'image links'])

    f_url = url_pages + '?show=all'

    html_text = s.get(f_url).text
    print("Scraping " + f_url)

    soup_page_by_page = BeautifulSoup(html_text, 'lxml')

    try:
        all_items_div = soup_page_by_page.find("ul", class_="products")
        all_items_product_div = all_items_div.find_all("li", class_="products__product")
    except Exception as e:
        print("----->No products in the page ")
        print(f"Error :{e}")
        exit()

    for item in all_items_product_div:
        try:
            pre_link = "https://www.johnson-tiles.com/"
            url_single_item = pre_link + item.find("a", class_="product__product-link")["href"]
        except Exception as e:
            print("---->Item page not found")
            break

        html_text_single_item = requests.get(url_single_item).text
        soup_single_item = BeautifulSoup(html_text_single_item, 'lxml')

        try:
            product_name = soup_single_item.find("div", class_="product-header").find("h1",
                                                                                      class_="product-header__info__name").text
        except:
            product_name = ""

        try:
            pre_link = "https://www.johnson-tiles.com"
            product_img = pre_link + soup_single_item.find("div", class_="product__gallery__image").find("img")["src"]
        except:
            product_img = ""
        try:
            product_recycle = soup_single_item.find("div", class_="product__stats__eco-friendly").find("p",
                                                                                                       class_="value").text
        except:
            product_recycle = ""

        try:
            div_details = soup_single_item.find("table", class_="product__stats")
            div_product_details = div_details.find_all("tr")
        except:
            break

        product_rectified_edge = ""
        product_wall_suitability = ""
        product_floor_suitability = ""
        product_wet_barefoot = ""
        product_material = ""
        product_classification = ""
        product_light_reflectance_value = ""
        product_CSV = ""
        product_PTV_4S = ""
        product_PTV_TRL = ""
        product_R_value = ""
        product_wet_ramp = ""
        product_PEI = ""
        product_traffic = ""
        product_grout_suggestions = ""
        for each_details in div_product_details:
            try:
                th_text = each_details.find("th").text
            except:
                th_text = ""
            if "Range" in th_text:
                try:
                    product_range = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_range = ""
            elif "Short Code" in th_text:
                try:
                    product_short_code = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_short_code = ""
            elif "Colour" in th_text:
                try:
                    product_colour = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_colour = ""
            elif "Finish" in th_text:
                try:
                    product_finish = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_finish = ""
            elif "Rectified Edge" in th_text:
                try:
                    product_rectified_edge = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_rectified_edge = ""
            elif "Wall Suitability" in th_text:
                try:
                    product_wall_suitability = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_wall_suitability = ""
            elif "Floor Suitability" in th_text:
                try:
                    product_floor_suitability = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_floor_suitability = ""
            elif "Wet Barefoot" in th_text:
                try:
                    product_wet_barefoot = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_wet_barefoot = ""
            elif "Material" in th_text:
                try:
                    product_material = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_material = ""

            elif "Classification" in th_text:
                try:
                    product_classification = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_classification = ""
            elif "Light Reflectance Value" in th_text:
                try:
                    product_light_reflectance_value = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_light_reflectance_value = ""
            elif "CSV" in th_text:
                try:
                    product_CSV = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_CSV = ""
            elif "PTV (4S)" in th_text:
                try:
                    product_PTV_4S = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_PTV_4S = ""
            elif "PTV (TRL)" in th_text:
                try:
                    product_PTV_TRL = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_PTV_TRL = ""
            elif "R Value" in th_text:
                try:
                    product_R_value = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_R_value = ""
            elif "Wet Ramp" in th_text:
                try:
                    product_wet_ramp = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_wet_ramp = ""
            elif "PEI" in th_text:
                try:
                    product_PEI = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_PEI = ""

            elif "Traffic" in th_text:
                try:
                    product_traffic = each_details.find("td").text.replace("\n", "").replace("  ", "")
                except:
                    product_traffic = ""
            elif "Grout Suggestions" in th_text:
                try:
                    product_grout_suggestions = []
                    div_grout_suggestionsp = each_details.find_all("td")
                    for each_div in div_grout_suggestionsp:
                        product_grout_suggestions.append(each_div.find("a").text.replace("\n", "").replace("  ", ""))

                except:
                    product_grout_suggestions = []

        try:
            div_size = soup_single_item.find("table", class_="product-sizes__table")
            div_size_table_names = div_size.find_all("tr")

            product_size = []
            product_size_code = []
            product_size_image = []

            product_fitting = []
            product_fitting_code = []

            for each_tr in div_size_table_names:
                try:
                    cls = each_tr["class"]
                    if cls[0] == 'has-zoom':
                        div_td = each_tr.find_all("td")
                        product_size.append(div_td[0].text)
                        product_size_code.append(div_td[1].text)
                        pre_link = "https://www.johnson-tiles.com"
                        img_link = pre_link + div_td[2].find("img")["data-full-size"]
                        product_size_image.append(img_link)
                except:
                    try:
                        data_type = each_tr["data-collapse"]
                        div_td = each_tr.find_all("td")
                        product_fitting.append(div_td[0].text)
                        product_fitting_code.append(div_td[1].text)
                    except:
                        pass
        except:
            product_size = []
            product_size_code = []
            product_size_image = []

            product_fitting = []
            product_fitting_code = []

        product_name = product_name + " " + product_colour + " " + product_finish
        product_url = url_single_item
        csv_writer.writerow(
            [product_url, product_name, product_recycle, product_range, product_short_code, product_colour,
             product_finish, product_rectified_edge
                , product_wall_suitability, product_floor_suitability, product_wet_barefoot, product_material,
             product_classification, product_light_reflectance_value
                , product_CSV, product_PTV_4S, product_PTV_TRL, product_R_value, product_wet_ramp, product_PEI,
             product_traffic, product_grout_suggestions
                , product_size, product_size_code, product_size_image, product_fitting, product_fitting_code,
             product_img])

    csv_file.close()

    df_new = pd.read_csv(file_name)
    df_new.to_excel(str(file + '.xlsx'), index=False)
    os.remove(file_name)


if __name__ == "__main__":
    '''
    usage:
    -> add category name as it appears in url to categories list
    -> Eg: 'wood' for https://www.johnson-tiles.com/catalog/search/categories/wood/
    -> run
    '''

    s = requests.Session()
    categories = ['mosaic', 'stone', 'concrete', 'marble', 'wood', 'colour', 'white', 'structure', 'pattern', 'shape', 'speckle', '20mm']

    with ThreadPoolExecutor(max_workers=6) as exe:
        # Maps the method 'cube' with a list of values.
        result = exe.map(scrape, categories)
