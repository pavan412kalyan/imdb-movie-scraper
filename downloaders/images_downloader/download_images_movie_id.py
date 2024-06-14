# -*- coding: utf-8 -*-

from flask import request
import requests
from bs4 import BeautifulSoup
import re,os
import uuid
from threading import Thread

def getImages(ImdbId) :
  url = "https://www.imdb.com/title/"+ImdbId+"/mediaindex"
  data= {}
  data['ImdbId']=ImdbId
  image_urls = []
  r = requests.get(headers={'User-Agent': 'Mozilla/5.0'},url=url)
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



def download(img_url) :
    r = requests.get(headers={'User-Agent': 'Mozilla/5.0'},url=img_url)
    unique_filename = str(uuid.uuid4())
    with open('images/'+unique_filename+'.JPG', 'wb') as f:
        f.write(r.content)


def start(ImdbId) :
    img=getImages(ImdbId)
    print("Creating folder")
    os.makedirs("images", exist_ok=True) 
    for i in img['other_images'] : 
        img_url =i['url']
        print(img_url)
        img_url = img_url.split(".")
        img_url = "https://m.media-amazon." + img_url[2]+"."
        print(img_url)
        
#        threads = []
        process = Thread(target=download, args=[img_url])
        process.start()
    #    threads.append(process)
    
#    for process in threads:
#        process.join()

start("tt0944947")
#    
#
#s="https://m.media-amazon.com/images/M/MV5BM2ZjMjBmZjktNTRhMS00YWQwLWIzZTQtZmE1ODU1NDYwMGE2XkEyXkFqcGdeQXVyNjY1MTg4Mzc@._V1_UY99_CR68,0,99,99_AL_.jpg"
#f=s.split(".")
#"https://m.media-amazon" + f[2]
