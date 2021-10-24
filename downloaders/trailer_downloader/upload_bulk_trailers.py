# -*- coding: utf-8 -*-
#upload_video_to_youtube(videopath,imagepath,title,description,tags_list,privacyStatus)
from upload_to_youtube import upload_video_to_youtube
import json,pandas as pd
import os.path


def start(file_ids) :
    ids =pd.read_csv(file_ids).iloc[:,0]
    ids = list(ids)
    for ImdbId in ids:
        load(ImdbId)
            
def load(ImdbId) : 
    
    if os.path.exists(f'trailers/{ImdbId}/{ImdbId}.mp4') == False  :
        print(f"Video for {ImdbId} doesnot exist")
        return
    if os.path.exists(f'trailers/{ImdbId}/{ImdbId}.json') == False  :
        print(f"Details for {ImdbId} doesnot exist")
        return 
    
    f = open(f'trailers/{ImdbId}/{ImdbId}.json') 
    data = json.load(f)
    
    title = data['title']
    movie_description = data['description']
    
    year=''
    if 'datePublished' in data :
        year = data['datePublished']

    directors = []
    if 'director' in data :
        for d in data['director'] :
            directors.append(d['name'])
    actors = []
    if 'actor' in data :
        for a in data['actor'] :
            actors.append(a['name'])        
    
    video_title = title
    if len(year) > 0 :
        video_title  = video_title + '('+ year.split('-')[0] + ')'  + '|Trailer'
    if len(actors) > 0 :
        video_title  = video_title + '|'+ actors[0]
    if len(directors) > 0 :
        video_title  = video_title + '|'+ directors[0]

    video_description = movie_description + "\n"
    if 'actor' in data :
        video_description = video_description + "ACTORS:"
        for a in data['actor'] :
            video_description= video_description + a['name'] + "," 

    if 'director' in data :
        video_description = video_description + " \n DIRECTOR(S):"
        for a in data['director'] :
            video_description= video_description + a['name'] + "," 
  
    tags_list = actors + directors + [title]
    f.close()
    print(video_title,video_description,ImdbId) 
    try :      
        upload_video_to_youtube(videopath=f'trailers/{ImdbId}/{ImdbId}.mp4',imagepath=f'trailers/{ImdbId}/{ImdbId}.JPG',title=video_title,description=video_description,tags_list=tags_list,privacyStatus='Public')
    except  Exception as e :
        print(e)
    
    
start(file_ids='imdbids.csv')              