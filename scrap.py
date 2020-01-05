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

mens_teams_url = 'https://roadtonationals.com/results/chartsM/'
mens_team_base_url = 'https://roadtonationals.com/results/teamsM/dashboard/2020/'

# driver.get(url)
# WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-td")))

# soup = BeautifulSoup(driver.page_source, 'html.parser')
#rows = soup.find(class_='rt-table').find_all(class_='rt-tr')[1:]
# for row in rows:
#     values = row.find_all(class_='rt-td')
#     print(values[0].string+' '+values[1].string)


def get_team_ids(url):
    team_ids = {}
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = soup.find_all(class_='rt-tr-group')
    for element in elements:
        team = element.find('a')
        team_name = team.string
        team_id_strarray = str(team.get('href')).split('/')
        team_id = team_id_strarray[len(team_id_strarray) - 1]
        team_ids[team_name] = team_id
    return team_ids

def get_rosters(team_ids, base_url):
    rosters = {}
    for team_name, team_id in team_ids.items():
        driver.get(base_url + team_id)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find(class_='rt-table').find_all(class_='rt-tr')[1:]
        roster = []
        for row in rows:
            values = row.find_all(class_='rt-td')
            roster.append((values[0].string, values[1].string, values[2].string, values[3].string, values[4].string))    
        rosters[team_name] = roster   
    return rosters

def main():
   # womens_teams_url = 'https://roadtonationals.com/results/charts/'
   # womens_team_base_url = 'https://roadtonationals.com/results/teams/dashboard/2020/'

    mens_teams_url = 'https://roadtonationals.com/results/chartsM/'
    mens_team_base_url = 'https://roadtonationals.com/results/teamsM/dashboard/2020/'

   # womens_team_ids = {}
    mens_team_ids = {}
   # womens_rosters = {}
    mens_rosters = {}

   # womens_team_ids = get_team_ids(womens_teams_url)
    mens_team_ids = get_team_ids(mens_teams_url)

   # womens_rosters = get_rosters(womens_team_ids, womens_team_base_url)
    mens_rosters = get_rosters(mens_team_ids, mens_team_base_url)

    # for team_name, roster in womens_rosters.items():
    #     print(team_name)
    #     print('-------------------------------')
    #     for team_member in roster:
    #         print(team_member)
    #     print()
    # print('---------------------------------------------------------------------')

    for team_name, roster in mens_rosters.items():
        print(team_name)
        print('-------------------------------')
        for team_member in roster:
            print(team_member)
        print()
    print('---------------------------------------------------------------------')

main()
