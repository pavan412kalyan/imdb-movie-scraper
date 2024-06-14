# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
import uuid,sys,os,json

def scrapechart(soup) :
    blocks =[]
    taglist = soup.find('tbody',{"class" : "lister-list" }).findAll('tr')
    for t in taglist :
        movie_block={}
        try :
            movie_block['ImdbId']=t.find('td',{'class':'posterColumn'}).find('a')['href'].split('/')[2]
            ###
            img_url=t.find('td',{'class':'posterColumn'}).find('img')['src']
            img_url = img_url.split(".")
            img_url = "https://m.media-amazon." + img_url[2]+"."
            movie_block['poster_url']=img_url
            ###
            movie_block['name']=t.find('td',{'class':'titleColumn'}).find('a').text.strip()
            movie_block['year']=t.find('span',{'class':'secondaryInfo'}).text.strip()
            movie_block['rating']=t.find('td',{'class':'ratingColumn'}).find('strong').text.strip()
            movie_block['rating-notes']=t.find('td',{'class':'ratingColumn'}).find('strong')['title']

        except Exception as e:          
            print(e)
        blocks.append(movie_block)
        unique_filename = str(uuid.uuid4())
    with open('charts/'+unique_filename +'.json', 'w') as json_file:
        json.dump(blocks, json_file)





def scrape(url) :
    os.makedirs("charts", exist_ok=True)
    r = requests.get(headers={'User-Agent': 'Mozilla/5.0'},url=url)
    soup = BeautifulSoup(r.text, 'html.parser')
    scrapechart(soup)


#url="https://www.imdb.com/india/top-rated-indian-movies/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=4da9d9a5-d299-43f2-9c53-f0efa18182cd&pf_rd_r=6K4T71CDNA8G26TF3J3S&pf_rd_s=right-4&pf_rd_t=15506&pf_rd_i=toptv&ref_=chttvtp_ql_7"
url='https://www.imdb.com/chart/top/'
scrape(url)


