from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os

Options = webdriver.ChromeOptions()
Options.add_argument('--no-sandbox')
Options.add_argument('--disable-dev-shm-usage')
Options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
Options.add_argument('--start-maximized')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=Options)
shops_data = []

with open('germany.txt', 'r', encoding='utf-8') as f:
    countries = f.read().splitlines()

def appendProduct(file_path2, data):
    temp_file = 'temp_file.csv'
    if os.path.isfile(file_path2):
        df = pd.read_csv(file_path2, encoding='utf-8')
    else:
        df = pd.DataFrame()

    df_new_row = pd.DataFrame([data])
    df = pd.concat([df, df_new_row], ignore_index=True)

    try:
        df.to_csv(temp_file, index=False, encoding='utf-8')
    except Exception as e:
        print(f"An error occurred while saving the temporary file: {str(e)}")
        return False

    try:
        os.replace(temp_file, file_path2)
    except Exception as e:
        print(f"An error occurred while replacing the original file: {str(e)}")
        return False

    return True

def scrape_data():
    driver.get('https://www.roco.cc/rde/haendler')
    time.sleep(5)
    postcode = driver.find_element(By.CSS_SELECTOR, "input[class$='myhaendselplz']")
    postcode.send_keys('1010')
    time.sleep(2)
    for country in countries:
        select_country = Select(driver.find_element(By.CSS_SELECTOR, "select[id='country']"))
        select_country.select_by_visible_text(country)
        time.sleep(1)
        select_radius = Select(driver.find_element(By.CSS_SELECTOR, "select[id='radius']"))
        select_radius.select_by_index(6)
        time.sleep(15)

        rows = driver.find_elements(By.CSS_SELECTOR, "div[id='tcustomertable'] div[class='row']")
        for row in rows:
            company_name = row.find_element(By.CSS_SELECTOR, "div:nth-of-type(1)").text
            street = row.find_element(By.CSS_SELECTOR, "div:nth-of-type(2)").text
            postal_code = row.find_element(By.CSS_SELECTOR, "div:nth-of-type(3)").text
            city = row.find_element(By.CSS_SELECTOR, "div:nth-of-type(4)").text

            try:
                website_element = WebDriverWait(row, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.myListLast a"))
                )
                website = website_element.get_attribute('href')
            except (NoSuchElementException, TimeoutException):
                website = ''

            data = {
                'Company Name': company_name,
                'Street': street,
                'Postal Code': postal_code,
                'City': city,
                'Website': website,
                'Country': country
            }
            shops_data.append(data)
            appendProduct('shops_data.csv', data)
    return shops_data

data = scrape_data()


driver.quit()
