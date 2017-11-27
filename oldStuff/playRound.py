#! /bin/bash

### ^ 'shebang' for running with bash ("./getGrades_DTU.py" instead of "python3 getGrades_DTU.py") ^ ###

'''
Getting familiar with pymongo..
'''

import json, time, re
import datetime
from pymongo import MongoClient
import pymongo
import pprint
#adming and pass
MdbURI = "mongodb://admin:datbat333@localhost:27017/tracking?authSource=admin"
# setting a client
client = MongoClient(MdbURI)
# starting database
db = client['test-database']
# restarting the collection...
db.posts.drop()
# creating a collection
posts = db['posts']

# wiping the database clean first..
client.drop_database('test-database')

# first document to insert
post = {"author": "Mike",
    "text": "My first blog post!",
    "tags": ["mongodb", "python", "pymongo"],
    "date": datetime.datetime.utcnow()}
# inserting one document
post_id = posts.insert_one(post).inserted_id

# finding with the find_one() command
print ("printing the first match with 'find_one()'' command in the 'posts':")
pprint.pprint(posts.find_one())
print ("we can find the first post from mike in 'posts':")
pprint.pprint(posts.find_one({"author": "Mike"}))
print ("but none from elliot:")
pprint.pprint(posts.find_one({"author": "elliot"}))
print ("or locate from the post_id:")
pprint.pprint(posts.find_one({"_id": post_id}))

# inserting multiple documents
new_posts = [{"author": "Mike", # first
    "text": "Another post!",
    "tags": ["bulk", "insert"],
    "date": datetime.datetime(2009, 11, 12, 11, 14)}, # second
    {"author": "Eliot",
    "title": "MongoDB is fun",
    "text": "and pretty easy too!",
    "date": datetime.datetime(2009, 11, 10, 10, 45)}]

result = posts.insert_many(new_posts)
print ("the ids of the inserted new_posts - there is two now, not one:")
print (result.inserted_ids)

# finding more than one document with loop - here all..:
print ("finding all documents with find() command")
for post in posts.find():
    pprint.pprint(post)
print ("total number of posts:")
print (posts.count())

# finding more than one document with loop - here all from mike..:
print ("finding all documents from mike with find() command")
for post in posts.find({"author": "Mike"}):
    pprint.pprint(post)
print ("total number of posts from Mike:")
print (posts.count({"author": "Mike"}))

# advanced queries
# say we have a date 'd',  older posts are of interest
d = datetime.datetime(2009, 11, 12, 12)
print ("Posts older than a date 'd', sorted by author:")
for post in posts.find({"date": {"$lt": d}}).sort("author"):
    pprint.pprint(post)

#something with userids...
print ("We have created a user_id, so now there is two different indexes:")
asdfasdfasdf = db.profiles.create_index([('user_id', pymongo.ASCENDING)],unique=True)
print (sorted(list(db.profiles.index_information())))

# setting up userprofilse
user_profiles = [
    {'user_id': 211, 'name': 'Luke'},
    {'user_id': 212, 'name': 'Ziltoid'}]
db.profiles.insert_many(user_profiles)

new_profile = {'user_id': 213, 'name': 'Drew'}
duplicate_profile = {'user_id': 212, 'name': 'Tommy'}
db.profiles.insert_one(new_profile)  # This is fine.
# db.profiles.insert_one(duplicate_profile) # this gives error

print ("Succes!! Reached end of document..")
