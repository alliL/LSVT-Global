import re
import csv
import time
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime

# to time how long the script runs
start_time = datetime.now()

# Accepts an array and a string
# Inserts value into the array. If the value is NoneType or an empty string,
# 'NA' is inserted instead.
def insert_value(clinician, value):
    if value == None or value == "":
        clinician = np.append(clinician, values='NA')
    else:
        clinician = np.append(clinician, values=value)
    return clinician

# all values that are being collected
attributes = ['Clinician URL', 'Image URL', 'Category', 'First Name',
              'Last Name', 'Title', 'Office Name', 'Address', 'City',
              'State', 'Zip/Postal Code','Country', 'Phone', 'Fax', 'Email',
              'Website', 'Alternate Office Website', 'Alternate Office State',
              'Alternate Office Country', 'Languages Spoken',
              'Type of Facility',
              'Does Your Facility Offer Both LSVT BIG & LSVT LOUD',
              'Do You Accept Insurance', 'LSVT Certification Date',
              'LSVT Certification Renewal Date']

# create the first row for the .csv file
clinicians = np.array([attributes])

driver = webdriver.Chrome()

# open the browser to the given link
driver.get('https://www.lsvtglobal.com/clinicians')

# Choose the 'LSVT BIG Physical Therapists or Occupational Therapists' option
driver.find_element_by_xpath("//input[@type='radio' and @value='big']").click()
# Choose the first option for all clinicians
driver.find_element_by_xpath("//*[@id='clinician_search_country']/option[1]").click()
# Agree to Terms and Conditions
driver.find_element_by_xpath("//*[@id='clinician_terms_checkbox']").click()
# Submit query
driver.find_element_by_xpath("//*[@id='uniform-undefined']//span//input[@type='submit' and @value='Search']").click()

time.sleep(5)

# lazy-load all clinicians (8641)
element = driver.find_element_by_id("advanced_search_wrap")
driver.execute_script("arguments[0].scrollIntoView();", element)
time.sleep(500)

# Selenium hands the page source to Beautiful Soup
all_soup = BeautifulSoup(driver.page_source, 'lxml')

# collect all the clinician links (8641)
clinician_links = []
for clinician_link in all_soup.find_all('li', class_=['one', 'two', 'three']):
    clinician_links.append(clinician_link.h2.a['href'])
print('Number of Clinicians: ', len(clinician_links))

# scrape info about each clinician
for link in clinician_links:
    # load the clinician's page
    driver.get(link)

    # create BeautifulSoup object for info scraping
    single_soup = BeautifulSoup(driver.page_source, 'lxml')

    # initialize an empty array for a clinician's information
    clinician = np.array([])

    # insert clinician's link into the clinician's array
    clinician = insert_value(clinician, link)

    # get the clinician's image url and insert it into the clinician's array
    image_url = single_soup.find('img', class_ = 'flt-right small')
    if image_url != None:
        image_url = image_url['src']
    clinician = insert_value(clinician, image_url)

    # get the clinician's category and insert it into the clinician's array
    category = single_soup.find('div', class_='cms-main')
    if category != None:
        category = category.p.text
    clinician = insert_value(clinician, category)

    # for each attribute in the list of attributes, collect the information
    # corresponding to the attribute
    for attribute in attributes[3:]:
        pattern = re.compile('(?<=%s</th><td>)(.*?)(?=</td>)'%attribute)
        if attribute == "Website":
            pattern = re.compile('(?<=Website</th><td><a href=")(.*?)(?=" target)')
        elif attribute == "Alternate Office Website":
            pattern = re.compile('(?<=Office Website</th><td><a href=")(.*?)(?=" target)')
        match = pattern.search(str(single_soup))
        if match:
            value = match.group()
        else:
            value = None
        clinician = insert_value(clinician, value)

    clinicians = np.vstack((clinicians, clinician))

# close the browser
driver.quit()

# open a .csv file
outfile = open('LSVT_BIG.csv','w', newline='')
writer = csv.writer(outfile)

# insert rows per clinician
for clinician in clinicians:
    writer.writerow(clinician)

# close the .csv file
outfile.close()

print(datetime.now() - start_time)
print("DONE")