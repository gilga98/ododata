# WARNING: For EDUCATIONAL PURPOSES ONLY! 

from selenium import webdriver
from selenium.webdriver.common import keys
import os
import time
from hashlib import md5
import urllib3
import argparse

# Limit count here
LIMIT_COUNT = 50

# Absolute path of your destination folder
DEST_FOLDER = "D:\datacramp\images2"

# Absolute path of chromedriver
CHROME_DRIVER_PATH = "main/drivers/chromedriver.exe"

# Dont change this
GOOGLE_IMAGES = "https://www.google.com/imghp?hl=en"

# The site from which the images should not be queried
EXCLUDE_SITE = "http://www.indianodonata.org"

#List of all species with count less than 30
SPECIES_LIST = "species.txt"


def download_image(basename, url):
    pool = urllib3.PoolManager()

    md5hash = md5()
    try:
        dest_folder = os.path.join(DEST_FOLDER, str(basename))
        if not os.path.exists(dest_folder):
            os.mkdir(dest_folder)
            
        # To avoid blocks or use user agent, changes needs to be done here    
        response = pool.urlopen(method="GET", url=url)
        # Feel free to have your own hash
        md5hash.update(url.encode())
        with open(os.path.join(dest_folder, md5hash.hexdigest() + ".jpg"), "wb") as fp:
            fp.write(response.data)
    except Exception as e:
        print(e)


def selenium_for_species(species, count):
    browser = webdriver.Chrome(CHROME_DRIVER_PATH)
    browser.get(GOOGLE_IMAGES)
    search_bar = browser.find_element_by_name("q")
    search_string = species + " -site:" + EXCLUDE_SITE
    search_bar.send_keys(search_string)

    search_button = browser.find_element_by_css_selector("button[aria-label='Google Search']")
    search_button.click()

    body = browser.find_element_by_tag_name("body")
    body.send_keys(keys.Keys.PAGE_DOWN)
    body.send_keys(keys.Keys.PAGE_DOWN)
    body.send_keys(keys.Keys.PAGE_DOWN)
    body.send_keys(keys.Keys.PAGE_DOWN)
    # Just in case load
    time.sleep(2)
    all_images = browser.find_elements_by_css_selector("a[jsaction='click:J9iaEb;']")
    url_basket = []
    for element in all_images[:min(count, len(all_images))]:
        # This is necessary to avoid SSL handshake error
        time.sleep(1)
        element.click()
        required_url = element.get_attribute("href")
        url_basket.append(required_url)

    for url in url_basket:
        browser.get(url)
        # Just in case load
        time.sleep(1)
        image_element = browser.find_element_by_xpath("//*[@id='irc_cc']/div/div[2]/div[1]/div[2]/div[1]/a/div/img")
        big_image_url = image_element.get_attribute("src")
        print("Now Downloading:")
        print(big_image_url)
        download_image(species, big_image_url)

    browser.close()


base = []
with open(SPECIES_LIST, "r") as filep:
    for specie in filep.readlines():
        base.append(str(specie).replace("\n", ""))

for specie_name in base:
    try:
        selenium_for_species(specie_name, LIMIT_COUNT)
    except Exception as e:
        print(e)
