# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json
from threading import Thread
import pandas as pd
from glob import glob
import time


def getMovieDetails(imdbID):
    data = {}
    
    movie_url = "https://www.imdb.com/title/"+imdbID
    r = requests.get(url=movie_url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')
    jsonData = soup.find('script',{"type":"application/ld+json"})
    #print(jsonData.string)
    Moredata=[]
    jsonSourceObj=json.loads(jsonData.string)
    Moredata.append(jsonSourceObj)
    data["expanded"]=Moredata

    

    #imdbId
    data["imdbID"] = imdbID

    #page title
    title = soup.find('title')
    data["title"] = title.string

    


    #title Year


    #RunTime
#    data["RunTime"]=""
    data["Minutes"]=""
#    runTime = soup.find("time")
#    if runTime!= None :
#      data["RunTime"]=runTime.string.strip()
#      data["Minutes"]=runTime['datetime']
    
    try :
        data["Minutes"]=jsonSourceObj['duration']
    except :
        data["Minutes"]=""



    # rating
    data["ratingValue"]=""
#    ratingValue = soup.find("span", {"itemprop" : "ratingValue"})
#    if ratingValue!= None :
#        data["ratingValue"] = ratingValue.string
    try : 
         data["ratingValue"]= jsonSourceObj['aggregateRating']['ratingValue']
    except :
        data["ratingValue"]=""

    
    

    # no of rating given
    data["ratingCount"] =""
#    ratingCount = soup.find("span", {"itemprop" : "ratingCount"})
#    if ratingCount!= None  :
#        data["ratingCount"] = ratingCount.string
    
    try : 
         data["ratingCount"]= jsonSourceObj['aggregateRating']['ratingCount']
    except :
        data["ratingCount"]=""
    

    # name
#    data["name"]=""
#    titleName = soup.find("div",{'class':'titleBar'}).find("h1")
#    if titleName!= None :
#        data["name"] = titleName.contents[0].replace(u'\xa0', u'')

    # additional details
#    subtext = soup.find("div",{'class':'subtext'})
#    data["subtext"] = ""
#    for i in subtext.contents:
#        data["subtext"] += i.string.strip()

    # summary
#    summary_text = soup.find("div",{'class':'summary_text'})
   # print(summary_text)
#    if summary_text!=None and summary_text.string != None :
#      data["summary_text"] = summary_text.string.strip()
#    else :
#      data["summary_text"]=""
    try : 
         data["summary_text"]= jsonSourceObj['description']
    except :
        data["summary_text"]=""    
    
    
    
#    credit_summary_item = soup.find_all("div",{'class':'credit_summary_item'})
#    data["credits"] = {}
#    for i in credit_summary_item:
#        item = i.find("h4")
#        names = i.find_all("a")
#        data["credits"][item.string] = []
#        for i in names:
#            data["credits"][item.string].append({
#                "link": i["href"],
#                "name": i.string
#            })

    try: 
        data['keywords']=jsonSourceObj['keywords']
    
    except :
         data['keywords']=""
    
    
    return data

#getMovieDetails('tt2794386')


def getCrewData(imdbID):

    url = "https://www.imdb.com/title/"+imdbID+"/fullcredits/"
    crew_data = {
        "imdbID" : imdbID,
        "crew": []
    }
    r = requests.get(url=url)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    #page title
    title = soup.find('title')
    crew_data["title"]=""
    if title!=None :
        crew_data["title"] = title.string
    cast_list = soup.find("table", {"class" : "cast_list"})
    trows=[]
    if cast_list!=None :
        trows = cast_list.find_all('tr')

    for tr in trows:
        td = tr.find_all('td')
        if len(td)==4:
            row = [i.text for i in td]
            crew_data["crew"].append({
                "name":re.sub("[^a-zA-Z' ]+", '', row[1]).strip(),
                "character":re.sub("[^a-zA-Z' ]+", '', row[3]).strip()
            })
    return crew_data
#getCrewData('tt9890028')

def getImages(ImdbId) :
  url = "https://www.imdb.com/title/"+ImdbId+"/mediaindex"
  data= {}
  data['ImdbId']=ImdbId
  image_urls = []
  r = requests.get(url=url)
  soup = BeautifulSoup(r.text, 'html.parser')
  img =soup.find("img",{'class':'poster'})
  src=""
  if img!=None :
      src = img.get('src')
  data["poster_url"]= src
  
  imagelist = soup.find('div',{"class" : "media_index_thumb_list"})
  
  Image_anchors_list=[]
  if imagelist!= None :
      Image_anchors_list=imagelist.findAll('a')

  
  for a in Image_anchors_list :
    img = { }
    img["image_title"]=""
    if a.has_attr('title'):
        img["image_title"] = a['title']
    img['url']=""
    #print(a['title'])
    imageTagList = a.findAll('img')
    if len(imageTagList) > 0 :
      img['url'] = imageTagList[0]['src']
    image_urls.append(img)

  data['other_images'] = image_urls 

    
  return data

#getImages('tt1579694')

def getVideos(ImdbId) :
  url = "https://www.imdb.com/title/"+ImdbId+"/mediaindex"
  data= {}
  data['ImdbId']=ImdbId
  video_urls = []
  r = requests.get(url=url)
#  print(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  videoList =soup.find("div",{'class':'mediastrip_big'})
#  print(videoList)
  VideoAnchorList=[]
  if videoList != None :
      VideoAnchorList = videoList.findAll('a')
  for a in VideoAnchorList :
#    print(a)
    video_urls.append(a['href'])
  data['video_urls']=video_urls
#  print(data)
  return data

#getVideos('tt12735856')

def scrapIMDB(ImdbId) :
    print(ImdbId+"started")

    data = {}
    data['imdbId']=ImdbId
    data['_id']=ImdbId

    data['videos'] = getVideos(ImdbId)
    data['images'] = getImages(ImdbId)
    data['info']    = getMovieDetails(ImdbId)
    data['crew_data'] =  getCrewData(ImdbId)
    data['name']=""

    try:
        if 'name' in data['info']['expanded'][0] :
            data['name']=data['info']['expanded'][0]['name']
    except :
        pass
    
    with open('movies/'+ImdbId +'.json', 'w') as json_file:
        json.dump(data, json_file)    
    print(ImdbId+"ended")


def start_with_threads(f_name) :
    ids =pd.read_csv(f_name).iloc[:,0]
    ids = list(ids)
    listId=ids
    threads = []
    for i in listId :
        process = Thread(target=scrapIMDB, args=[i])
        process.start()
        time.sleep(2.5)##ip gets blocked
        threads.append(process)
    for process in threads:
        process.join()
    




for f_name in glob('test_ids/*.csv'):
    print(f_name)
    start_with_threads(f_name)









