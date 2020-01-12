from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import os
from bs4 import BeautifulSoup
import time
# Set up chrome webdriver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920x1080')
chrome_driver = os.getcwd() + '/chromedriver'
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

def get_team_ids(url):
    print("Getting team ids")
    team_ids = {}
    driver.get(url)
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = soup.find_all(class_='rt-tr-group')
    for element in elements:
        team = element.find('a')
        team_name = team.string
        team_id_strarray = str(team.get('href')).split('/')
        team_id = team_id_strarray[len(team_id_strarray) - 1]
        team_ids[team_name] = team_id
    print("Team ids complete")
    return team_ids

def get_rosters(team_ids, base_url, past_url):
    rosters = {}
    print("Getting 2020 rosters")
    for team_name, team_id in team_ids.items():
        print(team_name)
        driver.get(base_url + team_id)
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find(class_='rt-table').find_all(class_='rt-tr')[1:]
        roster = {}
        for row in rows:
            values = row.find_all(class_='rt-td')
            roster[values[0].string + ' ' + values[1].string] = [values[2].string, values[3].string, values[4].string]    
        rosters[team_name] = roster
    print("--------------------------------------------")   
    return rosters

def get_past_averages(past_url, team_ids, rosters):
    averages_team = {}
    print("Getting 2019 averages")
    for team_name, team_id in team_ids.items():
        print(team_name)
        driver.get(past_url + team_id)
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rosterBox")))
        button = driver.find_element_by_xpath('//button[text()="Average"]')
        button.click()
        time.sleep(1)
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[style="min-width: 750px;"]')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        averages = {}
        rows = soup.find(class_='rt-tbody').find_all(class_='rt-tr-group')
        for row in rows:
            #values = row.find_elements_by_class_name('rt-td')
            values = row.find_all(class_='rt-td')
            full_name = values[0].string + ' '  + values[1].string
            if full_name in rosters[team_name].keys():
                indiv_averages = {}
                indiv_averages['FX'] = values[2].string
                indiv_averages['PH'] = values[3].string
                indiv_averages['SR'] = values[4].string
                indiv_averages['VT'] = values[5].string
                indiv_averages['PB'] = values[6].string
                indiv_averages['HB'] = values[7].string
                indiv_averages['AA'] = values[8].string
                averages[full_name] = indiv_averages
        averages_team[team_name] = averages
    print("--------------------------------------------")   
    return averages_team





def main():
   # womens_teams_url = 'https://roadtonationals.com/results/charts/'
   # womens_team_base_url = 'https://roadtonationals.com/results/teams/dashboard/2020/'

    mens_teams_url = 'https://roadtonationals.com/results/chartsM/'
    mens_team_base_url = 'https://roadtonationals.com/results/teamsM/dashboard/2020/'
    mens_team_past_url = 'https://roadtonationals.com/results/teamsM/dashboard/2019/'

   # womens_team_ids = {}
    mens_team_ids = {}
   # womens_rosters = {}
    mens_rosters = {}

   # womens_team_ids = get_team_ids(womens_teams_url)
    mens_team_ids = get_team_ids(mens_teams_url)

   # womens_rosters = get_rosters(womens_team_ids, womens_team_base_url)
    mens_rosters = get_rosters(mens_team_ids, mens_team_base_url, mens_team_past_url)

    mens_averages = get_past_averages(mens_team_past_url, mens_team_ids, mens_rosters)
    # for team_name, roster in womens_rosters.items():
    #     print(team_name)
    #     print('-------------------------------')
    #     for team_member in roster:
    #         print(team_member)
    #     print()
    # print('---------------------------------------------------------------------')
    print("2020 ROSTERS")
    for team_name, roster in mens_rosters.items():
        print(team_name)
        print('-------------------------------')
        for team_member, infos  in roster.items():
            print(team_member)
            for info in infos:
                print(info)
            print("-------------")
        print()
    print('---------------------------------------------------------------------')

    print("2019 AVERAGES")
    for team_name, averages in mens_averages.items():
        print(team_name)
        print('-------------------------------')
        for team_member, events in averages.items():
            print(team_member)
            for event in events:
                print(event + ': ' + str(mens_averages[team_name][team_member][event]))
            print("-------------")
        print()
    print('---------------------------------------------------------------------')   

main()
