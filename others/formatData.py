# -*- coding: utf-8 -*-

##this is to format your dataset that are already scraped which 
# where placed in dataset folder and the final files are placed in finaldataset folder
from glob import glob

import json

moviedata=[]
count=0
for f_name in glob('dataset/*.json'):
    count=count+1
    print(count)
    print(f_name)
    with open(f_name) as f:
        data = json.load(f)
        print("+++")
        fileName=data['imdbId']
        data['name']=""
        if 'name' in data['info']['expanded'][0] :
            data['name']=data['info']['expanded'][0]['name']
        data['genre']=[]
        genre=[]
        if 'genre' in data['info']['expanded'][0] :
            if type(data['info']['expanded'][0]['genre']) is list :
                for g in data['info']['expanded'][0]['genre'] :
                    genre.append(g)
            else :
                genre.append(data['info']['expanded'][0]['genre'] )           
        data['genre']=genre 
        moviedata.append(data)
#        print(data)
        with open('FinalDataset/'+fileName +'.json', 'w') as json_file:
            json.dump(data, json_file)
with open('teluguImdb.json', 'w') as json_file :
    json.dump(moviedata, json_file)            