## this is live tv series scrapper which scrapes all the seasons and episodes in it. This is  not imported
## ignore this 


import requests
from bs4 import BeautifulSoup
import re
import json


def scrapSeason(imdbID,season_no) :
    seasons_url="https://www.imdb.com/title/"+imdbID+"/episodes/?season="+str(season_no)
    r = requests.get(url=seasons_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    episodes=[]
    episodetags = soup.find('div',class_=['eplist']).findAll('div',class_=['list_item'])
#    print(len(episodetags))
    for e in episodetags :
        episode={}
        try :
            episode['epi_image_url']= e.find('img')['src']
            episode['episode_num']= e.find('a').find('div').find('div').string
            episode['epi_image_alt']= e.find('img')['alt']
            episode['air_date']=e.find('div',{'class' : 'airdate'}).string.strip()
            episode['title']=e.find('strong').find('a')['title']
            episode['episode_url']=e.find('strong').find('a')['href']
            episode['rating_value']=e.find('span',{'class' : 'ipl-rating-star__rating'}).string.strip()
            episode['rating_value']=e.find('span',{'class' : 'ipl-rating-star__total-votes'}).string.strip()
            episode['episode_plot']=e.find('div',{'class' : 'item_description'}).string.strip()
            episodes.append(episode)
        except :
            pass
    return episodes



imdb_url="https://www.imdb.com"

def scrapeTv(imdbID) :
#    imdbID="tt5753856"
    ############
    seasons_url ="https://www.imdb.com/title/"+imdbID+"/episodes"
    r = requests.get(url=seasons_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    seasons_tag=[]
    try :
        seasons_tag=soup.find('select',{'id':'bySeason'}).findAll('option')
    except:
        pass
    
    name=""
    try :
        name=soup.find('div',{'class':'subpage_title_block__right-column'}).find('a').string.strip()
    except :
        pass
    
    tv_series = {}
    tv_series['_id']=imdbID
    tv_series['title']=name
    
    air_years=""
    try :
        air_years=soup.find('div',{'class':'subpage_title_block__right-column'}).find('span').string.strip()
    except :
        pass
    tv_series['air_years']=air_years 
    
    #########
    tv_series['imdbID']=imdbID
    seasons= []
    for s in seasons_tag :
        season_no=s['value']
        season=scrapSeason(imdbID,season_no)
        seasons.append(season)
    tv_series['seasons']=seasons
    
    return tv_series
 

#import time
#start = time.process_time()
#ans=scrapeTv("tt0898266")
#print(time.process_time() - start)
  


