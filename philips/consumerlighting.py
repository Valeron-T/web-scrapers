import time
import os
import pandas as pd
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


# Create full link from partial link
def make_link(url):
    if 'https://www.lighting.philips.co.in' not in url:
        new_link = 'https://www.lighting.philips.co.in' + url
    else:
        new_link = url
    return new_link


def scrape(link, exec_path, driver_path):
    print("Scraped: " + link)
    # Instantiate options
    options = Options()
    # Configure executable path of Chromium browser
    options.binary_location = exec_path
    options.add_argument("--headless")

    # Set the location of the webdriver (Webdriver placed in script directory by default)
    ser = Service(driver_path)

    # Instantiate a webdriver
    driver_s = webdriver.Chrome(options=options, service=ser)
    driver_s.maximize_window()
    try:
        driver_s.get(link)
        source = driver_s.page_source
    except:
        print("URL not reachable. Recheck URL")
        exit()

    soup = BeautifulSoup(source, 'lxml')

    title = soup.select_one('.p-product-info .p-sub-title').text.strip()
    try:
        desc = " ".join(str(
            soup.select_one('.p-version-elements .p-body-copy-02').text).split()).strip().removesuffix(
            " See all benefits")
    except:
        desc = ""

    try:
        price = soup.select_one(".p-current-price-value").text.strip()
    except:
        price = ""

    sku = soup.select_one(".p-product-info .p-type").text.strip()
    features = [" ".join(str(feat.text).split()) for feat in soup.select(".p-feature-title")]

    try:
        img = soup.select_one(".p-normal-view img")['src']
    except:
        img = ""

    tech_specs_dict = {}
    # Load specifications page
    try:
        driver_s.get(link + "/specifications")
        source = driver_s.page_source

        soup = BeautifulSoup(source, 'lxml')

        tech_specs_titles = soup.find_all('dt')
        for tech_specs_title in tech_specs_titles:
            if tech_specs_title.find_next_sibling().find('ul'):
                tech_specs_values = [value.text.strip() for value in
                                     tech_specs_title.find_next_sibling().find_all('li')]
                tech_specs_dict[tech_specs_title.text.strip()] = tech_specs_values
            else:
                tech_specs_values = " ".join(str(tech_specs_title.find_next_sibling().text.strip()).split())
                tech_specs_dict[tech_specs_title.text.strip()] = tech_specs_values
    except:
        pass

    data = {
        'Link': str(link),
        'Title': title,
        'Description': desc,
        'Image': img,
        'Features': features,
        'Price': price,
        'SKU': sku,
    }

    if tech_specs_dict:
        data.update(tech_specs_dict)

    data_df = pd.DataFrame([data])
    driver_s.close()
    return data_df


def main(exec_path, driver_path):
    folder = "Consumer-lighting"
    create_folder(folder)
    # Instantiate options
    options = Options()
    # Configure executable path of Chromium browser
    options.binary_location = exec_path

    # Set the location of the webdriver (Webdriver placed in script directory by default)
    ser = Service(driver_path)

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=options, service=ser)
    driver.maximize_window()

    links = [
        'https://www.lighting.philips.co.in/consumer/choose-a-bulb/products#filters=CANDLE_BULB_SU%2CSPOT_BULB_SU%2CSTANDARD_BULB_SU%2CSPIRAL_BULB_SU%2CSTICK_BULB_SU%2CCIRCULAR_BULB_SU%2CLINEAR_BULB_SU%2CSMARTLIGHTING_BULB_SU&sliders=&support=&price=&priceBoxes=&page=0&layout=36.subcategory.p-grid-icon',
        'https://www.lighting.philips.co.in/consumer/choose-a-fixture/products#filters=CONCEPT_DECO_LINEAR_SU%2CCONCEPT_MYLIVING_SU%2CCONCEPT_MYBATHROOM_SU%2CCONCEPT_MYHOMEOFFICE_SU%2CCONCEPT_FUNCTIONAL_SU%2CCONCEPT_DISINFECTION_SU%2CCONCEPT_INDOOR_FIXTURES_SU%2CCONCEPT_OUTDOOR_FIXTURES_SU%2CCONCEPT_EMERGENCY_FIXTURES_SU&sliders=&support=&price=&priceBoxes=&page=0&layout=36.subcategory.p-grid-icon',
        'https://www.lighting.philips.co.in/consumer/switches-wiring-devices/products/all#filters=SS_SWITCH_SU%2CSS_SOCKET_SU%2CSS_CONTROLLER_SU%2CSS_CONNECTOR_SU%2CSS_GRID_COVER_SU%2CSS_MCB_SU%2CSS_RCCB_SU%2CSS_ISOLATOR_SU%2CSS_DISTRIBUTION_BOX_SU%2CSS_STABILIZER_SU%2CSS_LAMP_HOLDER_SU%2CSS_PLUG_TOP_SU%2CSS_SOLUTION_BOX_SU%2CSS_DOOR_BELL_SU%2CSS_OTHERS_SU&sliders=&support=&price=&priceBoxes=&page=0&layout=36.subcategory.p-grid-icon']

    for link in links:
        try:
            driver.get(link)
            time.sleep(random.randint(3, 5))
            source = driver.page_source
        except:
            print("URL not reachable. Recheck URL")
            exit()

        soup = BeautifulSoup(source, 'lxml')
        last_pg = soup.select_one('.p-pages li.p-number:nth-last-child(2)').text.strip()

        page_links = []

        for pg in range(int(last_pg)):
            link_f = link.replace('page=0', f"page={pg}")
            page_links.append(link_f)

        print(page_links)

        product_links = []

        for page_link in page_links:
            driver_p = webdriver.Chrome(options=options, service=ser)
            driver_p.maximize_window()
            try:
                driver_p.get(page_link)
                time.sleep(random.randint(3, 5))
                source = driver_p.page_source
            except:
                print("URL not reachable. Recheck URL")
                exit()

            soup = BeautifulSoup(source, 'lxml')

            links = [make_link(link['href']) for link in soup.select('.p-product-title.p-bold a') if
                     link['href'] != '#.html']
            product_links += links

            driver_p.close()

        print(len(product_links), product_links)

        master_df = pd.DataFrame()
        for prod in product_links:
            prod_df = scrape(prod, exec_path, driver_path)
            master_df = pd.concat([master_df, prod_df])

        master_df.to_excel((folder + "/" + link.split("/")[4].replace("choose-a-", "") + ".xlsx"), index=False)

    driver.close()


if __name__ == '__main__':
    # Script will run from philips.py
    # To run seperatelu optionally, pass browser and chromedriver executable as parameters to main
    main(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
         r"D:\Desktop\Web Scrapers\chromedriver.exe")
