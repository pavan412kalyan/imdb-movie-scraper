# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re,os
import uuid,json
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
    script =soup.find("script",{'type': 'application/json'})
    json_object = json.loads(script.string)
    print(json_object["props"]["pageProps"]["videoPlaybackData"]["video"]["playbackURLs"])
    videos = json_object["props"]["pageProps"]["videoPlaybackData"]["video"]["playbackURLs"]
    # links video quality order auto,1080,720

    for video in videos[1:] :
        video_link = video["url"]
        print(video_link)  
        break
    return video_link

    # for x in urls :
    #     if ".mp4" in x :
    #         print("###",x,"###")

    #         try :
    #             z=x.split("url")[4]## HD video
    #         except :
    #             try :
    #                 z=x.split("url")[3]  ## SD video
    #             except :
    #                 z=x.split("url")[2]  ## 480p
    #         link = z.split('\"')[2][:-1]
    #         print("link",link)
    #         link = link.replace("\\u0026","&")

    #         break
    # print(link)
#https://imdb-video.media-imdb.com/vi3986080537/1434659454657-dx9ykf-1633625495700.mp4?Expires=1659393293\u0026Signature=RwcwtTToP13W8ZRBQKELrGQdBP8-iR6Ou70Evj5j1S4VmKl1rm6HvQGxeoOjgUmR3VvwLVfJOJcs2vB-wv-f~uEVAmBgoh~z5z5RJkPvZin8urHTgUR6W1jCFxEGa4S~Lmna7BaL6DG20ljonAjgvvxuS5Mnv2OAxHO7VNY6O~eWLPxmQ4tRXRyb0L3SRpKum9lnJDNL0eVQDin90K9SD9J2Vul-ZjkaOsaDkVGixrrCNeOneDX9AD23GhsUgCOMzp7z90HZcaRuLnJd0SoGc-RqR9jzFWsHIhjHIx50QvUzOL7txwj7g8s6CsLcsZdWdluKlLkgDUaVwr8kBELVSg__\u0026Key-Pair-Id=APKAIFLZBVQZ24NQH3K


    
def start_download(video_id) :
    os.makedirs("videos", exist_ok=True)

    video_url =scrapeVidPage(video_id)
    download(video_url,video_id)

video_id="vi1143521817"
start_download(video_id)

    
            
       






###############################
#r = requests.get("https://cdn-a.amazon-adsystem.com/video/6feecfdc-9d90-4ae7-821c-bd1fd74855d4/MP4-10000kbs-29.97fps-48khz-320kbs-1080p.mp4")
#unique_filename = str(uuid.uuid4())
#with open('images/'+unique_filename+'.mp4', 'wb') as f:
#    f.write(r.content)
