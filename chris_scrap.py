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

def get_team_ids(url):
    team_ids = {}
    # Navigate webdriver to URL for list of teams
    driver.get(url)
    # Wait for page to load
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
    # Get all table rows (one for each team)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = soup.find_all(class_='rt-tr-group')
    # For each table row (team)
    for element in elements:
        # Get the <a href='...'> tag in the row
        team = element.find('a')
        # Get the team name
        team_name = team.string
        # Split the href attribute of the <a> tag into a string array e.g 'https://roadtonationals.com/results/teams/dashboard/2020/1' -> ['https:', 'roadtonationals.com', 'results', 'teams', 'dashboard', '2020', '1']
        team_id_strarray = str(team.get('href')).split('/')
        # Get the team id which is the last element in the string array e.g. 1
        team_id = team_id_strarray[len(team_id_strarray) - 1]
        # Assign team name -> team id
        team_ids[team_name] = team_id
    return team_ids

# Method to get rosters for teams given (team name -> team id)
# Returns (team name -> team roster)
def get_rosters(team_ids, base_url):
    rosters = {}
    # For every (team name -> team id) in dictionary storing team name -> team id
    for team_name, team_id in team_ids.items():
        # Navigate webdriver to URL for roster for team
        driver.get(base_url + team_id)
        # Wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
        # Get all table rows (one for each team member)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find(class_='rt-table').find_all(class_='rt-tr')[1:]
        # Initialize empty roster
        roster = []
        # For each table row (team member)
        for row in rows:
            # Get first name, last name, hometown, year, and events for team member
            values = row.find_all(class_='rt-td')
            # Append team member to roster
            roster.append((values[0].string, values[1].string, values[2].string, values[3].string))    
        # Set team roster to roster
        rosters[team_name] = roster   
    return rosters

def main():
    # Declare URL for list of all womens gymnastics teams
    womens_teams_url = 'https://roadtonationals.com/results/charts/'
    # Declare base URL for individual teams
    womens_team_base_url = 'https://roadtonationals.com/results/teams/dashboard/2020/'

    # Declare URL for list of all mens gymnastics teams
    mens_teams_url = 'https://roadtonationals.com/results/chartsM/'
    # Declare base URL for individual teams
    mens_team_base_url = 'https://roadtonationals.com/results/teamsM/dashboard/2020/'

    # Declare dictionary storing team name -> team id
    womens_team_ids = {}
    mens_team_ids = {}
    # Declare dictionary storing team name -> team roster
    womens_rosters = {}
    mens_rosters = {}

    # Get team ids for womens and mens teams
#    womens_team_ids = get_team_ids(womens_teams_url)
    mens_team_ids = get_team_ids(mens_teams_url)

    # Get rosters for mens and womens teams
#    womens_rosters = get_rosters(womens_team_ids, womens_team_base_url)
    mens_rosters = get_rosters(mens_team_ids, mens_team_base_url)

    # Print womens rosters
    # for team_name, roster in womens_rosters.items():
    #     print(team_name)
    #     print('-------------------------------')
    #     for team_member in roster:
    #         print(team_member)
    #     print()
    # print('---------------------------------------------------------------------')

    # Print mens rosters
    for team_name, roster in mens_rosters.items():
        print(team_name)
        print('-------------------------------')
        for team_member in roster:
            print(team_member)
        print()
    print('---------------------------------------------------------------------')

# Run program
main()
