#! /usr/bin/python3

### ^ 'shebang' for running with bash ("./getGrades_DTU.py" instead of "python3 getGrades_DTU.py") ^ ###

'''
What?
	Get grades from nosql database with courses
Result?
	Big Dollar Data Cloud ftw
'''

##################################################################################################################
################################################ LIBRARIES #######################################################
##################################################################################################################

import json, time, re
from datetime import datetime
import pymongo
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pprint
##################################################################################################################
################################################ UTILITIES #######################################################
##################################################################################################################

### Initialize database-connection:
client = MongoClient("mongodb://admin:datbat333@localhost:27017/tracking?authSource=admin")
# database
db = client['DTU']
# existing collection with courses
courseColl = db['course_info']
# the new collection with grades
gradeColl = db['grades']

# baseurl of grade sites..
#example: http://karakterer.dtu.dk/Histogram/1/62612/Winter-2017
baseUrlGrade = 'http://karakterer.dtu.dk/Histogram/1/'
# baseurl of list of semesters available site
#example: http://kurser.dtu.dk/course/02162/info
baseUrlSem = 'http://kurser.dtu.dk/course/'
##################################################################################################################
################################################ MAIN-METHODS #####################################################
##################################################################################################################


##################################################################################################################
################################################ SUB-METHODS #####################################################
##################################################################################################################
### Method: getting available semesters to crawl...
def getSemesters(course):
    url = baseUrlSem+course['course_id']+'/info'
    print('\n', url, '\n')
    xpath = "//*[@class='row']//*[@class='col-md-6']//*[@class='box']/div"
    driver.get(url)
    time.sleep(2)
    # the url contains two types of hrefs pointing to evaluations and grades of
    # course in different semesters
    value = []
    hrefGrades = []
    hrefEval = []
    #we also want to store the acutal semesters of grades and evaluations..
    semesterGradeList = []
    semesterEvalList = []
    # finding the stuff...
    value = driver.find_elements_by_xpath(xpath)
    for elem in value:
        try:
            elem = elem.find_element_by_css_selector('a').get_attribute('href')
            if "karakterer" in elem:
                print("Found grade href:", elem)
                hrefGrades.append(elem)
                semesterGradeList.append(elem.rsplit('/', 1)[-1])
            elif "evaluering" in elem:
                print("Found evaluation href:", elem)
                hrefEval.append(elem)
                semesterEvalList.append(elem.rsplit('/', 1)[-1])
            else:
                print("Found an href but neither an evaluation or a grade?")
        except:
            print('Couldnt find any href in element all!')
            #print('Couldnt find any href at all! Found instead:', elem.text)
    #print('\nLength of value =',len(value) )
    #print('Length of hrefGrades =',len(hrefGrades) )
    #print('Length of semesterList =',len(semesterList) )
    #print('Length of hrefEval =',len(hrefEval) )
    #print(semesterList)
    return(hrefEval, semesterEvalList, hrefGrades, semesterGradeList)

    
### Method: Initializiation method for a webdriver-object
def init_driver():
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver")
    driver.wait = WebDriverWait(driver, 2)
    driver.maximize_window()
    return(driver)

### Method: Initialization-point of the script. Put main methods here.
if __name__ == "__main__":
    driver = init_driver()
    course = list(courseColl.find())[0:2]
    for elem in course:
        getSemesters(elem)
    time.sleep(1)
    driver.close()

# http://selenium-python.readthedocs.io/locating-elements.html
print ("Reached end of doc!!")
