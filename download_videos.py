# -*- coding: utf-8 -*-
from flask import request
import requests
from bs4 import BeautifulSoup
import re
import uuid
from threading import Thread
from urllib.request import urlopen



def download(video_url) :
    file_size_str = requests.head(video_url).headers['Content-Length']
    file_size = str(float(file_size_str)/1024/1024) 
    print(file_size + " MB")
    r = requests.get(video_url)
    ru = urlopen(video_url)

    unique_filename = str(uuid.uuid4())
    f = open("videos/"+unique_filename+".mp4", 'wb')
    
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = ru.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        s= file_size_dl/1024/1024
        if s%5 == 0 :
            print(float(file_size_dl/1024/1024),"kb Downloaded")
        f.write(buffer)
#        status = str( (file_size_dl, file_size_dl * 100. / float(file_size_str)))
#        status = status + chr(8)*(len(status)+1)
#        print(status)

    f.close()
 
#    with open('videos/'+unique_filename+'.mp4', 'wb') as f:
#        f.write(r.content)



def scrapeVidPage(video_id) :
    video_url= "https://www.imdb.com/video/"+video_id
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
        z=x.split("url")[4]
        link = z.split('\"')[2][:-1]
        break

    print(link)
    return link

    

video_url =scrapeVidPage("vi3877612057")
download(video_url)








###############################
#r = requests.get("https://cdn-a.amazon-adsystem.com/video/6feecfdc-9d90-4ae7-821c-bd1fd74855d4/MP4-10000kbs-29.97fps-48khz-320kbs-1080p.mp4")
#unique_filename = str(uuid.uuid4())
#with open('images/'+unique_filename+'.mp4', 'wb') as f:
#    f.write(r.content)
