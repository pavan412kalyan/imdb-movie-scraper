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
- **Review Downloader**: Scrapes reviews using GraphQL API with pagination
- **Pages Downloader**: Bulk movie list scraping with GraphQL queries
- **Videos Downloader**: Extract and download videos with multi-threading support
- **Movie Info Downloader**: Extract comprehensive movie information from JSON-LD

### Usage:
```bash
# Images downloader
cd ImdbScraperV2/images_dowloader/
python3 images_downloader.py

# Video downloader - single video
cd ../videos_downloader/
python3 download_video_from_id.py

# Video downloader - bulk download with threading
python3 bulk_video_downloader.py

# Extract video IDs from movie gallery
python3 extract_video_ids_from_gallery.py

# Reviews downloader
cd ../review_downloader/
python3 reviews.py

# Pages downloader
cd ../pages_dowloader/
python3 scrape_all_movie_list.py

# Movie info downloader
cd ../movie_info_downloader/
python3 download_movie_info.py
```
  
### V2 Download Content Modules:
- **Images Downloader**: High-quality image extraction with pagination
- **Videos Downloader**: 
  - Single video download by ID
  - Bulk video download with multi-threading
  - Video gallery extraction
- **Reviews Downloader**: Complete review extraction with pagination
- **Pages Downloader**: Movie list scraping from search results
- **Movie Info Downloader**: Comprehensive movie metadata extraction
   
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





   