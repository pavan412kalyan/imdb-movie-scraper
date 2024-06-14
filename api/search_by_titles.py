# -*- coding: utf-8 -*-

#ur =https://www.imdb.com/search/title/?title=god
import requests
from bs4 import BeautifulSoup



def  scrapelist_title(title,count) :
    count =int(count)
    if count > 250 :
        count = 250
    
    url ="https://www.imdb.com/search/title/?title="+ str(title)+"&count="+ str(count) + "&view=simple" 
    print(url)
    r = requests.get(headers={'User-Agent': 'Mozilla/5.0'},url=url)
    soup = BeautifulSoup(r.text, 'html.parser')
    taglist = soup.findAll('div',{"class" : "col-title" })
    data = [ ]
#    print(taglist)
    for t in taglist :
        movie = {}
        try :
            movie['year'] = t.find('span',{'class' : 'lister-item-year'}).string.strip()
            movie['name'] = t.find('a').string.strip()
            movie['id'] = t.find('a')['href'].split('/')[2]
            data.append(movie)    

        except Exception as e:             
            print(e)
        
    return data
#data = scrapelist_title("king",30)