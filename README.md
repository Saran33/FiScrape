# News_Scrape

### Financial news scraping and processing for machine learning. 
`news_scrape` is a package for scraping financial news for trading signals based on natural langage processing and sentiment analysis. It leverages `scrapy`.

A search term can be queried across numerous online news sources. The resulting scraped headlines and bylines (and optionally the full text), along with metadata, will be timestamped and stored for each publication.  

Each news source on a particular topic can be stored as a seperate feature for timeseries analysis. e.g. For Bitcoin, all FT articles with "Bitcoin" in the title and/or text will be one feature. WSJ articles will be another feature. This facilitates sentiment analysis on each publication individually, to see which, if any, yield the highest Information Coefficient (IC) or other measures of predictive merit. It could also be used for forensic inveztigation of "pump-and-dump" forms of market manipulation. 

Additionally, features may be further segmented by author.

Generated features can be stored locally as CSV or in a database using SQLAlchemy. The scraper can be set to run periodically to update the database for live trading.

The repository can be found at:
[Github-News_Scrape](https://github.com/Saran33/news_scrape/)

#### To install from git:
`pip install git+git://github.com/Saran33/news_scrape.git`
