# -*- coding: utf-8 -*-

from flask import request
import requests
from bs4 import BeautifulSoup
import re,os
import uuid
from threading import Thread



def getVideos(soup) :
#  url = "https://www.imdb.com/title/"+ImdbId+"/videogallery?sort=date&sortDir=asc"
#  data= {}
#  data['ImdbId']=ImdbId
#  r = requests.get(url=url)
#  soup = BeautifulSoup(r.text, 'html.parser')

  videolist = soup.find('div',{"class" : "search-results"})
  
  Video_anchors_list=[]
  if videolist!= None :
      Video_anchors_list=videolist.findAll('a')
  print(len(Video_anchors_list))

  video_urls = []
  links=[]
  for a in Video_anchors_list :
    vid = { }
    links.append(a['href'].split('/')[2])
    vid['url']=a['href'].split('/')[2]
    video_urls.append(vid)
  print("links:",set(links))  
  return list(set(links))

    

def start(soup,ImdbId,limit=30) :
    video_list = getVideos(soup)
    
    video_list=video_list[0:limit]
    video_ids = video_list
    
    threads = []
    for video_id in video_ids :
        process = Thread(target=getmp4links, args=[video_id,ImdbId])
        process.start()
        threads.append(process)         
    for process in threads:
         process.join()
    
    

def getmp4links(video_id,ImdbId) :
    video_url= "https://www.imdb.com/video/"+video_id
#    print(video_url)
    print(video_url)
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
            z=x.split("url")[4]## 3# low defination
        except :
            try :
                z=x.split("url")[3]  # stanard defination
            except :
                z=x.split("url")[2] # hd 

            
        link = z.split('\"')[2][:-1]
        break

#    print(link)
    download(link,video_id,ImdbId)
#    return link

#getmp4links(video_id="vi2922945817")

def download(video_url,video_id,ImdbId) :
    r = requests.get(video_url)
    unique_filename = str(uuid.uuid4())
    print("downloading  "+ unique_filename)

    with open('videos/'+ImdbId+'_'+video_id+'.mp4', 'wb') as f:
        f.write(r.content)
    print("downloaded"+ video_id)





def startDownload(ImdbId,limit) :
    imdb_domain = "https://www.imdb.com" 
    url = "https://www.imdb.com/title/"+ImdbId+"/videogallery"
    next_page=url
    os.makedirs("videos", exist_ok=True)

    while next_page!="" :
            print(next_page)
            r = requests.get(url=next_page)
            soup = BeautifulSoup(r.text, 'html.parser')
            try: 
                
                  paginatinon_span= soup.findAll('span',{'class': 'pagination'})
                  a= paginatinon_span[1].findAll('a')[-1]
                  next_page =imdb_domain + a['href']
                  if "Next" not in a.string :
                      next_page=""
    
#                  print(next_page)
            except Exception as e:
                print(e,"---next-page")
                next_page=""
                
            try :  
                process_page = Thread(target=start, args=[soup,ImdbId,limit])
                process_page.start()
                
            except Exception as e: 
                print(e,"start-error")
                break













ImdbId="tt0944947"
startDownload(ImdbId="tt0944947",limit=100)
#video_url =scrapeVidPage("vi3877612057")
#download(video_url)













