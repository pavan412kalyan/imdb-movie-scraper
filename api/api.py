# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
import flask
from flask import request, jsonify,render_template,Response
import sys
import re
from flask import send_file
import json

from scrapping_functions import scrapIMDB
from reviews import scrapeReviews
from trendingMovies import trendingMovies
from tvseries_scraper import scrapeTv
from search_by_titles import scrapelist_title






#!pip install pymongo
#!pip install dnspython
#cluster movie
#db movie-db
#collection teluguImdb
#pthota3@asu.edu
#https://cloud.mongodb.com/v2/607c99e3d1949f7c3f143127#metrics/replicaSet/607ce0c08d32fa64397040a3/explorer/movie-db/teluguImdb/find
import config
client_url = config.mongo_db_url
client = pymongo.MongoClient(client_url)
db = client["movie-db"]
collection = db["teluguImdb"]



def findByName(movie) :
    movies_cursor= collection.find(({'name': re.compile(movie, re.IGNORECASE)})).limit(25)
    movie=[]
    for m in movies_cursor :
        movie.append(m) 
    return movie


def groupByGenre(genre) :
    movies_cursor= collection.find({'genre' : { "$in":[ genre ]}}).limit(20)
    movie=[]
    for m in movies_cursor :
        movie.append(m) 
    return movie

def searchById(id):
    movie = collection.find_one(id)
    return movie
    
def getImages(id) :
    movie = collection.find_one(id)
    if 'images' in movie :
        return movie['images']
    return {}    

    

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/api', methods=['GET'])
def api():
    return render_template('home.html')



@app.route('/api/movie/<movie>', methods=['GET'])
def movie(movie):
    print("+++++++++",movie,flush=True)
    movies = findByName(movie)
    return jsonify(movies)



@app.route('/api/genre/<genre>', methods=['GET'])
def genre(genre):
    movies = groupByGenre(genre)
    return jsonify(movies)

@app.route('/api/imdbid/<id>', methods=['GET'])
def SearchById(id):
    movies = searchById(id)
    return jsonify(movies)


@app.route('/api/images/<id>', methods=['GET'])
def SearchImagesById(id):
    images = getImages(id)
    return jsonify(images)

@app.route('/api/livescraper/movie/<id>', methods=['GET'])
def ScrapMovieNow(id):
    data = scrapIMDB(id)
    data["_id"]=id
    return jsonify(data)


@app.route('/api/livescraper/reviews/<id>', methods=['GET'])
def scrapeReviewsNow(id):
    #sort=helpfulnessScore&dir=desc&ratingFilter=0
    sort = request.args.get('sort') 
    if sort == None :
        sort="totalVotes"    
    
    ratingFilter = request.args.get('ratingFilter')
    if ratingFilter == None :
        ratingFilter=0   
        
    dir = request.args.get('dir')
    if dir == None :
        dir="desc"  
    data = scrapeReviews(id,sort,ratingFilter,dir)
    
    data["_id"]=id
    return jsonify(data)




@app.route('/api/livescraper/trendingIndia/<lan>', methods=['GET'])
def trendingIndia(lan):
    data =trendingMovies(lan)
    return jsonify(data)
    

 
@app.route('/api/livescraper/tv/<id>', methods=['GET'])
def scrapeTvshow(id):
    data =scrapeTv(id)
    return jsonify(data)

@app.route('/api/livescraper/title/<title>', methods=['GET'])
def scrapeSearchByTitle(title):
    count = request.args.get('count') 
    #count=int(count)
    if count == None :
        count = 30
    data = scrapelist_title(title,count)
    return jsonify(data)




@app.route('/api/livescraper/download/reviews/<id>', methods=['GET'])
def scrapeReviewsNowAndDownload(id):
    #sort=helpfulnessScore&dir=desc&ratingFilter=0
    sort = request.args.get('sort') 
    if sort == None :
        sort="totalVotes"    
    
    ratingFilter = request.args.get('ratingFilter')
    if ratingFilter == None :
        ratingFilter=0   
        
    dir = request.args.get('dir')
    if dir == None :
        dir="desc"  
    data = scrapeReviews(id,sort,ratingFilter,dir)
    
    data["_id"]=id
    
    
    return Response(
        json.dumps(data),
        mimetype="application/json",
        headers={"Content-disposition":
                 "attachment; filename="+id+".json"})

    
    
@app.route('/api/livescraper/download/tv/<id>', methods=['GET'])
def scrapeTvshowAndDownload(id):
    data =scrapeTv(id)
    data["_id"]=id

    return Response(
        json.dumps(data),
        mimetype="application/json",
        headers={"Content-disposition":
                 "attachment; filename="+id+".json"})   
   
#    return data



    

if __name__ == '__main__':
   app.run()