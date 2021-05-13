import requests
from bs4 import BeautifulSoup
import json
from pandas import DataFrame
import uuid
import sys

def  scrapelist(soup) :
    ids =[]
    movie_list=[]
    block= soup.find('div',{'class' : 'lister-list' })
    taglist = soup.findAll('div',{"class" : "lister-item mode-advanced" })
    for t in taglist :
        movie_block= {}
        #id
        try :
            A=t.findAll('a')[1]
            id=A['href'].split('/')[2]            
            movie_block['ImdbId']=id
            movie_block['_id']=id
            ids.append(id)
            #title
            movie_block['name']=A.text.strip()
            print(id)
        except Exception as e: 
            print(e)     
        
        #poster_url
        try :
            img_url=t.findAll('a')[0].find('img')['loadlate']
            img_url = img_url.split(".")
            img_url = "https://m.media-amazon." + img_url[2]+"."
            movie_block['poster_url']=img_url
        except:
            movie_block['poster_url']=""

        try :
           block= t.find('div',{"class" : "lister-item-content" })
           movie_block['year']=block.find('span',{"class" : "lister-item-year text-muted unbold" }).text[1:-1]
           #certificate
           try :
            movie_block['certificate']=block.find('span',{"class" : "certificate" }).text.strip()
           except :
               movie_block['certificate']=''
           #runtime
           try:    
               movie_block['runtime']=block.find('span',{"class" : "runtime" }).text.strip()
           except:
               movie_block['runtime']=''
           #genre
           try:    
               genres=block.find('span',{"class" : "genre" }).text.strip().split(',')
               movie_block['genre']=genres
           except:
               movie_block['genre']=[]
            #rating
           try:    
               rating=block.find('strong').text
               movie_block['ratingValue']=rating
           except:
               movie_block['ratingValue']=''
            #summary
           try:    
               summary=block.findAll('p',{'class' :'text-muted'})[1].text.strip()
               movie_block['summary_text']=summary
           except:
               movie_block['summary_text']=''
 
            #votes
           try :
                movie_block['ratingCount']=block.find('p',{"class" : "sort-num_votes-visible" }).findAll('span')[1].text.strip()
                
           except:
                movie_block['ratingCount']=''
                
            #crew
           try:
               cast=block.find('p',{'class' :''}).findAll('a')
               director= {}
               director['name']= cast[0].text.strip()
               director['name_id']= cast[0]['href'].split('/')[2]
               movie_block['director']=director
               
               actors = []
               for c in cast[1:] :
                   actor={}
                   actor['name']= c.text.strip()
                   actor['name_id']= c['href'].split('/')[2]
                   actors.append(actor)  
               movie_block['cast']=actors
           except:
               pass
               
        except Exception as e: 
            print(e)
        movie_list.append(movie_block)

    unique_filename = str(uuid.uuid4())
    with open('pages/'+unique_filename +'.json', 'w') as json_file:
        json.dump(movie_list, json_file)
             
    your_list=ids
    df = DataFrame (your_list)
    #unique_filename = str(uuid.uuid4())
    df.to_csv("pagesId/"+ unique_filename+".csv" ,index=False)        
    

def start_pagination(next_page) :
    imdb = "https://www.imdb.com"
    while next_page!="" :
            print(next_page)
            r = requests.get(url=next_page)
            soup = BeautifulSoup(r.text, 'html.parser')
            try: 
                  next_page = imdb + soup.find('a',{'class': 'lister-page-next next-page'})['href']
            except Exception as e: 
                print(e,'Invalid-URL')
                next_page=""
            try :
                scrapelist(soup)
                print(next_page)
            except Exception as e: 
                print(e,'Task Completed ')
                break

def start(pageurl) :
#    imdb = "https://www.imdb.com"
#    query= "?title_type=feature,tv_movie,tv_series,tv_episode,tv_special,tv_miniseries,documentary,video_game,short,video,tv_short&languages=te&view=simple&sort=moviemeter,asc&count=250"
#    
#    url=imdb+query
#    pageurl="https://www.imdb.com/search/title/?title_type=feature&languages=te&count=250" 
    next_page=pageurl
    start_pagination(next_page)



#if __name__ == "__main__": 
#   file=sys.argv[1:]
#   if len(file)==1:
#       start(file[0])
#   else :
#        print('enter arguments --> python https://www.imdb.com/search/title/?title_type=feature&languages=te&view=simple&count=250 ')
#
start("https://www.imdb.com/search/title/?countries=in&count=250")   