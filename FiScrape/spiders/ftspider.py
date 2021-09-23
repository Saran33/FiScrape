# import scrapy
# from scrapy.loader import ItemLoader
# from FiScrape.items import FT_ArticleItem # ArticleItem
# from datetime import date, datetime

# # Input
# query = input('Enter a search term: ').replace(' ', '+')
# if query == 'b':
#     query = 'bitcoin'
# start_date = input('Enter a start date in Y/M/D (e.g. 2021-02-22): ')
# if start_date == 'y':
#     start_date = '2021-01-01'
# elif start_date== 't':
#     start_date = datetime.now().date()
# if type(start_date) is str:
#     start_date = datetime.strptime(start_date,'%Y-%m-%d')
# print ('Getting articles on: ' + query + '...\n')

# class FT_Spider(scrapy.Spider):
#     '''
#     Spider for the Financial Times.
#     name :  'ft'
#     '''
#     name = "ft"
#     allowed_domains = ['ft.com']
#     domain_name ='https://www.ft.com'
#     start_urls = [f"https://www.ft.com/search?q={query}&sort=date",
#                     "https://www.ft.com/search?q=bitcoin&page=2&sort=date"]

#     def parse(self, response):
#         self.logger.info('Parse function called on {}'.format(response.url))
#         #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
#         article_snippets = response.css('div.o-teaser.o-teaser--article.o-teaser--small.o-teaser--has-image.js-teaser')

#         for snippet in article_snippets:
#             loader = ItemLoader(item=FT_ArticleItem(), selector=snippet)
#             loader.add_css('published_date', 'div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')
#             loader.add_css('headline', "a.js-teaser-heading-link *::text")
#             loader.add_css('standfirst', "p.o-teaser__standfirst *::text")
#             # pay attention to the dot .// to use relative xpath
#             # loader.add_xpath('article_content', ".//span[@class='text']/text()")
#             # loader.add_css('article_content', '.text::text')
#             # loader.add_xpath('author', './/small//text()')
#             loader.add_css('tags', "a.o-teaser__tag::text")
#             loader.add_css('article_link', "div.o-teaser__heading a::attr(href)")
#             article_item = loader.load_item()

#             yield article_item

#             article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
#             # go to the article page and pass the current collected article info
#             # self.logger.info('Get article page url')
#             yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

#         # Go to next page
#         #for a in response.css('li.next a'):
#         for a in response.xpath(".//a[@class='search-pagination__next-page o-buttons o-buttons--secondary o-buttons-icon o-buttons-icon--arrow-right o-buttons--big o-buttons-icon--icon-only']"):
#             # self.logger.info('Go to next page')
#             yield response.follow(a, callback=self.parse)
#             # yield response.follow(a, self.parse)

#     def parse_article(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         #loader.add_css('article_content', '.article__content ::text')
#         loader.add_css('author_names', "a.n-content-tag--author::text")
#         author_urls = response.css("a.n-content-tag--author::attr(href)").getall()
#         # go to the author page and pass the current collected article info
#         # self.logger.info('Get author page url')
#         for author_url in author_urls:
#             yield response.follow(author_url, self.parse_author, meta={'article_item': article_item})
#         yield loader.load_item()

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