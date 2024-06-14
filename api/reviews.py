# -*- coding: utf-8 -*-

# this is for scraping reviews given imdb id - also with filters from api urls

import requests
from bs4 import BeautifulSoup
import re
import json
def scrapeReviews(ImdbId,sort="submissionDate",ratingFilter=10,dir="asc") :
    
    try :
#        movie_url = "https://www.imdb.com/title/"+ImdbId+"/reviews?"+"sort="+sort+"&dir="+dir+"&ratingFilter="+ratingFilter
         movie_url = "https://www.imdb.com/title/"+ImdbId+"/reviews/_ajax?"+"sort="+sort+"&dir="+dir+"&ratingFilter="+ratingFilter
         print(movie_url)
    except :
        
#        movie_url = "https://www.imdb.com/title/"+ImdbId+"/reviews"
         movie_url = "https://www.imdb.com/title/"+ImdbId+"/reviews"+"/_ajax"
        
    r = requests.get(headers={'User-Agent': 'Mozilla/5.0'},url=movie_url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')
    try :
        reviews = soup.find_all('div',{'class' : 'imdb-user-review'})
    except :
        pass
        
    
    #review = soup.find('div',{'class' : 'imdb-user-review'})
    
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

#scarpeReviews(ImdbId)
