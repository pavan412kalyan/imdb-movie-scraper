# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from flask import request
import requests
from bs4 import BeautifulSoup
import re
import uuid
from threading import Thread


def getVideosFromMainPage(ImdbId) :
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


def getVideos(ImdbId) :
  url = "https://www.imdb.com/title/"+ImdbId+"/videogallery?sort=date&sortDir=asc"
  data= {}
  data['ImdbId']=ImdbId
  r = requests.get(url=url)
  soup = BeautifulSoup(r.text, 'html.parser')

  videolist = soup.find('div',{"class" : "search-results"})
  
  Video_anchors_list=[]
  if videolist!= None :
      Video_anchors_list=videolist.findAll('a')

  video_urls = []
  links=[]
  for a in Video_anchors_list :
    vid = { }
    links.append(a['href'].split('/')[2])
    vid['url']=a['href'].split('/')[2]
    video_urls.append(vid)
  
  return links

    



def start(ImdbId,limit=10) :
    video_list = getVideos(ImdbId)
    video_list=video_list[0:limit]
    video_ids = video_list
    
    threads = []
    for video_id in video_ids :
        process = Thread(target=getmp4links, args=[ImdbId,video_id])
        process.start()
        threads.append(process)         
    for process in threads:
         process.join()
    
    

def getmp4links(ImdbId,video_id) :
    video_url= "https://www.imdb.com/video/"+video_id
#    print(video_url)
    r = requests.get(url=video_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    v =soup.findAll("script",{'type': 'text/javascript'})

    #print(v[2].text)
    script=v[2]

    urls = re.findall('[a-z]+[:.].*?(?=\s)', script.text)
#    print(urls) 

    for x in urls :
      if ".mp4" in x :
        try :
            z=x.split("url")[4]## HD video
        except :
            try :
                z=x.split("url")[3]  ## SD video
            except :
                z=x.split("url")[2]  ## 480p

            
        link = z.split('\"')[2][:-1]
        break

    print(link)
    download(ImdbId,video_id,link)
#    return link

#getmp4links(video_id="vi2922945817")

def download(ImdbId,video_id,video_url) :
    r = requests.get(video_url)
    print("downloading  "+ video_id)

    with open('videos/'+ImdbId+'_' + video_id+'.mp4', 'wb') as f:
        f.write(r.content)
    print("downloaded"+ video_id)

    
start(ImdbId="tt6723592",limit=40)
#video_url =scrapeVidPage("vi3877612057")
#download(video_url)












