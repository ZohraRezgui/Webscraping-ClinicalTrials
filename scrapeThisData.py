from selenium import webdriver
from selenium.webdriver.support.ui import Select

import requests
from bs4 import BeautifulSoup
import re

import os
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class ScrapeThatData:
    
    def __init__(self, chrome_webdriver_path, time_threshold = 10):
        os.environ["PATH"] += os.pathsep +chrome_webdriver_path
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver,10)


        self.attribute_dict = {'status':1 ,'conditions':2, 'interventions': 3, 'study type':4, 
                   'phase':5, 'sponsor':6, 'funder type':7 , 'study design': 8,
                   'outcome measures':9, 'number enrolled':10, 'sex':11, 'age':12,
                   'nct number': 13, 'other ids':14, 'title acronym': 15 , 'study start': 16,
                   'primary completion': 17, 'study completion': 18 , 'first posted': 19, 
                   'last update posted': 20 , 'results first posted': 21 , 'locations':22, 'study documents': 23}

        self.status_dict =     {'not yet recruiting' : 'notYetRecrCB',
         'recruiting' : 'rectruitingCB',
         'enrolling by invitation':'enrollingByInvCB',
         'active, not recruiting': 'activeCB',
         'suspended': 'suspendedCB',
         'terminated':'terminatedCB',
         'completed':'completedCB',
         'withdrawn': 'withdrawnCB',
         'unknown status': 'unknownCB'}
    
    def clicking_show_hide_cols(self, driver):
        columns = driver.find_element_by_xpath('//*[@id="theDataTable_wrapper"]/div[3]/button')
        action_chain = ActionChains(driver)
        action_chain.move_to_element(columns).click()
        action_chain.perform()
    
    def select_attributes_to_show(self, listed_attributes, attribute_dict):
        ll = [value.lower() for value in listed_attributes if value.lower() in ['status', 'conditions', 'interventions', 'locations']]
        if ll:
            to_show = [value.lower() for  value in listed_attributes if value.lower() not in ll]
            to_hide = [value for value in ['status', 'conditions', 'interventions', 'locations'] if value not in ll]
            to_click = to_hide + to_show
            for att in to_click:
                self.clicking_show_hide_cols(self.driver)
                time.sleep(1)
                self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="theDataTable_wrapper"]/div[3]/div[2]/button['+ str(attribute_dict[att]) + ']'))).click()
                time.sleep(1)
        else:
            for att in listed_attributes:
                self.clicking_show_hide_cols(self.driver)
                time.sleep(1)
                self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="theDataTable_wrapper"]/div[3]/div[2]/button['+ str(attribute_dict[att.lower()]) + ']'))).click()
                time.sleep(1)

    def select_by_status(self, listed_states, status_dict):
        if listed_states:
            for status in listed_states:
                self.driver.find_element_by_id(status_dict[status.lower()]).click()

            self.driver.find_element_by_xpath('//*[@id="FiltersBody"]/div[1]/input[1]').click()
            time.sleep(3)


        select = Select(self.driver.find_element_by_name('theDataTable_length'))
        select.select_by_value('100')
        
    def collect_data_search_page(self,l_ordered, amount_of_data = None):

        class_name = ''
        page_index = 1
        
        elements = [l_ordered]

        while 'disabled' not in class_name :
           


            time.sleep(5)

            print('Getting data from page {}'.format(page_index))

            #Counting how many rows of the table appear
            table = self.driver.find_element_by_id('theDataTable')
            row_count = len(table.find_elements_by_tag_name("tr")) 

            #Looping table page
            for index in range(1, row_count):
                row = []
                if 'status' in l_ordered:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child(3)')))
                    status_element = self.driver.find_element_by_css_selector('#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child(3) > span')
                    row.append(status_element.text.strip())
                    for i, val  in enumerate(l_ordered):
                        if val == 'status':
                            continue
                        
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child('+str(4+i)+')')))
                        element = self.driver.find_element_by_css_selector('#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child('+str(4+i)+')')
                        try:
                            row.append(element.text.strip())
                        except:
                            print(i, element)
                else:
                    for i, val  in enumerate(l_ordered):
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child('+str(3+i)+')')))
                        element = self.driver.find_element_by_css_selector('#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child('+str(3+i)+')')
                        try:
                            row.append(element.text.strip())
                        except:
                            print(i, element)
                elements.append(row)




            #Getting next page button
            next_page= self.driver.find_element_by_id("theDataTable_next")

            #Getting the class attribute of the next page button
            class_name = next_page.get_attribute('class')

            #Going to the next page
            next_page.click()
            page_index += 1
            if len(elements) >= amount_of_data:
                break
            else:
                continue

        return elements

    def get_criteria(self, NCTnumber):
    
        url = 'https://clinicaltrials.gov/ct2/show/' + NCTnumber
        ClinicalTrialpage = requests.get(url)
        soup = BeautifulSoup(ClinicalTrialpage.text, 'html.parser')

        wrapping_crit_class = soup.find_all("div", {"class": "tr-indent2"})
        list_elements = wrapping_crit_class[1].find_all(re.compile("(ul|ol)"))
        inclusion, exclusion  = ('','')


        if not list_elements:
            print ("WARNING: Study number " + NCTnumber + " doesn't have eligibility criteria or HTML tag format is not a list")
        else:

            if len(list_elements) == 1: 
                try:
                    if wrapping_crit_class[1].find(text = 'Inclusion Criteria:'):
                        inclusion = list_elements[0].find_all("li")

                    elif wrapping_crit_class[1].find(text = 'Exclusion Criteria:'):
                        exclusion = list_elements[0].find_all("li")
                except:
                    print('criteria doesnt exist')
            else:
                inclusion = list_elements[0].find_all("li")
                exclusion = list_elements[1].find_all("li")


        inclusion = [t.text.strip() for t in inclusion ]
        inclusion = ' '.join(inclusion)
        exclusion = [t.text.strip() for t in exclusion ]
        exclusion = ' '.join(exclusion)
        return(inclusion, exclusion)

#function that gets number of patients enrolled in a study
    def get_enrollment (self, NCTnumber):
        url = 'https://clinicaltrials.gov/ct2/show/' + NCTnumber
        ClinicalTrialpage = requests.get(url)
        soup = BeautifulSoup(ClinicalTrialpage.text, 'html.parser')
        enrollment = ''
        wrapping_enrol_class = soup.find_all('td', {'headers':'studyInfoColData','style':"padding-left:1em"})
        if not wrapping_enrol_class:
            print('WARNING: Number of Participants in Study number '+ NCTnumber +' is unavailable')
        else:
            enrollment = wrapping_enrol_class[1]
            enrollment = enrollment.text.split()[0]
            if enrollment.isdigit() == False:
                print ('WARNING: Number of Participants in Study number '+ NCTnumber +' is unavailable')
            else:
                return(enrollment)

    
        
    def __call__(self, condition, listed_attributes, listed_states, amount_of_data):
        
        self.driver.get('https://clinicaltrials.gov/ct2/results?cond=' + condition + '&rank=1&view=record#rowId0')
        self.select_attributes_to_show(listed_attributes, self.attribute_dict)
        self.select_by_status(listed_states, self.status_dict)
        n = []
        for i in listed_attributes: 
            n.append(self.attribute_dict[i.lower()])
        attribute_ordered = [list(self.attribute_dict.keys())[list(self.attribute_dict.values()).index(i)]for i in sorted(n)]
        
        search_data = self.collect_data_search_page(attribute_ordered, amount_of_data=amount_of_data)
        nct_numbers = [e[search_data[0].index('nct number')] for e in search_data[1:]]
        search_data[0].extend(['inclusion', 'exclusion', 'enrollment'])
        for index, nct in enumerate(nct_numbers):
            if index % 100 == 0 and index!= 0:
                print("Collected Data from {} Studies: ".format(index))
        
            inc, exc = self.get_criteria(nct)
            enrol = self.get_enrollment(nct)
            search_data[index + 1].extend([inc, exc, enrol])
                
        return search_data
        