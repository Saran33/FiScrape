
import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import FT_ArticleItem, convert_ft_dt # ArticleItem
from datetime import date, datetime,timedelta
from pytz import timezone
from dateutil import parser
from ln_meta import ft_user, ft_pass

todays_date = date.today()
today = todays_date.strftime("%B %-d, %Y")

def strp_dt(text):
    """
    convert string '1932-03-17' to Python date, add utc timezone.
    """
    try:
        dt = datetime.strptime(text, "%Y-%m-%d")
    except:
        dt = parser.parse(text)
    dt = timezone.utc.localize(dt)
    return dt

# Input
query = input('Enter a search term: ').replace(' ', '+')
if query == 'b':
    query = 'bitcoin'
start_date = input('Enter a start date in Y/M/D (e.g. 2021-02-22): ')
if start_date == 'y':
    start_date = '2021-01-01'
elif start_date== 't':
    start_date = datetime.utcnow()
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
elif start_date== 'yd':
    start_date = datetime.utcnow()
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
if type(start_date) is str:
    start_date = datetime.strptime(start_date,'%Y-%m-%d')
start_date = timezone("UTC").localize(start_date)
print ('Getting articles on: ' + query + '...\n')

# class LoginSpider(scrapy.Spider):
#     name = 'ftlog'
#     start_urls = ['http://www.example.com/users/login.php']

#     def parse(self, response):
#         return scrapy.FormRequest.from_response(
#             response,
#             formdata={'username': 'john', 'password': 'secret'},
#             callback=self.after_login
#         )

#     def after_login(self, response):
#         # check login succeed before going on
#         if "authentication failed" in response.body:
#             self.logger.error("Login failed")
#             return

class FT_Spider(scrapy.Spider):
    '''
    Spider for the Financial Times.
    name :  'ft'
    '''
    name = "ft"
    allowed_domains = ['ft.com']
    domain_name ='https://www.ft.com'
    start_urls = [f"https://www.ft.com/search?q={query}&sort=date",
                    "https://www.ft.com/search?q=bitcoin&page=2&sort=date"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
        article_snippets = response.css('div.o-teaser.o-teaser--article.o-teaser--small.o-teaser--has-image.js-teaser')

        for snippet in article_snippets:
            published_date = snippet.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)').get()
            published_date = convert_ft_dt(published_date)
            if published_date >= start_date:
                loader = ItemLoader(item=FT_ArticleItem(), selector=snippet)
                loader.add_css('published_date', 'div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')
                loader.add_css('headline', "a.js-teaser-heading-link *::text")
                loader.add_css('standfirst', "p.o-teaser__standfirst *::text")
                # pay attention to the dot .// to use relative xpath
                # loader.add_xpath('article_content', ".//span[@class='text']/text()")
                # loader.add_css('article_content', '.text::text')
                # loader.add_xpath('author', './/small//text()')
                loader.add_css('tags', "a.o-teaser__tag::text")
                loader.add_css('article_link', "div.o-teaser__heading a::attr(href)")
                article_item = loader.load_item()

                #yield article_item

                article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
                # go to the article page and pass the current collected article info
                # self.logger.info('Get article page url')
                yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

        last_date = response.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')[-1].extract()
        last_date = convert_ft_dt(last_date)
        if  last_date >= start_date:
            # Go to next page
            #for a in response.css('li.next a'):
            for a in response.xpath(".//a[@class='search-pagination__next-page o-buttons o-buttons--secondary o-buttons-icon o-buttons-icon--arrow-right o-buttons--big o-buttons-icon--icon-only']"):
                # self.logger.info('Go to next page')
                yield response.follow(a, callback=self.parse)
                # yield response.follow(a, self.parse)

    def parse_article(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        #loader.add_css('article_content', '.article__content ::text')
        authors = response.css("a.n-content-tag--author::text").getall()
        print (authors)
        loader.add_css('author_names', "a.n-content-tag--author::text")
        author_urls = response.css("a.n-content-tag--author::attr(href)").getall()
        # go to the author page and pass the current collected article info
        # self.logger.info('Get author page url')
        for author_url in author_urls:
            yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()
        # yield loader.load_item(), [response.follow(author_url, self.parse_author, meta={'article_item': article_item}) for author_url in author_urls]

    def parse_author(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        loader.add_css('author_bio', "div.sub-header__strapline::text")
        loader.add_xpath('author_email', ".//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href")
        loader.add_xpath('author_twitter', ".//a[@class='sub-header__content__link sub-header__content__link--twitter-handle']/@href")
        #loader.add_css('author_names', '.author-title::text')
        # loader.add_css('author_birthday', '.author-born-date::text')
        # loader.add_css('author_bornlocation', '.author-born-location::text')
        yield loader.load_item()

# class FT_Spider(scrapy.Spider):
#     '''
#     Spider for the Financial Times.
#     name :  'ft'
#     '''
#     name = "ft"
#     allowed_domains = ['ft.com']
#     domain_name ='https://www.ft.com'
#     start_urls = [f"https://www.ft.com/search?q={query}&sort=date",]
#                     #"https://www.ft.com/search?q=bitcoin&page=2&sort=date"]

#     def parse(self, response):
#         self.logger.info('Scraping FT.')
        
#         article_snippets = response.css('div.o-teaser.o-teaser--article.o-teaser--small.o-teaser--has-image.js-teaser')
#         for snippet in article_snippets:

#             yield {
#                 'datetime': snippet.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)').getall(),
#                 'headline': "".join(snippet.css("a.js-teaser-heading-link *::text").extract()),
#                 #'standfirst': "".join(snippet.css("p.o-teaser__standfirst ::text").extract()),
#             }
    # def parse(self, response):
    #     self.logger.info('Parse function called on {}'.format(response.url))
    #     #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
    #     article_snippets = response.css('div.o-teaser.o-teaser--article.o-teaser--small.o-teaser--has-image.js-teaser')

    #     for snippet in article_snippets:
    #         loader = ItemLoader(item=FT_ArticleItem(), selector=snippet)
    #         loader.add_css('published_date', 'div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')
    #         loader.add_css('headline', "a.js-teaser-heading-link *::text")
    #         loader.add_css('standfirst', "p.o-teaser__standfirst *::text")
    #         # pay attention to the dot .// to use relative xpath
    #         # loader.add_xpath('article_content', ".//span[@class='text']/text()")
    #         # loader.add_css('article_content', '.text::text')
    #         # loader.add_xpath('author', './/small//text()')
    #         loader.add_css('tags', "a.o-teaser__tag::text")
    #         loader.add_css('article_link', f"{self.domain_name}div.o-teaser__heading a::attr(href)")
    #         article_item = loader.load_item()

    #         # yield {
    #         #     'text': quote.css('.text::text').get(),
    #         #     'author': quote.css('.author::text').get(),
    #         #     'tags': quote.css('.tag::text').getall(),
    #         # }

    #         article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
    #         # go to the article page and pass the current collected article info
    #         # self.logger.info('Get article page url')
    #         yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

    #     # # Go to next page
    #     # #for a in response.css('li.next a'):
    #     # for a in response.xpath(".//a[@class='search-pagination__next-page o-buttons o-buttons--secondary o-buttons-icon o-buttons-icon--arrow-right o-buttons--big o-buttons-icon--icon-only']"):
    #     #     # self.logger.info('Go to next page')
    #     #     yield response.follow(a, callback=self.parse)
    #     #     # yield response.follow(a, self.parse)

    def parse_article(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        #loader.add_css('article_content', '.article__content ::text')
        loader.add_css('author_names', "a.n-content-tag--author::text")
        author_urls = response.css("a.n-content-tag--author::attr(href)").getall()
        # go to the author page and pass the current collected article info
        # self.logger.info('Get author page url')
        for author_url in author_urls:
            yield response.follow(author_url, self.parse_author, meta={'article_item': article_item})
        yield loader.load_item()

    def parse_author(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        loader.add_css('author_bio', "div.sub-header__strapline::text")
        loader.add_xpath('author_email', ".//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href")
        loader.add_xpath('author_twitter', ".//a[@class='sub-header__content__link sub-header__content__link--twitter-handle']/@href")
        #loader.add_css('author_names', '.author-title::text')
        # loader.add_css('author_birthday', '.author-born-date::text')
        # loader.add_css('author_bornlocation', '.author-born-location::text')
        yield loader.load_item()

# class GenSpider(scrapy.Spider):
#     '''
#     generic news article spider template. 
#     name :  'gen'
#     '''
#     # # Input
#     # query = input('Enter a search term: ').replace(' ', '+')
#     # if query == 'b':
#     #     query = 'bitcoin'
#     # start_date = input('Enter a start date in Y/M/D (e.g. 2021-02-22): ')
#     # if start_date == 'y':
#     #     start_date = '2021-01-01'
#     # elif start_date== 't':
#     #     start_date = datetime.now().date()
#     # if type(start_date) is str:
#     #     start_date = datetime.strptime(start_date,'%Y-%m-%d')
#     # print ('Getting articles on: ' + query + '...\n')

#     name = "gen"
#     allowed_domains = ['ft.com']
#     start_urls = [f"https://www.ft.com/search?q={query}&sort=date"]

#     def parse(self, response):
#         self.logger.info('Parse function called on {}'.format(response.url))
#         # articles = response.xpath("//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
#         articles = response.css('div.o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser')

#         for article in articles:
#             loader = ItemLoader(item=ArticleItem(), selector=article)
#             loader.add_css('published_date', '.text::text')
#             loader.add_css('headline', '.o-teaser__heading::text')
#             loader.add_css('standfirst', '.o-teaser__standfirst::text')
#             # pay attention to the dot .// to use relative xpath
#             # loader.add_xpath('article_content', ".//span[@class='text']/text()")
#             # loader.add_css('article_content', '.text::text')
#             # loader.add_xpath('author', './/small//text()')
#             loader.add_css('tags', '.o-teaser__tag::text')
#             loader.add_css('link', '.js-teaser-heading-link + a::attr(href)')
#             article_item = loader.load_item()

#             # author_url = article.css('.author + a::attr(href)').get()
#             # # go to the author page and pass the current collected article info
#             # # self.logger.info('Get author page url')
#             # yield response.follow(author_url, self.parse_author, meta={'article_item': article_item})

#         # Go to next page
#         for a in response.css('li.next a'):
#             # self.logger.info('Go to next page')
#             yield response.follow(a, callback=self.parse)
#             # yield response.follow(a, self.parse)
    
#     def parse_author(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         loader.add_css('author_name', '.author-title::text')
#         loader.add_css('author_birthday', '.author-born-date::text')
#         loader.add_css('author_bornlocation', '.author-born-location::text')
#         loader.add_css('author_bio', '.author-description::text')
#         yield loader.load_item()
