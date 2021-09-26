# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re,os
import uuid
from urllib.request import urlopen



def download(video_url,video_id) :
    file_size_str = requests.head(video_url).headers['Content-Length']
    file_size = str(float(file_size_str)/1024/1024) 
    print(file_size + " MB")
#    r = requests.get(video_url)
    ru = urlopen(video_url)

    unique_filename = str(uuid.uuid4())
    f = open("videos/"+video_id+"_"+unique_filename+".mp4", 'wb')
    
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = ru.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        s= file_size_dl/1024/1024
        if s%5 == 0 :
            print(float(file_size_dl/1024/1024),"MB Downloaded")
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
    return link

    
def start_download(video_id) :
    os.makedirs("videos", exist_ok=True)

    video_url =scrapeVidPage(video_id)
    download(video_url,video_id)

video_id="vi1352056089"
start_download(video_id)

    
            
       






###############################
#r = requests.get("https://cdn-a.amazon-adsystem.com/video/6feecfdc-9d90-4ae7-821c-bd1fd74855d4/MP4-10000kbs-29.97fps-48khz-320kbs-1080p.mp4")
#unique_filename = str(uuid.uuid4())
#with open('images/'+unique_filename+'.mp4', 'wb') as f:
#    f.write(r.content)
