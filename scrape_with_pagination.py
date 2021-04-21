
import requests
from bs4 import BeautifulSoup
import re


def  scrapelist(soup) :
    taglist = soup.findAll('div',{"class" : "col-title" })
    for t in taglist :
        print(t.find('a')['href'])
        
imdb = "https://www.imdb.com"
query= "?title_type=feature,tv_movie,tv_series,tv_episode,tv_special,tv_miniseries,documentary,video_game,short,video,tv_short&languages=te&view=simple&sort=moviemeter,asc&count=250"

url=imdb+query
#url="https://www.imdb.com/search/title/?genres=western&countries=ad&languages=icl&view=simple&count=250"
url="https://www.imdb.com/search/title/?title_type=feature&languages=te&view=simple&count=250"
#url ="https://www.imdb.com/search/title/?title_type=feature&languages=hi&view=simple&count=250&start=12000"
next_page=url

while True :
        print(next_page)
        r = requests.get(url=next_page)
        soup = BeautifulSoup(r.text, 'html.parser')
        try :
            next_page = imdb + soup.find('a',{'class': 'lister-page-next next-page'})['href']
            scrapelist(soup)
            print(next_page)
        except Exception as e: 
            print(e)
            break


