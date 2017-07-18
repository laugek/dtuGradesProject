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
##################################################################################################################
################################################ UTILITIES #######################################################
##################################################################################################################

### Initialize database-connection:
client = MongoClient("mongodb://admin:datbat333@localhost:27017/tracking?authSource=admin")
# database
db = client['DTU']
# existing collection with courses
courseColl = db['course_info']
# for testing: dropping the database..
db.grades.drop()
# the new collection with grades
gradeColl = db['grades']

# baseurl of grade sites..
#example: http://karakterer.dtu.dk/Histogram/1/62612/Winter-2017
baseUrlGrade = 'http://karakterer.dtu.dk/Histogram/1/'
# baseurl of list of semesters available site
#example: http://kurser.dtu.dk/course/02162/info
baseUrlSem = 'http://kurser.dtu.dk/course/'

### Method: Defines the database structure using a python-dictionary, stamps with timestamp
def dbInsert(mongoCollection, course, url, semester, listGrades,
listStudents,tilmeldte,fremmoedte,eksgns):
    json = {"course_id"    : course,
            "course_url"   : url,
            "semester"     : semester,
            "list_grades"  : listGrades,
            "list_students": listStudents,
            "tilmeldte"    : tilmeldte,
            "fremmoedte"   : fremmoedte,
            "eksgns"       : eksgns,
            "timestamp"    : datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    print("Inserted in to database:")
    print(json)
    print("")
    mongoCollection.insert_one(json).inserted_id

##################################################################################################################
################################################ MAIN-METHODS #####################################################
##################################################################################################################
def masta(courseCollection):
    for course in courseCollection:
        [hrefEval, semesterEvalList, hrefGrades, semesterGradeList] = findSemesters(course)
        idx = 0
        for url in hrefGrades:
            if len(hrefGrades) == 0: # if no urs at all then...
                print("Everything is empty..")
                listGrades = ["nan"]
                listStudents = ["nan"]
                tilmeldte = ["nan"]
                fremmoedte = ["nan"]
                eksgns = ["nan"]
                url = ["nan"]
                semester = ["nan"]
            else: # there is a number of urls...
                semester = semesterGradeList[idx]
                print("semester", semester)
                driver.get(url)
                time.sleep(2)
                [listGrades, listStudents] = findGrades(course, url)
                try:
                    [tilmeldteTemp] = findTilmeldte()
                    tilmeldte = tilmeldteTemp.text
                except:
                    tilmeldte = ["nan"]
                try:
                    [fremmoedteTemp] = findFremmoedte()
                    fremmoedte = fremmoedteTemp.text
                except:
                    fremmoedte = ["nan"]
                try:
                    [eksgnsTemp] = findEksgns()
                    eksgns = eksgnsTemp.text
                    eksgns = eksgns[0:3]
                except:
                    eksgns = ["nan"]
            print("")
            print("tilmeldte", tilmeldte)
            print("fremmoedte", fremmoedte)
            print("eksgns", eksgns)
            print("")
            dbInsert(gradeColl, course['course_id'], url, semester
            , listGrades, listStudents, tilmeldte,fremmoedte, eksgns)
            idx = idx+1
            # call a function that saves this with the semesterGradeList
        #for sem in hrefEval:
            # some function..

##################################################################################################################
################################################ SUB-METHODS #####################################################
##################################################################################################################

### Method: getting available semesters to crawl...
def findSemesters(course):
    url = baseUrlSem+course['course_id']+'/info'
    print("\n", url, "\n")
    driver.get(url)
    time.sleep(2)
    value = []
    hrefGrades = []
    hrefEval = []
    #we also want to store the acutal semesters of grades and evaluations..
    semesterGradeList = []
    semesterEvalList = []
    xpath = "//*[@class='row']//*[@class='col-md-6']//*[@class='box']/div"
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
            print("")
            #print('Couldnt find any href in element!')
            #print('Couldnt find any href at all! Found instead:', elem.text)
    return(hrefEval, semesterEvalList, hrefGrades, semesterGradeList)

### Method: getting the grades from the url...
def findGrades(course, url):
    # for storing the web elements..
    valueGrades = []
    valueStudents = []
    # xpaths
    xpathGrade = "//*[@style='text-align: center']/preceding-sibling::*"
    xpathStudents = "//*[@style='text-align: center']"
    #url to visit for all the semesters.
    # for storign the actual text
    listGrades = []
    listStudents = []
    driver.get(url)
    time.sleep(2)
    valueGrades = driver.find_elements_by_xpath(xpathGrade)
    valueStudents = driver.find_elements_by_xpath(xpathStudents)
    if len(valueGrades) == len(valueStudents):
        if len(valueGrades) == 0:
            print("No grades for this course.")
        else:
            for elem in valueGrades:
                listGrades.append(elem.text)
            for elem in valueStudents:
                listStudents.append(elem.text)
            if "12" and "13" in listGrades:
                print("OBS: there is both 12- and 13-scale grading, but 13 is omitted.")
                idx13 = listGrades.index("13")
                listGrades = listGrades[0:idx13]
                listStudents = listStudents[0:idx13]
            elif "12" in listGrades:
                print("This is 12-grade scaling")
            elif "13" in listGrades:
                print("This is 13-grade scaling")
            else:
                print("neither 13 or 12 scale??")
    else:
        print("Err: lengts of grades and studens are unequal?")
    print(listGrades)
    print(listStudents)
    return(listGrades, listStudents)

### Method: getting other basic info from the url...
def findTilmeldte():
    xpath = ".//*[contains(text(), 'Antal tilmeldte')]/following-sibling::*"
    value = driver.find_elements_by_xpath(xpath)
    return(value)

def findFremmoedte():
    xpath = ".//*[contains(text(), 'Fremm')]/following-sibling::*"
    value = driver.find_elements_by_xpath(xpath)
    return(value)

def findEksgns():
    xpath = ".//*[contains(text(), 'Eksamensgennemsnit')]/following-sibling::*"
    value = driver.find_elements_by_xpath(xpath)
    return(value)

##################################################################################################################
################################################ INITIALIZATION ##################################################
##################################################################################################################


### Method: Initializiation method for a webdriver-object
def init_driver():
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver")
    driver.wait = WebDriverWait(driver, 2)
    driver.maximize_window()
    return(driver)

### Method: Initialization-point of the script. Put main methods here.
if __name__ == "__main__":
    driver = init_driver()
    courseCollection = list(courseColl.find())
    masta(courseCollection)
    time.sleep(1)
    driver.close()

print(gradeColl.find_one())

# http://selenium-python.readthedocs.io/locating-elements.html
print ("\nReached end of doc!!")
