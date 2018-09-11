from selenium import webdriver
from selenium.webdriver.support.ui import Select

import os
import time

#Must download Chrome driver and save it in folder of your choice. The instruction below 
#sets the path of the python environment to where the driver is located

os.environ["PATH"] += os.pathsep + r'C:\Users\zohra.rezgui\Documents\Selenium';
driver = webdriver.Chrome()


#condition to be searched in the site
condition = 'Breast+Cancer'
#Opening URL
driver.get("https://clinicaltrials.gov/ct2/results?cond="+ condition +"&rank=1&view=record#rowId0")




from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains



#defining a waiting parameter
wait = WebDriverWait(driver,10)


#function to click the Show/Hide columns button. Since choosing a column results in a fading window, this function uses Actions
#chain to make sure the driver can click on the Show/hide button again 
def clicking_show_hide_cols():
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="theDataTable_wrapper"]/div[3]/button')))
    columns = driver.find_element_by_xpath('//*[@id="theDataTable_wrapper"]/div[3]/button')
    action_chain = ActionChains(driver)
    action_chain.move_to_element(columns).click()
    action_chain.perform()
    return None

#Show/Hide click
clicking_show_hide_cols()
#waiting 1 second for window to appear
time.sleep(1)

#Hiding conditions column
wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="theDataTable_wrapper"]/div[3]/div/button[2]'))).click() 
time.sleep(1)

#Show/Hide click
clicking_show_hide_cols()
time.sleep(1)

#Hiding Interventions Button
wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="theDataTable_wrapper"]/div[3]/div/button[3]'))).click()
time.sleep(1)

#Show/Hide click
clicking_show_hide_cols()
time.sleep(1)

#Showing NCT Number
wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="theDataTable_wrapper"]/div[3]/div/button[13]'))).click()
time.sleep(1)

#Show/Hide click
clicking_show_hide_cols()
time.sleep(1)

#Hiding Locations Column
wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="theDataTable_wrapper"]/div[3]/div/button[22]'))).click()
time.sleep(1)


#Selecting Status of Studies
driver.find_element_by_id('suspendedCB').click()
driver.find_element_by_id('terminatedCB').click()
driver.find_element_by_id('withdrawnCB').click()
driver.find_element_by_id('completedCB').click()

#Applying Selection
driver.find_element_by_xpath('//*[@id="FiltersBody"]/div[1]/input[1]').click()
time.sleep(3)


#showing 100 observations per page
select = Select(driver.find_element_by_name('theDataTable_length'))
select.select_by_value('100')




#Collecting NCT Numbers and Status from Search Page


class_name = ''

NCT_Number = []

Status =  []

page_index = 1


while 'disabled' not in class_name :

    time.sleep(5)
    
    print('Getting data from page {}'.format(page_index))
    
    #Counting how many rows of the table appear
    table = driver.find_element_by_id('theDataTable')
    row_count = len(table.find_elements_by_tag_name("tr")) 
    
    #Looping table page
    for index in range(1, row_count):
        
        #Waiting till the elements are loaded
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child(5)')))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child(3) > span')))
        
        #Getting the elements
        nct_element = driver.find_element_by_css_selector('#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child(5)')
        status_element = driver.find_element_by_css_selector('#theDataTable > tbody > tr:nth-child('+str(index)+') > td:nth-child(3) > span')
        
        #Appending them to lists
        NCT_Number.append(nct_element.text.strip())
        Status.append(status_element.text.strip())
    
    #Getting next page button
    next_page= driver.find_element_by_id("theDataTable_next")
    
    #Getting the class attribute of the next page button
    class_name = next_page.get_attribute('class')
    
    #Going to the next page
    next_page.click()
    page_index += 1
    print('Collected {} NCT Numbers'.format(len(NCT_Number)))
   



import requests
from bs4 import BeautifulSoup
import re


#function that gets Separated Inclusion and Exclusion Criteria from a study
def get_criteria(NCTnumber):
    
    
    #Getting the html page
    url = 'https://clinicaltrials.gov/ct2/show/' + NCTnumber
    ClinicalTrialpage = requests.get(url)
    soup = BeautifulSoup(ClinicalTrialpage.text, 'html.parser')
    
    #the Eligibility criteria has to be in a list format for this to work, ordered or not ordered
    wrapping_crit_class = soup.find_all("div", {"class": "indent1"})
    wrapping_crit_class = wrapping_crit_class[1].find_all("div", {"class":"indent2"})
    list_elements = wrapping_crit_class[1].find_all(re.compile("(ul|ol)"))
    inclusion, exclusion  = ('','')
    

    if not list_elements:
        print ("WARNING: Study number " + NCTnumber + " doesn't have eligibility criteria or HTML tag format is not a list")
    else:

        if len(list_elements) == 1: 
            if wrapping_crit_class[1].find(text = 'Inclusion Criteria:'):
                inclusion = list_elements[0].find_all("li")
                
            elif wrapping_crit_class[1].find(text = 'Exclusion Criteria:'):
                exclusion = list_elements[0].find_all("li")

        else:
            inclusion = list_elements[0].find_all("li")
            exclusion = list_elements[1].find_all("li")
     
  
    inclusion = [t.text.strip() for t in inclusion ]
    inclusion = ' '.join(inclusion)
    exclusion = [t.text.strip() for t in exclusion ]
    exclusion = ' '.join(exclusion)
    return(inclusion, exclusion)

#function that gets number of patients enrolled in a study
def get_enrollment (NCTnumber):
    url = 'https://clinicaltrials.gov/ct2/show/' + NCTnumber
    ClinicalTrialpage = requests.get(url)
    soup = BeautifulSoup(ClinicalTrialpage.text, 'html.parser')
    enrollment = ''
    wrapping_enrol_class = soup.find_all('table', {'class':'layout_table','summary':'Layout table for study information', 'style':'margin-bottom:2ex;'})
    if not wrapping_enrol_class:
        print('WARNING: Number of Participants in Study number '+ NCTnumber +' is unavailable')
    else:
        enrollment = wrapping_enrol_class[0].find_all('td',{'headers':'studyInfoColData', 'style':'padding-left:1em'})[1]
        enrollment = enrollment.text.split()[0]
        if enrollment.isdigit() == False:
            print ('WARNING: Number of Participants in Study number '+ NCTnumber +' is unavailable')
        else:
            return(enrollment)
        
    

#function that gets the country, region of the study
def get_location (NCTnumber):
    url = 'https://clinicaltrials.gov/ct2/show/' + NCTnumber
    ClinicalTrialpage = requests.get(url)
    soup = BeautifulSoup(ClinicalTrialpage.text, 'html.parser')
    location = ''
    wrapping_loc_class = soup.find_all('table', {'class':'layout_table indent2', 'summary':'Layout table for location information'})
    if not wrapping_loc_class:
        print('WARNING: location in Study number '+ NCTnumber +' is unavailable')
    else:
        location = wrapping_loc_class[0].find_all('td', {'class':'header3'})[0]
        location = location.text.strip()
        
    return(location)

#function that gets the study center 
def get_study_center( NCTnumber):
    url = 'https://clinicaltrials.gov/ct2/show/' + NCTnumber
    ClinicalTrialpage = requests.get(url)
    soup = BeautifulSoup(ClinicalTrialpage.text, 'html.parser')
    center = ''
    wrapping_center_class = soup.find_all('table', {'class':'layout_table indent2', 'summary':'Layout table for location information'})
    if not wrapping_center_class:
        print('WARNING: Study Center in Study number '  + NCTnumber + ' is unavailable')
    else:
        center = wrapping_center_class[0].find('td', {'headers': 'locName'})
        center = center.text.strip()
        
    return (center)

#Main function using all previous functions
def get_data(NCT_list):
    inclusion_list = []
    exclusion_list = []
    enrollment_list = []
    location_list = []
    center_list = []
    for index in range(len(NCT_list)):
        if (index % 100 == 0):
            print("Collected Data from {} Studies: ".format(index))
        
        inc, exc = get_criteria(NCT_list[index])
        enrol = get_enrollment(NCT_list[index])
        loc = get_location(NCT_list[index])
        ctr = get_study_center(NCT_list[index])
        
        inclusion_list.append(inc)
        exclusion_list.append(exc)
        enrollment_list.append(enrol)
        location_list.append(loc)
        center_list.append(ctr)
        
        
    return(inclusion_list, exclusion_list, enrollment_list, location_list, center_list)
    
Inclusion, Exclusion, Enrollment, Location, Center = get_data(NCT_Number)




#Merging into df and saving into excel
import pandas as pd
dataset = pd.DataFrame({ 'Study Identifier': NCT_Number, 'Status': Status,'Location (Country)': Location, 'Center': Center ,'Number of Patients Enrolled': Enrollment, 'Inclusion': Inclusion, 'Exclusion': Exclusion})


writer = pd.ExcelWriter(r'C:\Users\zohra.rezgui\Documents\clinicaltrials.xlsx')
dataset.to_excel(writer)
writer.save()





