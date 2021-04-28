# -*- coding: utf-8 -*-

import pandas as pd

import numpy as np
from pandas import DataFrame
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
collection = db["indiaImdb"]



##get all the ids in your database
process=[]
for d in collection.find({}) :
    process.append(d['_id'])
    

### get all the ids for new update from your csv file
ids =pd.read_csv('part1.csv').iloc[:,0]
len(set(ids))

idList=[]
for id in ids :
  idList.append(id.split('/')[4])


###finding the list for updating movies
main_list = np.setdiff1d(idList,process)
your_list=list(main_list)  


##pending.csv creates the ids that needed to pushed on mongo db
df = DataFrame (your_list)  
df.to_csv('pending.csv',index=False)

##########################
#code for pulling data from mongo
#collection_indiaImdb = db["indiaImdb"]
#collection_teluguImdb = db["teluguImdb"]
#
#data_many=[]
#
#for d in collection_indiaImdb.find({}) :
#    data_many.append(d)
#    
#for d in collection_teluguImdb.find({}) :
#    data_many.append(d)
#    
    
#        
#
#
#collection_all_indian= db["all-indian"]
#collection_all_indian.insert_many(data_many)




