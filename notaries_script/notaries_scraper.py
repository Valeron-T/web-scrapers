import scrapy
from scrapy.crawler import CrawlerProcess
import re
import pandas as pd
import os
from glob import glob


class NotariesSpider(scrapy.Spider):
    name = 'notaries'
    # -----------------------------------------------------------------------------------------------------------
    # Choose starting page and ending page here. (Ending page will not be scraped)
    # Example: If starting page is 0 and ending page is 10, scraper will scrape pages 0-9.
    # IMPORTANT: Even though page numbers are displayed from 1 on the website, the initial page is page 0.
    # To specify if conversion to xlsx is required, scroll to line 115
    # -----------------------------------------------------------------------------------------------------------
    start_pg = 0
    end_pg = 3500
    # -----------------------------------------------------------------------------------------------------------
    # Last page displayed on website as of 29th May 2022 is 6895.
    # -----------------------------------------------------------------------------------------------------------
    start_urls = ['https://notaries-directory.eu/cs/search?page=' + str(i) for i in range(start_pg, end_pg)]

    def parse(self, response):
        for link in response.css('a.notary-detail-link::attr(href)').extract():
            new_link = 'https://notaries-directory.eu' + str(link)
            yield response.follow(new_link, callback=self.parse_categories)

    def parse_categories(self, response):
        # Name
        try:
            name = response.css('div.title span::text, h1::text').extract()
            name_f = " ".join(" ".join(name).split())
        except:
            name_f = "Not found"

        # Full address
        try:
            address = response.css('.address::text , .address span::text').extract()
            address_f = " ".join(" ".join(address).split()).replace("/f", "")
        except:
            address_f = "Not found"

        # Email
        try:
            email = response.css('div.mail a::text').extract()
        except:
            email = "Not found"

        # Stores original (full) address
        address_copy = address_f

        # State
        try:
            state = str(address_f.split(",")[-1]).strip()
        except:
            state = ""

        # City
        try:
            city = str(address_f.split(",")[-2]).strip()
        except:
            city = ""

        # Get new address without state and city
        try:
            address_split = address_f.split(",")
            address_split.pop(-1)
            address_split.pop(-1)
            address_ff = " ".join(address_split)
        except:
            address_ff = ""

        # ZIP code (matches regex pattern)
        pattern = re.compile(r"([0-9]{4}\s[A-Z]{2})|([A-Z]{3}\d{4})|((\d{2,4}-\d{3})|(\d{4,6}))")
        if pattern.search(str(address_copy)):
            zip_code = pattern.search(str(address_copy))
            zip_code_f = zip_code.group(0)
        else:
            zip_code_f = ""

        # Phone
        try:
            phone = response.css('div.phone::text').extract()
        except:
            phone = "Not found"

        # Website
        try:
            website = response.css('a.link-site::text').extract()
        except:
            website = "Not found"

        # Data
        yield {
            'Name': name_f,
            'Address': address_ff,
            'City': city,
            'Zip code': zip_code_f,
            'State': state,
            'Phone': phone,
            'Email': email,
            'WWW': website
        }


# Creates folder
def create_folder(fold_name):
    if not os.path.exists(f'{fold_name}'):
        os.mkdir(f'{fold_name}')


if __name__ == "__main__":
    # Creates directory notaries
    create_folder("notaries")

    process = CrawlerProcess(settings={
        'FEED_URI': 'notaries/notaries_%(start_pg)s-%(end_pg)s.csv',
        'FEED_FORMAT': 'csv',
        'DOWNLOAD_DELAY': 0.50,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'middlewares.TooManyRequestsRetryMiddleware': 543,
        }
    })

    # Starts crawling and scraping
    process.crawl(NotariesSpider)
    process.start()

    # To convert generated csv to xlsx, set this to True. Otherwise, leave it as false.
    convert_to_xlsx = True

    # If you want to retain csv file after conversion to xlsx, set this to False.
    delete_csv = True

    if convert_to_xlsx:
        for csv_file in glob(fr"{os.getcwd()}\notaries\*.csv"):
            print(f"Converted : {csv_file}")
            df = pd.read_csv(csv_file)
            xlsx_file = os.path.splitext(csv_file)[0] + '.xlsx'
            df.to_excel(xlsx_file, index=None, header=True)
            if delete_csv:
                os.remove(csv_file)
