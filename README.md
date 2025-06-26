This repo is for 
1) Scraping  content on IMDB website
2) REST API for content of IMDB <br>
   a) Static data  - hosted on MongoDB <br>
   b) Dynamic data - scraping from Imdb on Request
###  Link for API and documentation: https://imdb-rest-api.herokuapp.com/


3) **V2 Scraper** - Pull data from API instead of scraping the data from Website
  
## V2 Scraper (ImdbScraperV2/)
Modern scrapers using IMDB's GraphQL APIs for faster and more reliable data extraction:

### Features:
- **Images Downloader**: Downloads high-quality images using GraphQL pagination
- **Review Downloader**: Scrapes reviews using modern API endpoints
- **Pages Downloader**: Bulk movie list scraping with improved performance

### Usage:
```bash
cd ImdbScraperV2/images_dowloader/
python3 images_downloader.py
```
Use scrapeSel.py to get PERSISTED_QUERY_HASH variable

  
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





   