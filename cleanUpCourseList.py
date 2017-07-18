#! /usr/bin/python3

### ^ 'shebang' for running with bash ("./getGrades_DTU.py" instead of "python3 getGrades_DTU.py") ^ ###

'''
What?
    clean data base..
    1) remove duplicates of course_id
    2) consistent course_id (seems to appear at Manegement courses), eg:
    right) course_id = 01005
    wrong) course_id = 01005 Engineering Mathematics 1

Result?
    Big Dollar Data Cloud ftw
'''
############################################################################
# Initialize
############################################################################

import pymongo
from pymongo import DeleteOne
import json, time, re
from datetime import datetime
from pymongo import MongoClient
from pymongo import UpdateOne

client = MongoClient("mongodb://admin:datbat333@localhost:27017/tracking?authSource=admin"
)
db = client['DTU']
# source
sourceCol = db['course_info']
# target
targetCol = db['targetCol']

############################################################################
# her it happens
# since getGrades.py only uses the course_id to finde grades, this is the
# only parameter used to determine a duplicate...
############################################################################
# go through all unique ids in list
for uniqueId in sourceCol.distinct("course_id"):
    #insert in to new collection
    targetCol.insert(sourceCol.find_one({"course_id":uniqueId}))
    # remove stuff after first space if any is present
    cleanedId = uniqueId.split(" ",1)[0]
    if cleanedId != uniqueId:
        db.targetCol.update_one({"course_id": uniqueId},{'$set': {'course_id': cleanedId}}, upsert=False)

############################################################################
# summation + checking
############################################################################

print("\n number of docs in sourceCol.")
nbefore = sourceCol.count()
print(nbefore)

print("\n number of docs in targetCol..")
nafter = targetCol.count()
print(nafter)

print("\n number of unique course_ids in sourceCol.")
noUnique= len(sourceCol.distinct("course_id"))
print(noUnique)

nremove = nbefore - nafter
print("\n No of documents not included in the targetCol..")
print(nremove)

print("\nOK... end of doc\n")
