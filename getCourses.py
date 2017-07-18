#! /usr/bin/python3

### ^ 'shebang' for running with bash ("./getGrades_DTU.py" instead of "python3 getGrades_DTU.py") ^ ###

'''
What?
	Get dat data

Why are we doing it this way?
    1) Consistency
    2) Error-avoidance
    3) Readability
    4) Replication

Result?
	Big Dollar Data Cloud ftw
'''

##################################################################################################################
################################################ LIBRARIES #######################################################
##################################################################################################################

import json, time, re
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

##################################################################################################################
################################################ UTILITIES #######################################################
##################################################################################################################

### List of entry-point URL's
# note: think two are needed,
# english = mainly msc
# danish = bsc and beng

urlList = ["http://kurser.dtu.dk/search?CourseCode=&SearchKeyword=&SchedulePlacement=&Department=&CourseType=&TeachingLanguage=da-DK&Volume=",
            "http://kurser.dtu.dk/search?CourseCode=&SearchKeyword=&SchedulePlacement=&Department=&CourseType=&TeachingLanguage=en-GB&Volume="]

### Placeholder list - fill this with URL's
hrefs = []

### Initialize database-connection:
	### This requires, that you have pymongo installed alongside a running instance of MongoDB
client = MongoClient("mongodb://admin:datbat333@localhost:27017/tracking?authSource=admin"
)
db = client['DTU']
collection = db['course_info']

### Method: Defines the database structure using a python-dictionary, stamps with timestamp
def dbInsert(mongoCollection, name, url, years, ects, cid):
    json = {"course_name"  : name,
            "course_url"   : url,
            "course_years" : years,
            "course_ects"  : ects,
            "course_id"    : cid,
            "timestamp"    : datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    print(json)
    mongoCollection.insert_one(json).inserted_id

##################################################################################################################
################################################ MAIN-METHODS ####################################################
##################################################################################################################

### Method: Main method for executing all sub-methods trough open connection to driver object
### Input: ({driver: a webdriver object defined by init_driver}, {urls: a list of URL's to traverse})
def getContents(driver, urls, mongoCollection):
	for url in urls:
		driver.get(url)
		time.sleep(5)
		getHrefs(driver, hrefs)
		for href in hrefs:
			driver.get(href)
			xpath = "//*[@id='pagecontents']"
			courseUrl = href
			pageContents = driver.find_element_by_xpath(xpath)
			courseName = getCourseName(pageContents)
			courseYears = getCourseYears(pageContents)
			ECTS = getECTS(pageContents)
			courseID = retrieveCourseID(courseName)
			dbInsert(mongoCollection, courseName, courseUrl, courseYears, ECTS, courseID)

			# print("Course Name: " + courseName)
			# print("Course Year. " + courseYears)
			# print("ECTS: " + ECTS)
			# print("Course ID: " + str(courseID) + " " + str(type(courseID)))

##################################################################################################################
################################################ SUB-METHODS #####################################################
##################################################################################################################

### Method: Submethod for retrieving course HREF's(URL's) from each element in 'urlList' - append these to 'hrefs'
def getHrefs(element, hrefs):
	xpath = "//*[@class='panel panel-default']//*[@class='table']/tbody/tr/td/a"
	values = element.find_elements_by_xpath(xpath)[1:]
	value = []
	for elem in values:
		hrefs.append(elem.get_attribute('href'))

### Method: Submethod for retrieving the course name from an HREF
def getCourseName(element):
	xpath = ".//*[@class='col-xs-8']"
	value = element.find_element_by_xpath(xpath).text
	return(value)

### Method: Submethod for retrieving the course-years, e.g. 2016/2017 from an HREF
def getCourseYears(element):
	xpath = ".//*[@class='col-xs-4']"
	value = element.find_element_by_xpath(xpath).text
	return(value)

### Method: Submethod for retrieving the awarded number of ECTS-points from an HREF
def getECTS(element):
	xpath = ".//*[contains(text(), 'ECTS')]/parent::*/following-sibling::*"
	value = element.find_element_by_xpath(xpath).text
	return(value)

### Method: Submethod for decoding the 'courseName' into a string containing the course-ID
def retrieveCourseID(string):
	regex = re.compile("^.*[0-9]{5}")
	try:
		value = regex.search(string).group()
	except:
		value = ahstring
	return(value)

##################################################################################################################
################################################ INITIALIZATION ##################################################
##################################################################################################################

### Method: Initializiation method for a webdriver-object
def init_driver():
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver")
    driver.wait = WebDriverWait(driver, 10)
    driver.maximize_window()
    return(driver)

### Method: Initialization-point of the script. Put main methods here.
if __name__ == "__main__":
	driver = init_driver()
	getContents(driver, urlList, collection)
	driver.close()
