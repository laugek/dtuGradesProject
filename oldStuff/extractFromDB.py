#! /bin/bash

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
import pandas as pd 
from pandas.io.json import json_normalize

### Initialize database-connection:
	### This requires, that you have pymongo installed alongside a running instance of MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['DTU']
collection = db['course_info']

data = list(collection.find())
data = json_normalize(data)

path = "~/Downloads/DTU_export.csv"

data.to_csv(path, sep = ";", encoding = "utf-8")
