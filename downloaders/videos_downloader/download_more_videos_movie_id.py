# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from flask import request
import requests
from bs4 import BeautifulSoup
import re,os
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
    print(video_url)
    r = requests.get(url=video_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    script =soup.find("script",{'type': 'application/json'})
    json_object = json.loads(script.string)
    print(json_object["props"]["pageProps"]["videoPlaybackData"]["video"]["playbackURLs"])
    videos = json_object["props"]["pageProps"]["videoPlaybackData"]["video"]["playbackURLs"]
    # links video quality order auto,1080,720

    for video in videos[1:] :
        video_link = video["url"]
        print(video_link)  
        break
    print(video_link)
    download(ImdbId,video_id,video_link)
#    return link

#getmp4links(video_id="vi2922945817")

def download(ImdbId,video_id,video_url) :
    r = requests.get(video_url)
    print("downloading  "+ video_id)
    os.makedirs("videos", exist_ok=True)

    with open('videos/'+ImdbId+'_' + video_id+'.mp4', 'wb') as f:
        f.write(r.content)
    print("downloaded"+ video_id)

    
start(ImdbId="tt6723592",limit=40)
#tt1160419
#video_url =scrapeVidPage("vi3877612057")
#download(video_url)












