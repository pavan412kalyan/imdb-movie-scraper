# -*- coding: utf-8 -*-

#https://www.imdb.com/title/tt10872600/keywords
##this is for scrapping trendnig movies  in india and lan is must - takes default as telugu

import requests
from bs4 import BeautifulSoup
import re
import json
def trendingMovies(lan="telugu") :
    data= {}
    data['lan']=lan

    
    movie_url ="https://www.imdb.com/india/"+lan+"/"
#    print(movie_url)
    r = requests.get(headers={'User-Agent': 'Mozilla/5.0'},url=movie_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    topMovies_soup = soup.findAll("div", {"class": "trending-list-rank-item"})
        
    trending=[]
    for m in topMovies_soup :
        
        movie_o ={}
        movie_o['name']=m.find('a').string
        movie_o['ImdbId']=m.find('a')['href'].split('/')[2]
        movie_o['todays_view_share'] =m.find('span',{"class": "trending-list-rank-item-share"}).string
        trending.append(movie_o)
    data['trending']= trending   
    return data        

#trendingMovies() 