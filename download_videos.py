# -*- coding: utf-8 -*-
from flask import request
import requests
from bs4 import BeautifulSoup
import re
import uuid
from threading import Thread





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





def scrapeVidPage(video_id) :
    video_url= "https://www.imdb.com/video/"+video_id
    print(video_url)
    r = requests.get(url=video_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    v =soup.findAll("script",{'type': 'text/javascript'})
    print(len(v))

    

scrapeVidPage("vi589675545")




def getvideourls(ImdbId):
    vid = getVideos(ImdbId)
    for  v in  vid['video_urls'] :
        print(v)
    threads = []
    process = Thread(target=download, args=[img_url])
    process.start()
    threads.append(process)




ImdbId="tt0944947"
vid = getvideourls(ImdbId)









###############################
#r = requests.get("https://cdn-a.amazon-adsystem.com/video/6feecfdc-9d90-4ae7-821c-bd1fd74855d4/MP4-10000kbs-29.97fps-48khz-320kbs-1080p.mp4")
#unique_filename = str(uuid.uuid4())
#with open('images/'+unique_filename+'.mp4', 'wb') as f:
#    f.write(r.content)
