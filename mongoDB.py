# -*- coding: utf-8 -*-

#for pushing documnets into MongoDb Atlas cluster if files are availble in your local folder


import pymongo
from pymongo import MongoClient
#!pip install pymongo

#!pip install dnspython
#cluster movie
#db movie-db
#collection teluguImdb


client = pymongo.MongoClient("")
db = client["movie-db"]
collection = db["teluguImdb"]





from glob import glob
import json
moviedata=[]

files =glob('FinalDataset/*.json')
count=0
for f_name in files:
    count=count+1
    print(count)
    print(f_name)
    with open(f_name) as f:
        data = json.load(f)
        print("+++")
        fileName=data['imdbId']
        data["_id"]=fileName
        moviedata.append(data)
        try :  
            collection.insert_one(data)
        except :
            print("--")
