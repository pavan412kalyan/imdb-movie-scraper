# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from flask import  jsonify


#movie_url = "https://www.imdb.com/title/"+ImdbId+"/reviews/_ajax?"+"sort="+sort+"&dir="+dir+"&ratingFilter="+ratingFilter

#movie_url = "https://www.imdb.com/title/tt0944947/reviews/_ajax?"
 
 
def scrapeReviews(soup,ImdbId) :  
    
    try :
        reviews = soup.find_all('div',{'class' : 'imdb-user-review'})
    except :
        pass   
    

    data = {}
    data['ImdbId'] = ImdbId
    reviews_text =[]
    for review in reviews :
        review_imdb={}
        
        ################
        try :
            review_imdb['reviewer_name']=review.find('span',{'class':'display-name-link'}).find('a').string.strip()
        except :
            review_imdb['reviewer_name']=""    
        ###############
        try :
            review_imdb['reviewer_url']=review.find('span',{'class':'display-name-link'}).find('a')['href']
        except:
            review_imdb['reviewer_url']=""
        ############
        try :
            review_imdb['data-review-id']=review['data-review-id']
        except :
            review_imdb['data-review-id']=""
            
        #############
        try:
            short_review =review.find('a',{'class': 'title'})
            text=short_review.string.strip()
            review_imdb['short_review']=text
        except :
            review_imdb['short_review']=""
    
        ######################
        try :
            full_review = review.find('div',{'class' : 'show-more__control'})
            text = full_review.string.strip()
            review_imdb['full_review']=text
        except :
             review_imdb['full_review']=""
        #############
        try :
            review_date = review.find('span',{'class' : 'review-date'})
            text=review_date.string.strip()
            review_imdb['review_date'] =text    
        except :
             review_imdb['review_date']  ="" 
        #######
        try :
            ratings_span = review.find('span',{'class' : 'rating-other-user-rating'})
            text=ratings_span.find('span').string.strip()
            review_imdb['rating_value']  = text      
        except :
            review_imdb['rating_value']  = "" 
        ##########
        reviews_text.append(review_imdb)    
    
    data['reviews']=reviews_text
    return data



def scrap(movie_url,ImdbId,all_data) :
    print(movie_url)
    r = requests.get(url=movie_url)
    soup = BeautifulSoup(r.text, 'html.parser')
     
    data =scrapeReviews(soup,ImdbId) 
    all_data.append(data)
    try :
        pagination_key =soup.find('div',{'class' : 'load-more-data'})['data-key']
        movie_url = "https://www.imdb.com/title/"+ImdbId+"/reviews/_ajax?&paginationKey="+pagination_key
#        print(movie_url) 
        scrap(movie_url,ImdbId,all_data)
    except Exception as e:             
        print(e)
        return all_data
        

    
def start(ImdbId) :
     movie_url = "https://www.imdb.com/title/"+ImdbId+"/reviews/_ajax?"
     all_data=[]
     scrap(movie_url,ImdbId,all_data)
     reviews= {}
     reviews['ImdbId']=ImdbId
     reviews['reviews']=all_data
     return reviews

x=start("tt0944947")
import json

with open('dataset/'+"reviews_"+"pavan"+'.json', 'w') as json_file:
    json.dump(x, json_file)




