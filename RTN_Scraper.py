from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import os
import platform
from bs4 import BeautifulSoup
import time
import pandas as pd
import csv
import requests

# Set up chrome webdriver
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920x1080')
# differentiate based on operating system
chrome_driver = os.getcwd()
if platform.system() == "Darwin":
    chrome_driver += "/chromedriver_mac"
elif platform.system() == "Linux":
    chrome_driver += "/chromedriver_lin"
else:
    chrome_driver += "/chromedriver_win.exe"
driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,TimeoutException,)

def get_team_ids(url, year):
    print("Getting " + year + " team ids")
    team_ids = {}
    driver.get(url)
    WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(lambda d: d.execute_script("return document.readyState") == "complete")
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.ID, "year_filter")))
    select = Select(driver.find_element_by_id("year_filter"))
    select.select_by_visible_text(year)
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "rt-td")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find_all(class_='rt-tr-group')
    for row in rows:
        team = row.find('a')
        team_name = team.string
        team_id_strarray = str(team.get('href')).split('/')
        team_id = team_id_strarray[len(team_id_strarray) - 1]
        team_ids[team_name] = team_id
    print("Team ids complete")
    print("--------------------------------------------")
    return team_ids

def get_rosters(team_ids, base_url, year):
    rosters = {}
    print("Getting " + year + " rosters")
    print("--------------------------------------------")
    for team_name, team_id in team_ids.items():
        print(team_name)
        driver.get(base_url + '/' + year + '/' + team_id)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find(class_='rosterBox').find(class_='rt-table').find_all(class_='rt-tr-group')
        roster = {}
        for row in rows:
            values = row.find_all(class_='rt-td')
            full_name = values[0].string + ' '  + values[1].string
            roster[full_name] = [values[2].string, values[3].string, values[4].string]    
        rosters[team_name] = roster
    print("--------------------------------------------")   
    return rosters

def get_all_individual_averages(base_url, year, team_ids, rosters):
    averages_team = {}

    print("Getting " + year + " averages")
    print("--------------------------------------------")  
    for team_name, team_id in team_ids.items():
        print(team_name)
        driver.get(base_url + '/' + year + '/' + team_id)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rosterBox")))
        button = driver.find_element_by_xpath('//button[text()="Average"]')
        button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[style="min-width: 750px;"]')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        averages = {}

        rows = soup.find(class_='rosterBox').find(class_='rt-table').find_all(class_='rt-tr-group')
        for row in rows:            
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

def get_team_scores(team_ids, base_url, year):
    team_scores = {}
    print("Getting " + year + " team scores")
    print("--------------------------------------------")
    driver.get(base_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "allteamscores")))
    button = driver.find_element_by_xpath("//button[text()='All Team Scores']")
    button.click()
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
    select = Select(driver.find_element_by_id("year_filter"))
    select.select_by_visible_text(year)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find(class_='rt-table').find(class_='rt-tbody').find_all(class_='rt-tr-group')
    for team_name, team_id in team_ids.items():
        print(team_name)
        scores = {}
        for row in rows:
            values = row.find_all(class_='rt-td')
            if values[0].string == team_name:
                scores[values[1].string] = values[8].string
        team_scores[team_name] = scores
    print("--------------------------------------------")  
    return team_scores

def get_ncaa_team_scores(team_ids, base_url, year, ncaa=True):
    team_scores = {}
    print("Getting " + year + " team NCAA scores")
    print("--------------------------------------------")
    for team_name, team_id in team_ids.items():
        print(team_name)
        driver.get(base_url + '/' + year + '/' + team_id)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "scheduleBox")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find(class_='scheduleBox').find(class_='rt-tbody').find_all(class_='rt-tr')
        scores = {}
        for row in rows:
            values = row.find_all(class_='rt-td')
            if str(values[2].string) != "None" and float(values[2].string) != 0.0:
                # gets ONLY NCAA scores
                if ncaa == True and "NCAA" in str(values[5].string):
                    scores[values[1].string[5:]] = values[2].string
                # gets every non-NCAA score
                elif ncaa == False and not("NCAA" in str(values[5].string)):
                    scores[values[1].string[5:]] = values[2].string
        team_scores[team_name] = scores
    print("--------------------------------------------")  
    return team_scores

def get_all_individual_scores(athlete_base_url, year, team_ids, rosters):
    scores_ind_team = {}
    print("Getting " + year + " individual scores")
    print("--------------------------------------------")  
    for team_name, team_id in team_ids.items():
        meet = {}
        print(team_name)
        print("-------------------------------------------------------------------------")
        driver.get(athlete_base_url + '/' + year + '/' + team_id)
        time.sleep(1)
        # WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-table")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        scores = {}
        print("ROSTER SIZE: " + str(len(rosters[team_name])))
        for index in range(len(rosters[team_name])):
            select = Select(driver.find_element_by_id('gymnast_filter'))
            athlete_names = soup.find(id='gymnast_filter').find_all('option')
            print(athlete_names[index].string)
            select.select_by_visible_text(athlete_names[index].string)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tbody")))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            rows = soup.find(class_='rt-tbody').find_all(class_='rt-tr-group')
            athlete_name = athlete_names[index].string
            if len(rows)>0:
                for row in rows:
                    values = row.find_all(class_='rt-td')
                    print("-----------------------")
                    print(values[0].string[5:])
                    print('FX: ', values[3].string)
                    print('PH: ', values[4].string)
                    print('SR: ', values[5].string)
                    print('VT: ', values[6].string)
                    print('PB: ', values[7].string)
                    print('HB: ', values[8].string)
                    print('AA: ', values[9].string)
                    ind_scores = {}
                    ind_scores['FX'] = values[3].string
                    ind_scores['PH'] = values[4].string
                    ind_scores['SR'] = values[5].string
                    ind_scores['VT'] = values[6].string
                    ind_scores['PB'] = values[7].string
                    ind_scores['HB'] = values[8].string
                    ind_scores['AA'] = values[9].string
                    meet[values[0].string[5:]] = ind_scores
            scores[athlete_name] = meet
            print("------------------------------")   
        scores_ind_team[team_name] = scores
    print("---------------------------------------------------------") 
    return scores_ind_team     

def get_team_NQAs(base_url, year):
    print("Getting " + year + " team NQA scores")
    print("--------------------------------------------")
    team_NQAs = {}
    driver.get(base_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "year_filter")))
    select = Select(driver.find_element_by_id("year_filter"))
    select.select_by_visible_text(year)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rt-tr-group")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find(class_='rt-table').find(class_='rt-tbody').find_all(class_='rt-tr-group')
    for row in rows:
            values = row.find_all(class_='rt-td')
            team_NQAs[values[1].string] = values[4].string
            print(values[1].string, ": ", values[4].string)
    print("--------------------------------------------")  
    return team_NQAs

# gets teams margin of victories
def get_team_MOVs(team_ids, base_url, year, ncaa=False):
    team_movs = {}
    print("Getting " + year + " Team Margin of Victories")
    print("--------------------------------------------")
    for team_name, team_id in team_ids.items():
        print(team_name)
        mov_list = []
        if(year != "2014" or team_name != "Penn State"):
            driver.get(base_url + '/' + year + '/' + team_id)
            WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(lambda d: d.execute_script("return document.readyState") == "complete")
            WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'scheduleBox')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            rows = soup.find(class_='scheduleBox').find(class_='rt-tbody').find_all(class_='rt-tr')
            for i, row in enumerate(rows):
                values = row.find_all(class_='rt-td')
                if str(values[2].string) != "None" and float(values[2].string) != 0.0:
                    if ncaa == False and "NCAA" in str(values[5].string):
                        continue
                    else:
                        # click on meet link
                        WebDriverWait(driver, 40, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_all_elements_located((By.LINK_TEXT, 'View')))
                        meet_links = driver.find_elements_by_link_text('View')
                        # print(len(meet_links))
                        link = meet_links[i].get_attribute('href')
                        if link == "https://roadtonationals.com/results/scheduleM/meet/0":
                            mov_list.append(-23.65)
                            continue
                        # print(link)
                        meet_links[i].click()
                        WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'teamsbox')))
                        driver.get(link)
                        WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(lambda d: d.execute_script("return document.readyState") == "complete")
                        WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'rt-tr')))
                        meet_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        meet_rows = meet_soup.find(class_='teamsbox').find(class_='rt-tbody').find_all(class_='rt-tr')
                        meet_movs = []
                        winner = False
                        for meet_row in meet_rows:
                            meet_values = meet_row.find_all(class_='rt-td')
                            # get current team margin of victory
                            # if zero, get lowest absolute value of other team leads
                            mov = float(meet_values[10].string)
                            if mov != 0.0:
                                meet_movs.append(abs(mov))
                            if meet_values[1].string == team_name:
                                if mov != 0.0:
                                    mov_list.append(mov)
                                else:
                                    winner = True
                        if winner and not len(meet_movs) == 0:
                            mov_list.append(min(meet_movs))
                        print(mov_list)
                        driver.back()
                        WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(lambda d: d.execute_script("return document.readyState") == "complete")
        team_movs[team_name] = mov_list
    print("--------------------------------------------")  
    return team_movs

# get team schedules
def get_team_schedules(team_ids, base_url, year, ncaa=False):
    team_schedules = {}
    print("Getting " + year + " Team Schedules")
    print("--------------------------------------------")
    for team_name, team_id in team_ids.items():
        print(team_name)
        schedule = []
        if(year != "2014" or team_name != "Penn State"):
            driver.get(base_url + '/' + year + '/' + team_id)
            WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(lambda d: d.execute_script("return document.readyState") == "complete")
            WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'scheduleBox')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            rows = soup.find(class_='scheduleBox').find(class_='rt-tbody').find_all(class_='rt-tr')
            for i, row in enumerate(rows):
                values = row.find_all(class_='rt-td')
                if str(values[2].string) != "None" and float(values[2].string) != 0.0:
                    if ncaa == False and "NCAA" in str(values[5].string):
                        continue
                    else:
                        # click on meet link
                        WebDriverWait(driver, 40, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_all_elements_located((By.LINK_TEXT, 'View')))
                        meet_links = driver.find_elements_by_link_text('View')                       
                        link = meet_links[i].get_attribute('href')
                        if link == "https://roadtonationals.com/results/scheduleM/meet/0":
                            schedule.append("Navy")
                            continue
                        meet_links[i].click()
                        WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'teamsbox')))
                        driver.get(link)
                        WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(lambda d: d.execute_script("return document.readyState") == "complete")
                        WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'rt-tr')))
                        meet_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        meet_rows = meet_soup.find(class_='teamsbox').find(class_='rt-tbody').find_all(class_='rt-tr')
                        meet_movs = []
                        winner = False
                        for meet_row in meet_rows:
                            meet_values = meet_row.find_all(class_='rt-td')
                            # get current team margin of victory
                            # if zero, get lowest absolute value of other team leads
                            mov = float(meet_values[10].string)
                            if meet_values[1].string != team_name and mov == 0.0:
                                schedule.append(meet_values[1].string)
                                break
                            elif meet_values[1].string != team_name:
                                schedule.append(meet_values[1].string)
                                break
                        print(schedule)
                        driver.back()
                        WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(lambda d: d.execute_script("return document.readyState") == "complete")
        team_schedules[team_name] = schedule
    print("--------------------------------------------")  
    return team_schedules
            

if __name__ == "__main__":
   # womens_teams_url = 'https://roadtonationals.com/results/charts/'
   # womens_team_base_url = 'https://roadtonationals.com/results/teams/dashboard/2020/'
    mens_final_scores_url = 'https://roadtonationals.com/results/standingsM/final'
    mens_teams_url = 'https://roadtonationals.com/results/chartsM/allteams'
    mens_athletes_url = 'https://roadtonationals.com/results/teamsM/gymnast'
    mens_team_base_url = 'https://roadtonationals.com/results/teamsM/dashboard'
    
    # mens_NQAs = get_team_NQAs(mens_final_scores_url, "2019")
    # mens_team_ids = get_team_ids(mens_teams_url, "2019")
    # mens_rosters = get_rosters(mens_team_ids, mens_team_base_url, "2020")
    # mens_averages = get_all_individual_averages(mens_team_base_url, "2020", mens_team_ids, mens_rosters)
    # mens_team_scores = get_team_scores(mens_team_ids, mens_teams_url, "2019")
    # mens_ind_scores = get_all_individual_scores(mens_athletes_url, "2020", mens_team_ids, mens_rosters)
    # mens_ncaa_team_scores = get_ncaa_team_scores(mens_team_ids, mens_team_base_url, "2019", ncaa=False)
    # print(mens_ncaa_team_scores)
    # get_team_MOVs(mens_team_ids, mens_team_base_url, "2019")
    # get_team_schedules(mens_team_ids, mens_team_base_url, "2019")

    # NQA Scores
    # path = 'C:/Users/jbkul/Desktop/NQA_System_Research/NQA_scores_data/'
    # rtn_years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    # for year in rtn_years:
    #     mens_NQAs = get_team_NQAs(mens_final_scores_url, year)
    #     filename = year + '_M_NQAs.csv'
    #     with open(path + filename, 'w', newline='') as f:
    #         teams = list(mens_NQAs.keys())
    #         writer = csv.DictWriter(f, fieldnames=teams)
    #         writer.writeheader()
    #         writer.writerow(mens_NQAs)

    # write csv files for all of the mens team scores
    # year.csv
    # team name for field names
    # meet dates
    # meet scores
    # path = 'C:/Users/jbkul/Desktop/NQA_System_Research/ncaa_scores_data/'
    # rtn_years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    # for year in rtn_years:
    #     mens_team_ids = get_team_ids(mens_teams_url, year)
    #     mens_team_scores = get_ncaa_team_scores(mens_team_ids, mens_team_base_url, year, ncaa=False)
    #     filename = year + '_M_no_ncaa_scores.csv'
    #     with open(path + filename, 'w', newline='') as f:
    #         writer = csv.writer(f)
    #         for team in mens_team_scores:
    #             writer.writerow([team])
    #             dates = list(mens_team_scores[team].keys())
    #             score_writer = csv.DictWriter(f, fieldnames=dates)
    #             score_writer.writeheader()
    #             score_writer.writerow(mens_team_scores[team])
    
    # BETTER SCORE WRITER
    # team's scores per column
    # path = 'C:/Users/jbkul/Desktop/NQA_System_Research/ncaa_scores_data/'
    # rtn_years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    # for year in rtn_years:
    #     mens_team_ids = get_team_ids(mens_teams_url, year)
    #     mens_team_scores = get_ncaa_team_scores(mens_team_ids, mens_team_base_url, year, ncaa=False)
    #     filename = year + '_M_no_ncaa_scores.csv'
    #     print("Writing " + filename + "..."+"\n--------------------------------------------")
    #     data = list()
    #     teams = list(mens_team_scores.keys())
    #     n = len(max(mens_team_scores.values(), key=len))
    #     data.append(teams)
    #     for i in range(n):
    #         row = list()
    #         for team in mens_team_scores:
    #             if i < len(list(mens_team_scores[team].values())):
    #                 row.append(list(mens_team_scores[team].values())[i])
    #             else:
    #                 row.append(None)
    #         data.append(row)
    #     with open(path + filename, 'w', newline='') as f:
    #         score_writer = csv.writer(f)
    #         for row in data:
    #             score_writer.writerow(row)

    # MOV WRITER
    # team's movs per column
    # path = 'C:/Users/jbkul/Desktop/NQA_System_Research/movs_data/'
    # rtn_years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    # for year in rtn_years:
    #     mens_team_ids = get_team_ids(mens_teams_url, year)
    #     mens_team_movs = get_team_MOVs(mens_team_ids, mens_team_base_url, year)
    #     filename = year + '_M_movs1.csv'
    #     print("Writing " + filename + "..."+"\n--------------------------------------------")
    #     data = list()
    #     teams = list(mens_team_movs.keys())
    #     n = len(max(mens_team_movs.values(), key=len))
    #     data.append(teams)
    #     for i in range(n):
    #         row = list()
    #         for team in mens_team_movs:
    #             if i < len(list(mens_team_movs[team])):
    #                 row.append(list(mens_team_movs[team])[i])
    #             else:
    #                 row.append(None)
    #         data.append(row)
    #     with open(path + filename, 'w', newline='') as f:
    #         csv_writer = csv.writer(f)
    #         for row in data:
    #             csv_writer.writerow(row)

    # SCHEDULE WRITER
    # teams' schedule per column
    path = 'C:/Users/jbkul/Desktop/NQA_System_Research/schedules_data/'
    # rtn_years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    rtn_years = ['2012', '2013', '2015', '2016', '2017', '2018', '2019']
    for year in rtn_years:
        mens_team_ids = get_team_ids(mens_teams_url, year)
        mens_team_schedules = get_team_schedules(mens_team_ids, mens_team_base_url, year)
        filename = year + '_M_schedules1.csv'
        print("Writing " + filename + "..."+"\n--------------------------------------------")
        data = list()
        teams = list(mens_team_schedules.keys())
        n = len(max(mens_team_schedules.values(), key=len))
        data.append(teams)
        for i in range(n):
            row = list()
            for team in mens_team_schedules:
                if i < len(list(mens_team_schedules[team])):
                    row.append(list(mens_team_schedules[team])[i])
                else:
                    row.append(None)
            data.append(row)
        with open(path + filename, 'w', newline='') as f:
            csv_writer = csv.writer(f)
            for row in data:
                csv_writer.writerow(row)

    # for team in mens_team_scores:
    #     print("--------------------------------------------")
    #     print(team)
    #     dates = list(mens_team_scores[team].keys())
    #     for date in mens_team_scores[team].keys():
    #         print(date)
    #         print(mens_team_scores[team][date])

    # print("2020 Rosters")
    # for team_name, roster in mens_rosters.items():
    #     print(team_name)
    #     print('-------------------------------')
    #     for team_member, infos  in roster.items():
    #         print(team_member)
    #         for info in infos:
    #             print(info)
    #         print("-------------")
    #     print()
    # print('---------------------------------------------------------------------')

    # print("2019 Averages")
    # for team_name, averages in mens_averages.items():
    #     print(team_name)
    #     print('-------------------------------')
    #     for team_member, events in averages.items():
    #         print(team_member)
    #         for event in events:
    #             print(event + ': ' + str(mens_averages[team_name][team_member][event]))
    #         print("-------------")
    #     print()
    # print('---------------------------------------------------------------------')   
    
    # print("Team Scores")
    #  for team, scores in mens_team_scores.items():
    #     print(team)
    #     for date, score in scores.items():
    #         print(str(date) + " : " + str(score))
        # print("2020 Rosters")
   
    # for team_name, scores in mens_ind_scores.items():
    #     print(team_name)
    #     print('-------------------------------')
    #     for athlete, meet  in scores.items():
    #         print(athlete)
    #         for meet_name, events in meet.items():
    #             print(meet_name)
    #             for event, event_scores, in events.items():
    #                 print(event+" : "+event_scores)
    #         print("-------------")
    #     print()
    # print('---------------------------------------------------------------------')

