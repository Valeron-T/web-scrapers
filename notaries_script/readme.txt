Requirements:
Python 3 installed on your system (Tested on python 3.10)

Required modules:
pandas==1.4.2
Scrapy==2.6.1

Files provided:
middlewares.py
notaries_scraper.py

Instructions:

1. Install required modules. You may make use of the following commands.
    pip install pandas
    pip install scrapy

2. Copy the 2 files to desired location. Open the "notaries_scraper.py" file with IDLE/any ".py" compatible editor.

3. There are 4 options to configure in "notaries_scraper.py" file.
   Location of these variables in the file varies, hence comments are included in the script as well to locate them

    -- start_pg = 2
        Value type: Integer
        This tells the scraper to start scraping from this page onwards.

    -- end_pg = 3
        Value type: Integer
        This tells the scraper to start scraping up till this page number. (Doesn't include this page)

    Example: If starting page is 0 and ending page is 10, scraper will scrape pages 0-9.

    -- convert_to_xlsx = True
        Value type: Boolean ("True" or "False")
        To convert generated csv to xlsx, set this to True. Otherwise, leave it as false.

    -- delete_csv = True
        Value type: Boolean ("True" or "False")
        If you want to retain csv file after conversion to xlsx, set this to False.

4. After completing configuration, run the script.

5. Upon successful completeion, a directory named "notaries" will appear in the script directory which contains a .xlsx file.
   The file will be named in the format "notaries_(start_pg_no)-(end_pg_no)"
   If pages 0-10 were scraped, the xlsx filename would be "notaries_0-10"