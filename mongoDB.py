# -*- coding: utf-8 -*-

#for pushing documnets into MongoDb Atlas cluster


import pymongo
from pymongo import MongoClient
#!pip install pymongo

#!pip install dnspython
#cluster movie
#db movie-db
#collection teluguImdb

#https://cloud.mongodb.com/v2/607c99e3d1949f7c3f143127#metrics/replicaSet/607ce0c08d32fa64397040a3/explorer/movie-db/teluguImdb/find
client = pymongo.MongoClient("mongodb+srv://admin:root@movie-cluster.hvw8d.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
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
