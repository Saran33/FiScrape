
# import scrapy
# from scrapy.loader import ItemLoader
# from FiScrape.items import FT_ArticleItem, convert_ft_dt, InsiderArticleItem, convert_bi_dt, FT_AuthorItem, AuthorItemLoader
# from datetime import date, datetime,timedelta
# from pytz import timezone
# from dateutil import parser
# from scrapy.selector import Selector

# todays_date = date.today()
# today = todays_date.strftime("%B %-d, %Y")

# def strp_dt(text):
#     """
#     convert string '1932-03-17' to Python date, add utc timezone.
#     """
#     try:
#         dt = datetime.strptime(text, "%Y-%m-%d")
#     except:
#         dt = parser.parse(text)
#     dt = timezone.utc.localize(dt)
#     return dt

# # Input
# query = input('Enter a search term: ').replace(' ', '+')
# if query == 'b':
#     query = 'bitcoin'
# start_date = input('Enter a start date in Y/M/D (e.g. 2021-02-22): ')
# if start_date == 'y':
#     start_date = '2021-01-01'
# elif start_date== 't':
#     start_date = datetime.utcnow()
#     start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
# elif start_date== 'yd':
#     start_date = datetime.utcnow()
#     start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
# elif start_date== 'w':
#     start_date = datetime.utcnow()
#     start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
# if type(start_date) is str:
#     start_date = datetime.strptime(start_date,'%Y-%m-%d')
# start_date = timezone("UTC").localize(start_date)
# print ('Getting articles on: ' + query + '...\n')

# # from ln_meta import ft_user,ft_pass,wsj_user,wsj_pass
# # class LoginSpider(scrapy.Spider):
# #     name = 'ftlog'
# #     start_urls = ['http://www.example.com/users/login.php']

# #     def parse(self, response):
# #         return scrapy.FormRequest.from_response(
# #             response,
# #             formdata={'username': f'{ft_user}', 'password': f'{ft_pass}'},
# #             callback=self.after_login
# #         )

# #     def after_login(self, response):
# #         # check login succeed before going on
# #         if "authentication failed" in response.body:
# #             self.logger.error("Login failed")
# #             return

# # class FT_Spider(scrapy.Spider):
# #     '''
# #     Spider for the Financial Times.
# #     name :  'ft'
# #     '''
# #     name = "ft"
# #     allowed_domains = ['ft.com']
# #     domain_name ='https://www.ft.com'
# #     start_urls = [f"https://www.ft.com/search?q={query}&sort=date"]

# #     def parse(self, response):
# #         self.logger.info('Parse function called on {}'.format(response.url))
# #         #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
# #         article_snippets = response.css('div.o-teaser.o-teaser--article.o-teaser--small.o-teaser--has-image.js-teaser')

# #         for snippet in article_snippets:
# #             published_date = snippet.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)').get()
# #             published_date = convert_ft_dt(published_date)
# #             if published_date >= start_date:
# #                 loader = ItemLoader(item=FT_ArticleItem(), selector=snippet)
# #                 loader.add_css('published_date', 'div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')
# #                 loader.add_css('headline', "a.js-teaser-heading-link *::text")
# #                 loader.add_css('standfirst', "p.o-teaser__standfirst *::text")
# #                 # pay attention to the dot .// to use relative xpath
# #                 # loader.add_xpath('article_content', ".//span[@class='text']/text()")
# #                 # loader.add_css('article_content', '.text::text')
# #                 # loader.add_xpath('author', './/small//text()')
# #                 loader.add_css('tags', "a.o-teaser__tag::text")
# #                 loader.add_css('article_link', "div.o-teaser__heading a::attr(href)")
# #                 article_item = loader.load_item()

# #                 #yield article_item

# #                 article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
# #                 # go to the article page and pass the current collected article info
# #                 # self.logger.info('Get article page url')
# #                 yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

# #         last_date = response.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')[-1].extract()
# #         last_date = convert_ft_dt(last_date)
# #         if  last_date >= start_date:
# #             # Go to next page
# #             #for a in response.css('li.next a'):
# #             for a in response.xpath(".//a[@class='search-pagination__next-page o-buttons o-buttons--secondary o-buttons-icon o-buttons-icon--arrow-right o-buttons--big o-buttons-icon--icon-only']"):
# #                 # self.logger.info('Go to next page')
# #                 yield response.follow(a, callback=self.parse)
# #                 # yield response.follow(a, self.parse)

# #     def parse_article(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         loader.add_xpath('.//*[@class="article__content-body n-content-body js-article__content-body"]/p/text()')
# #         authors = response.css("a.n-content-tag--author::text").getall()
# #         print (authors)
# #         loader.add_css('author_names', "a.n-content-tag--author::text")
# #         author_urls = response.css("a.n-content-tag--author::attr(href)").getall()
# #         # go to the author page and pass the current collected article info
# #         # self.logger.info('Get author page url')
# #         for author_url in author_urls:
# #             yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()
# #         # yield loader.load_item(), [response.follow(author_url, self.parse_author, meta={'article_item': article_item}) for author_url in author_urls]

# #     def parse_author(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         loader.add_css('author_bio', "div.sub-header__strapline::text")
# #         loader.add_xpath('author_email', ".//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href")
# #         loader.add_xpath('author_twitter', ".//a[@class='sub-header__content__link sub-header__content__link--twitter-handle']/@href")
# #         #loader.add_css('author_names', '.author-title::text')
# #         # loader.add_css('author_birthday', '.author-born-date::text')
# #         # loader.add_css('author_bornlocation', '.author-born-location::text')
# #         yield loader.load_item()

# class FT_Spider(scrapy.Spider):
#     '''
#     Spider for the Financial Times.
#     name :  'ft'
#     '''
#     name = "ft"
#     allowed_domains = ['ft.com']
#     domain_name ='https://www.ft.com'
#     start_urls = [f"https://www.ft.com/search?q={query}&sort=date"]

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
#         loader.add_xpath('article_summary', './/*[@class="o-topper__standfirst"]/text()')
#         loader.add_xpath('image_caption', './/*[@class="n-content-image__caption"]')
#         loader.add_xpath('article_content', './/*[@class="article__content-body n-content-body js-article__content-body"]/p/text()')
#         loader.add_xpath('article_footnote', './/*[@id="site-content"]/div[3]/div[3]/p[1]/em/text()')
#         loader.add_xpath('article_footnote', './/*[@id="site-content"]/div[3]/div[2]/p[last()-1]/em/text()')
#         # authors = response.css("a.n-content-tag--author::text").getall()
#         # print (authors)
#         # loader.add_css('author_names', "a.n-content-tag--author::text")
#         author_urls = response.css("a.n-content-tag--author::attr(href)").getall()
#         # go to the author page and pass the current collected article info
#         # self.logger.info('Get author page url')

#         # for author_url in author_urls:
#         #     #yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()
#         #     yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()
#         # loader.add_value('authors', author_req.response)
#         # yield loader.load_item()
#         #     # yield loader.add_value('authors', author)
#         # #yield loader.add_value('authors', response.follow(author_url, self.parse_author, meta={'article_item': article_item}))
#         # # yield loader.load_item(), [response.follow(author_url, self.parse_author, meta={'article_item': article_item}) for author_url in author_urls]

#         yield from response.follow_all(author_urls, callback=self.add_authors, meta={'article_item': article_item})

#     def add_authors(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         loader.add_value('authors', self.parse_author(response))   
#         yield loader.load_item()
        
#     # def parse_author(self, response):
#     #     article_item = response.meta['article_item']
#     #     loader = ItemLoader(item=article_item, response=response)
#     #     author_item = FT_AuthorItem()
#     #     author_loader = ItemLoader(item=author_item, response=response)
#     #     author_loader.add_xpath('author_name', './/h1[@class="sub-header__page-title"]/text()')
#     #     author_loader.add_css('author_position', 'div.sub-header__strapline::text')
#     #     author_loader.add_xpath('author_bio','.//*[@class="sub-header__description"]/descendant-or-self::*/text()')
#     #     author_loader.add_xpath('author_email', ".//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href")
#     #     author_loader.add_xpath('author_twitter', ".//a[@class='sub-header__content__link sub-header__content__link--twitter-handle']/@href")
#     #     loader.add_value('authors', dict(author_item))
#     #     yield loader.load_item(), author_loader.load_item() #,

#     def parse_author(self, response):
#         # article_item = response.meta['article_item']
#         # loader = ItemLoader(item=article_item, response=response)
#         # author_item = FT_AuthorItem()
#         selector = Selector(response=response, type='html')
#         auth_loader = AuthorItemLoader(item=FT_AuthorItem(), selector=selector)
#         auth_loader.add_xpath('author_name', './/h1[@class="sub-header__page-title"]/text()')
#         auth_loader.add_css('author_position', 'div.sub-header__strapline::text')
#         auth_loader.add_xpath('author_bio','.//*[@class="sub-header__description"]/descendant-or-self::*/text()')
#         auth_loader.add_xpath('author_email', ".//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href")
#         auth_loader.add_xpath('author_twitter', ".//a[@class='sub-header__content__link sub-header__content__link--twitter-handle']/@href")
#         yield dict(auth_loader.load_item()) #, loader.load_item()

# # class WSJ_Spider(scrapy.Spider):
# #     '''
# #     Spider for the Wall Street Journal.
# #     name :  'wsj'
# #     '''
# #     name = "wsj"
# #     allowed_domains = ['wsj.com']
# #     domain_name ='https://www.wsj.com'
# #     start_urls = [f"https://www.wsj.com/search?query={query}&mod=searchresults_viewallresults"]

# #     def parse(self, response):
# #         self.logger.info('Parse function called on {}'.format(response.url))
# #         #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
# #         article_snippets = response.css('div.o-teaser.o-teaser--article.o-teaser--small.o-teaser--has-image.js-teaser')

# #         for snippet in article_snippets:
# #             published_date = snippet.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)').get()
# #             published_date = convert_ft_dt(published_date)
# #             if published_date >= start_date:
# #                 loader = ItemLoader(item=FT_ArticleItem(), selector=snippet)
# #                 loader.add_css('published_date', 'div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')
# #                 loader.add_css('headline', "a.js-teaser-heading-link *::text")
# #                 loader.add_css('standfirst', "p.o-teaser__standfirst *::text")
# #                 # pay attention to the dot .// to use relative xpath
# #                 # loader.add_xpath('article_content', ".//span[@class='text']/text()")
# #                 # loader.add_css('article_content', '.text::text')
# #                 # loader.add_xpath('author', './/small//text()')
# #                 loader.add_css('tags', "a.o-teaser__tag::text")
# #                 loader.add_css('article_link', "div.o-teaser__heading a::attr(href)")
# #                 article_item = loader.load_item()

# #                 #yield article_item

# #                 article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
# #                 # go to the article page and pass the current collected article info
# #                 # self.logger.info('Get article page url')
# #                 yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

# #         last_date = response.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')[-1].extract()
# #         last_date = convert_ft_dt(last_date)
# #         if  last_date >= start_date:
# #             # Go to next page
# #             #for a in response.css('li.next a'):
# #             for a in response.xpath(".//a[@class='search-pagination__next-page o-buttons o-buttons--secondary o-buttons-icon o-buttons-icon--arrow-right o-buttons--big o-buttons-icon--icon-only']"):
# #                 # self.logger.info('Go to next page')
# #                 yield response.follow(a, callback=self.parse)
# #                 # yield response.follow(a, self.parse)

# #     def parse_article(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         #loader.add_css('article_content', '.article__content ::text')
# #         # authors = response.css("a.n-content-tag--author::text").getall()
# #         # print (authors)
# #         loader.add_css('author_names', "a.n-content-tag--author::text")
# #         author_urls = response.css("a.n-content-tag--author::attr(href)").getall()
# #         # go to the author page and pass the current collected article info
# #         # self.logger.info('Get author page url')
# #         for author_url in author_urls:
# #             yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()
# #         # yield loader.load_item(), [response.follow(author_url, self.parse_author, meta={'article_item': article_item}) for author_url in author_urls]

# #     def parse_author(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         loader.add_css('author_bio', "div.sub-header__strapline::text")
# #         loader.add_xpath('author_email', ".//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href")
# #         loader.add_xpath('author_twitter', ".//a[@class='sub-header__content__link sub-header__content__link--twitter-handle']/@href")
# #         #loader.add_css('author_names', '.author-title::text')
# #         # loader.add_css('author_birthday', '.author-born-date::text')
# #         # loader.add_css('author_bornlocation', '.author-born-location::text')
# #         yield loader.load_item()

# # class InsiderSpider(scrapy.Spider):
# #     '''
# #     Spider for Business Insider.
# #     name :  'insider'
# #     '''
# #     name = "insider"
# #     allowed_domains = ['businessinsider.com']
# #     domain_name ='https://www.businessinsider.com'
# #     start_urls = [f"https://www.businessinsider.com/s?q={query}"]

# #     def parse(self, response):
# #         self.logger.info('Parse function called on {}'.format(response.url))
# #         #article_snippets = response.xpath(".//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
# #         article_snippets = response.xpath('.//*[@id="l-content"]/section[@class="river-item featured-post"]')

# #         for snippet in article_snippets:
# #             published_date = snippet.css('div.tout-tag.d-lg-flex span::text').get()
# #             published_date = convert_bi_dt(published_date)
# #             if published_date >= start_date:
# #                 loader = ItemLoader(item=InsiderArticleItem(), selector=snippet)
# #                 loader.add_css('published_date', 'div.tout-tag.d-lg-flex span::text')
# #                 loader.add_xpath('headline', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/text()')
# #                 loader.add_xpath('standfirst', './/section/div[@class="tout-text-wrapper default-tout"]/div[@class="tout-copy river body-regular"]/text()')
# #                 loader.add_xpath('tags', './/div[@class="tout-tag d-lg-flex"]/a/text()')
# #                 loader.add_xpath('article_link', './/section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href')
# #                 article_item = loader.load_item()

# #                 #yield article_item

# #                 article_url = snippet.xpath('.//section/div[@class="tout-text-wrapper default-tout"]/h2/a/@href').get()
# #                 # go to the article page and pass the current collected article info
# #                 # self.logger.info('Get article page url')
# #                 yield response.follow(article_url, self.parse_article, meta={'article_item': article_item})

# #         last_date = response.xpath('//*[@id="l-content"]/section[@class="river-item featured-post"]/div/span//text()')[-1].extract()
# #         last_date = convert_bi_dt(last_date)
# #         if  last_date >= start_date:
# #             # Go to next page
# #             for a in response.xpath('//*[@id="l-content"]/a').get():
# #                 # self.logger.info('Go to next page')
# #                 yield response.follow(a, callback=self.parse)

# #     def parse_article(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         # summary = response.css('#piano-inline-content-wrapper > div > div > ul ::text').getall()
# #         loader.add_css('article_summary', '#piano-inline-content-wrapper > div > div > ul ::text')
# #         loader.add_xpath('author_names', '//*[@class="byline-author headline-bold"]/span/a/text()')
# #         loader.add_css('article_content', '#piano-inline-content-wrapper > div > div > p ::text')
# #         loader.add_xpath('article_footnote', '//*[@class="category-tagline body-italic"]/div/p[@class="body-italic"]/text()')
# #         author_urls = response.xpath('//*[@class="byline-link byline-author-name"]/@href').getall()
# #         # go to the author page and pass the current collected article info
# #         # self.logger.info('Get author page url')
# #         for author_url in author_urls:
# #             yield response.follow(author_url, self.parse_author, meta={'article_item': article_item}) #, loader.load_item()

# #     def parse_author(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         loader.add_xpath('author_bio', './/*[@id="l-content"]/section[1]/div/div[2]/p/text()')
# #         loader.add_xpath('author_email', './/*[@class="author-contact-icon-link share-link email"]/@href')
# #         loader.add_xpath('author_twitter', './/*[@class="author-contact-icon-link share-link twitter"]/@href')
# #         yield loader.load_item()

# # class GenSpider(scrapy.Spider):
# #     '''
# #     generic news article spider template. 
# #     name :  'gen'
# #     '''
# #     # # Input
# #     # query = input('Enter a search term: ').replace(' ', '+')
# #     # if query == 'b':
# #     #     query = 'bitcoin'
# #     # start_date = input('Enter a start date in Y/M/D (e.g. 2021-02-22): ')
# #     # if start_date == 'y':
# #     #     start_date = '2021-01-01'
# #     # elif start_date== 't':
# #     #     start_date = datetime.now().date()
# #     # if type(start_date) is str:
# #     #     start_date = datetime.strptime(start_date,'%Y-%m-%d')
# #     # print ('Getting articles on: ' + query + '...\n')

# #     name = "gen"
# #     allowed_domains = ['ft.com']
# #     start_urls = [f"https://www.ft.com/search?q={query}&sort=date"]

# #     def parse(self, response):
# #         self.logger.info('Parse function called on {}'.format(response.url))
# #         # articles = response.xpath("//div[@class='o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser']")
# #         articles = response.css('div.o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser')

# #         for article in articles:
# #             loader = ItemLoader(item=ArticleItem(), selector=article)
# #             loader.add_css('published_date', '.text::text')
# #             loader.add_css('headline', '.o-teaser__heading::text')
# #             loader.add_css('standfirst', '.o-teaser__standfirst::text')
# #             # pay attention to the dot .// to use relative xpath
# #             # loader.add_xpath('article_content', ".//span[@class='text']/text()")
# #             # loader.add_css('article_content', '.text::text')
# #             # loader.add_xpath('author', './/small//text()')
# #             loader.add_css('tags', '.o-teaser__tag::text')
# #             loader.add_css('link', '.js-teaser-heading-link + a::attr(href)')
# #             article_item = loader.load_item()

# #             # author_url = article.css('.author + a::attr(href)').get()
# #             # # go to the author page and pass the current collected article info
# #             # # self.logger.info('Get author page url')
# #             # yield response.follow(author_url, self.parse_author, meta={'article_item': article_item})

# #         # Go to next page
# #         for a in response.css('li.next a'):
# #             # self.logger.info('Go to next page')
# #             yield response.follow(a, callback=self.parse)
# #             # yield response.follow(a, self.parse)
    
# #     def parse_author(self, response):
# #         article_item = response.meta['article_item']
# #         loader = ItemLoader(item=article_item, response=response)
# #         loader.add_css('author_name', '.author-title::text')
# #         loader.add_css('author_birthday', '.author-born-date::text')
# #         loader.add_css('author_bornlocation', '.author-born-location::text')
# #         loader.add_css('author_bio', '.author-description::text')
# #         yield loader.load_item()
