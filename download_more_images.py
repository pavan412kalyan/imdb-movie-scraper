# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

import uuid
from threading import Thread


def getImages(soup) :
#  url = "https://www.imdb.com/title/"+ImdbId+"/mediaindex"
  data= {}
  data['ImdbId']=ImdbId
  image_urls = []
#  r = requests.get(url=url)
#  soup = BeautifulSoup(r.text, 'html.parser')
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
    r = requests.get(img_url)
    unique_filename = str(uuid.uuid4())
    with open('images/'+unique_filename+'.JPG', 'wb') as f:
        f.write(r.content)




def startDownload(ImdbId) :
    imdb_domain = "https://www.imdb.com" 
    url = "https://www.imdb.com/title/"+ImdbId+"/mediaindex"
    next_page=url
    while next_page!="" :
            print(next_page)
            r = requests.get(url=next_page)
            soup = BeautifulSoup(r.text, 'html.parser')
            try: 
                  a= soup.findAll('a',{'class': 'prevnext'})[1]
                  next_page =imdb_domain + a['href']
                  if "Next" not in a.string :
                                  next_page=""
    
                  print(next_page)
    
            except Exception as e:
                print(e)
                next_page=""
                
            try :    
                img=getImages(soup)
                for i in img['other_images'] : 
                    img_url =i['url']
                    print(img_url)
                    img_url = img_url.split(".")
                    img_url = "https://m.media-amazon." + img_url[2]+"."
                    print(img_url)
                    threads = []
                    process = Thread(target=download, args=[img_url])
                    process.start()
                    threads.append(process)
                
                for process in threads:
                    process.join()
                
            except Exception as e: 
                print(e)
                break




ImdbId="tt0944947"
startDownload(ImdbId)







