# -*- coding: utf-8 -*-

# this is to get list of ids from csv file -- check the csv format
import pandas as pd

imdbIds=[]
imdb=pd.read_csv('movieList.csv')
urls = imdb['movie_imdb_url']
for url  in urls :
    imdbIds.append(url.split('/')[4])


len(set(imdbIds))    
df = pd.DataFrame(set(imdbIds))
df.to_csv('TeluguIds.csv', index=False)

