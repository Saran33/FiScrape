
import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import ArticleItem
from datetime import date, datetime

todays_date = date.today()
today = todays_date.strftime("%B %-d, %Y")

class FT_Spider(scrapy.Spider):

    # Input
    query = input('Enter a search term: ').replace(' ', '+')
    start_date = input('Enter a start date in Y/M/D (e.g. 2021-02-22): ')
    start_date = datetime.strptime(start_date,'%Y-%m-%d')
    print ('Getting articles on: ' + query + '...\n')

    name = "ft"
    allowed_domains = ['ft.com']
    start_urls = [f"https://www.ft.com/search?q={query}&sort=date"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        # articles = response.xpath("//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
        articles = response.css('div.o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser')

        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article)
            loader.add_css('published_date', '.text::text')
            loader.add_css('headline', '.o-teaser__heading::text')
            loader.add_css('standfirst', '.o-teaser__standfirst::text')
            # pay attention to the dot .// to use relative xpath
            # loader.add_xpath('article_content', ".//span[@class='text']/text()")
            # loader.add_css('article_content', '.text::text')
            # loader.add_xpath('author', './/small//text()')
            loader.add_css('tags', '.o-teaser__tag::text')
            loader.add_css('link', '.js-teaser-heading-link + a::attr(href)')
            article_item = loader.load_item()

            # author_url = article.css('.author + a::attr(href)').get()
            # # go to the author page and pass the current collected article info
            # # self.logger.info('Get author page url')
            # yield response.follow(author_url, self.parse_author, meta={'article_item': article_item})

        # Go to next page
        for a in response.css('li.next a'):
            # self.logger.info('Go to next page')
            yield response.follow(a, callback=self.parse)
            # yield response.follow(a, self.parse)
    
    def parse_author(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        loader.add_css('author_name', '.author-title::text')
        loader.add_css('author_birthday', '.author-born-date::text')
        loader.add_css('author_bornlocation', '.author-born-location::text')
        loader.add_css('author_bio', '.author-description::text')
        yield loader.load_item()
