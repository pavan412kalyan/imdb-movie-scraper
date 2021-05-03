This repo is for 
1) Scraping  content on IMDB website
2) REST API for content of IMDB <br>
   a) Static data  - hosted on MongoDB <br>
   b) Dynamic data - scraping from Imdb on Request
  
  
   Download Content     |   
   --------------       | 
   Image downloader     |  
   Video downloader     |
   Pages dowloader      |
   Reviews downloader   |
   Tv series dowloader  |
   movie dowloader      |
   
  # Reviews downloader
  1) Download all Reviews of Movie/Tv Series by Imdbd ID 
   
  # Image downloader
  1) Download Images by Imdbd ID 
  2) Download All Images of movie/Tv  by Imdbd ID 
  
  # Videos downloader
  1) Download videos by Imdbd ID 
  2) Download all videos of movie  by Imdbd ID 
  
  # Movie data downloader
  1) Download Movie data by list of Imdbd IDs from csv file 
  2) Download Movie data from list of csv files placed in a folder.

  # Tv series downloader
  1) Download Tv series data by Imdbd ID 

  # Page downloader
  1) Download all Imdbd IDs  by search list url 
  2) Download all movie data by search list url



## Movie Data API
id -->  ImdbId Example -  tt4154796
lan --> telugu,tamil,upcoming
```
Endpoint                     Methods  Rule
---------------------------  -------  --------------------------------------
home                         GET      /
ScrapMovieNow                GET      /api/livescraper/movie/<id>
SearchById                   GET      /api/imdbid/<id>
SearchImagesById             GET      /api/images/<id>
genre                        GET      /api/genre/<genre>
movie                        GET      /api/movie/<movie>
scrapeReviewsNow             GET      /api/livescraper/reviews/<id>
scrapeReviewsNowAndDownload  GET      /api/livescraper/download/reviews/<id>
scrapeSearchByTitle          GET      /api/livescraper/title/<title>
scrapeTvshow                 GET      /api/livescraper/tv/<id>
scrapeTvshowAndDownload      GET      /api/livescraper/download/tv/<id>
trendingIndia                GET      /api/livescraper/trendingIndia/<lan>
```





   