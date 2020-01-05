from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import os
from bs4 import BeautifulSoup

# Set up chrome webdriver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920x1080')
chrome_driver = os.getcwd() + '/chromedriver'
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

url = 'https://roadtonationals.com/results/teamsM/dashboard/2019/51'
driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-td")))

soup = BeautifulSoup(driver.page_source, 'html.parser')
rows = soup.find(class_='rt-table').find_all(class_='rt-tr')[1:]
for row in rows:
    # Get first name, last name, hometown, year, and events for team member
    values = row.find_all(class_='rt-td')
    # Append team member to roster
    print(values[0].string+' '+values[1].string)