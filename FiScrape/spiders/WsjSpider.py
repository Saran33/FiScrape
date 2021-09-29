
import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import FT_ArticleItem, convert_ft_dt, InsiderArticleItem, convert_bi_dt, strp_dt #, FT_AuthorItem, AuthorItemLoader
from datetime import date, datetime,timedelta
from pytz import timezone
from dateutil import parser
from scrapy.selector import Selector
from FiScrape.search import query, start_date

# class WSJ_Spider(scrapy.Spider):
#     '''
#     Spider for the Wall Street Journal.
#     name :  'wsj'
#     '''
#     name = "wsj"
#     allowed_domains = ['wsj.com']
#     domain_name ='https://www.wsj.com'
#     start_urls = [f"https://www.wsj.com/search?query={query}&mod=searchresults_viewallresults"]

#     def parse(self, response):
#         self.logger.info('Parse function called on {}'.format(response.url))
#         #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
#         article_snippets = response.css('div.o-teaser.o-teaser--article.o-teaser--small.o-teaser--has-image.js-teaser')

#         for snippet in article_snippets:
#             published_date = snippet.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)').get()
#             published_date = convert_ft_dt(published_date)
#             if published_date >= start_date:
#                 loader = ItemLoader(item=FT_ArticleItem(), selector=snippet)
#                 loader.add_css('published_date', 'div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')
#                 loader.add_css('headline', "a.js-teaser-heading-link *::text")
#                 loader.add_css('standfirst', "p.o-teaser__standfirst *::text")
#                 # pay attention to the dot .// to use relative xpath
#                 # loader.add_xpath('article_content', ".//span[@class='text']/text()")
#                 # loader.add_css('article_content', '.text::text')
#                 # loader.add_xpath('author', './/small//text()')
#                 loader.add_css('tags', "a.o-teaser__tag::text")
#                 loader.add_css('article_link', "div.o-teaser__heading a::attr(href)")
#                 article_item = loader.load_item()

#                 #yield article_item

#                 article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
#                 # go to the article page and pass the current collected article info
#                 # self.logger.info('Get article page url')
#                 yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

#         last_date = response.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')[-1].extract()
#         last_date = convert_ft_dt(last_date)
#         if  last_date >= start_date:
#             # Go to next page
#             #for a in response.css('li.next a'):
#             for a in response.xpath(".//a[@class='search-pagination__next-page o-buttons o-buttons--secondary o-buttons-icon o-buttons-icon--arrow-right o-buttons--big o-buttons-icon--icon-only']"):
#                 # self.logger.info('Go to next page')
#                 yield response.follow(a, callback=self.parse)
#                 # yield response.follow(a, self.parse)

#     def parse_article(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         #loader.add_css('article_content', '.article__content ::text')
#         # authors = response.css("a.n-content-tag--author::text").getall()
#         # print (authors)
#         loader.add_css('author_names', "a.n-content-tag--author::text")
#         author_urls = response.css("a.n-content-tag--author::attr(href)").getall()
#         # go to the author page and pass the current collected article info
#         # self.logger.info('Get author page url')
#         for author_url in author_urls:
#             yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()
#         # yield loader.load_item(), [response.follow(author_url, self.parse_author, meta={'article_item': article_item}) for author_url in author_urls]

#     def parse_author(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         loader.add_css('author_bio', "div.sub-header__strapline::text")
#         loader.add_xpath('author_email', ".//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href")
#         loader.add_xpath('author_twitter', ".//a[@class='sub-header__content__link sub-header__content__link--twitter-handle']/@href")
#         #loader.add_css('author_names', '.author-title::text')
#         # loader.add_css('author_birthday', '.author-born-date::text')
#         # loader.add_css('author_bornlocation', '.author-born-location::text')
#         yield loader.load_item()

# class InsiderSpider(scrapy.Spider):
#     '''
#     Spider for Business Insider.
#     name :  'insider'
#     '''
#     name = "insider"
#     allowed_domains = ['businessinsider.com']
#     domain_name ='https://www.businessinsider.com'
#     start_urls = [f"https://www.businessinsider.com/s?q={query}"]

#     def parse(self, response):
#         self.logger.info('Parse function called on {}'.format(response.url))
#         #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
#         article_snippets = response.xpath('.//*[@id="l-content"]/section[@class="river-item featured-post"]')

#         for snippet in article_snippets:
#             published_date = snippet.css('div.tout-tag.d-lg-flex span::text').get()
#             published_date = convert_bi_dt(published_date)
#             if published_date >= start_date:
#                 loader = ItemLoader(item=InsiderArticleItem(), selector=snippet)
#                 loader.add_css('published_date', 'div.tout-tag.d-lg-flex span::text')
#                 loader.add_xpath('headline', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/text()')
#                 loader.add_xpath('standfirst', './/section/div[@class="tout-text-wrapper default-tout"]/div[@class="tout-copy river body-regular"]/text()')
#                 loader.add_xpath('tags', './/div[@class="tout-tag d-lg-flex"]/a/text()')
#                 loader.add_xpath('article_link', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href')
#                 article_item = loader.load_item()

#                 #yield article_item

#                 article_url = snippet.xpath('.//section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href').get()
#                 # go to the article page and pass the current collected article info
#                 # self.logger.info('Get article page url')
#                 yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

#         last_date = response.xpath('//*[@id="l-content"]/section[@class="river-item featured-post"]/div/span//text()')[-1].extract()
#         last_date = convert_bi_dt(last_date)
#         if  last_date >= start_date:
#             # Go to next page
#             for a in response.xpath('//*[@id="l-content"]/a').get():
#                 # self.logger.info('Go to next page')
#                 yield response.follow(a, callback=self.parse)

#     def parse_article(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         # summary = response.css('#piano-inline-content-wrapper > div > div > ul ::text').getall()
#         loader.add_css('article_summary', '#piano-inline-content-wrapper > div > div > ul ::text')
#         loader.add_xpath('author_names', '//*[@class="byline-author headline-bold"]/span/a/text()')
#         loader.add_css('article_content', '#piano-inline-content-wrapper > div > div > p ::text')
#         loader.add_xpath('article_footnote', '//*[@class="category-tagline body-italic"]/div/p[@class="body-italic"]/text()')
#         author_urls = response.xpath('//*[@class="byline-link byline-author-name"]/@href').getall()
#         # go to the author page and pass the current collected article info
#         # self.logger.info('Get author page url')
#         for author_url in author_urls:
#             yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()

#     def parse_author(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         loader.add_xpath('author_bio', './/*[@id="l-content"]/section[1]/div/div[2]/p/text()')
#         loader.add_xpath('author_email', './/*[@class="author-contact-icon-link share-link email"]/@href')
#         loader.add_xpath('author_twitter', './/*[@class="author-contact-icon-link share-link twitter"]/@href')
#         yield loader.load_item()

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
