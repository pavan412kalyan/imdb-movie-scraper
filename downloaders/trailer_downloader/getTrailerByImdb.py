import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
import uuid,sys,os,json
import re,os
import uuid
from threading import Thread
from urllib.request import urlopen

def getMovieTrailerDetails(imdbID):
    movie_url = "https://www.imdb.com/title/"+imdbID
    r = requests.get(url=movie_url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')
    jsonData = soup.find('script',{"type":"application/ld+json"})
    #print(jsonData.string)
    jsonSourceObj=json.loads(jsonData.string)
    movie = {}
    movie['title'] = jsonSourceObj['name']
    
    if 'description' in jsonSourceObj: 
        movie['description'] = jsonSourceObj['description']
    
    if 'image' in jsonSourceObj:
        movie['image'] = jsonSourceObj['image']
    
    movie['trailer_id'] = ""
    
    if 'keywords' in jsonSourceObj: 
        movie['keywords'] = jsonSourceObj['keywords']
    if 'director' in jsonSourceObj:
        movie['director'] = jsonSourceObj['director']
    if 'actor' in jsonSourceObj:
        movie['actor'] = jsonSourceObj['actor']
    if 'datePublished' in jsonSourceObj:
        movie['datePublished'] = jsonSourceObj['datePublished']

    try :
        if 'trailer' in jsonSourceObj :
            movie['trailer_vid'] =jsonSourceObj['trailer']['embedUrl'].split('/')[-1]
            movie['trailer_name'] =jsonSourceObj['trailer']['name']
            movie['trailer_description'] =jsonSourceObj['trailer']['description']
    except :
        print("Trailer URL not found")
    return movie
##############
def download(video_url,video_id,imdbID) :
    file_size_str = requests.head(video_url).headers['Content-Length']
    file_size = str(float(file_size_str)/1024/1024) 
    print(file_size + " MB")
#    r = requests.get(video_url)
    ru = urlopen(video_url)
    f = open(f"trailers/{imdbID}/"+imdbID+".mp4", 'wb')
    
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

    urls = re.findall('[a-z]+[:.].*?(?=\s)', str(script)) #changed from script.text to str(script)
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
    
def start_download(video_id,imdbID) :
    video_url =scrapeVidPage(video_id)
    download(video_url,video_id,imdbID)


def start_image_download(thumb_url,imdbID) :
    img_url=thumb_url
    img_url = img_url.split(".")
    img_url = "https://m.media-amazon." + img_url[2]+"."
    print(img_url)
    r = requests.get(img_url)
    with open(f'trailers/{imdbID}/'+imdbID+'.JPG', 'wb') as f:
        f.write(r.content)

def start_trailer_download(imdbID):
    os.makedirs('trailers/'+imdbID, exist_ok=True)
    movie = getMovieTrailerDetails(imdbID)
    with open(f'trailers/{imdbID}/'+imdbID +'.json', 'w') as json_file:
        json.dump(movie, json_file)
    video_id_trailer = movie['trailer_vid']
    print("trailer_video_id",video_id_trailer)
    start_download(video_id=video_id_trailer,imdbID=imdbID)
    thumb_url =movie['image'] 
    start_image_download(thumb_url,imdbID)

    
def start(file_ids) :
    os.makedirs('trailers', exist_ok=True)
    ids =pd.read_csv(file_ids).iloc[:,0]
    ids = list(ids)

    for ImdbId in ids :
        start_trailer_download(ImdbId)
        
    '''
    threads = []
    for ImdbId in ids :
        process = Thread(target=start_trailer_download, args=[ImdbId])
        process.start()
        threads.append(process)
        time.sleep(2.5)##ip gets blocked         
    for process in threads:
         process.join()
    '''     
#start_trailer_download(imdbID='tt1160419')

start(file_ids='top250.csv') 







