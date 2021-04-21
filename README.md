This repo is for scraping the whole page of a movie from IMDB website.

https://www.imdb.com/title/tt2631186/

tt2631186 is the movie IMDB ID. <br>
Below are the functions for scraping Movie, Crew and Image and Video URLs
```
getMovieDetails(imdbID)
getCrewData(imdbID)
getImages(ImdbId)
getVideos(ImdbId)
```

1)Place list of IMDB id's of all the movies that you want scrape in TeluguIds.csv. <br>
2)Run scrape.py to starts scraping and then run formatData.py to merge all the individual files into JSON array <br>

View sample result of a single movie - https://raw.githubusercontent.com/pavan412kalyan/imdb-movie-scraper/main/tt2631186.json

1) Add all IMDB id's the movies that you want scrape in TeluguIds.csv. <br>
2) Run scrape.py to start scraping <br>
3) Run formatData.py to merge all the individual files into JSON array <br>


View sample result of a movie - https://raw.githubusercontent.com/pavan412kalyan/imdb-movie-scraper/main/tt2631186.json

### Results of 5287 Telugu Movies from IMDB Website 
https://drive.google.com/file/d/1FBNbZFvoE8E0tZ61jtk5rw8mB4xQrFRP/view?usp=sharing


Resources :
https://dev.to/magesh236/scrape-imdb-movie-rating-and-details-3a7c
https://dev.to/magesh236/scrape-imdb-movie-rating-and-details-3a7c
