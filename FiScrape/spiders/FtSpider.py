
import scrapy
from scrapy.loader import ItemLoader
from FiScrape.items import FT_ArticleItem, convert_ft_dt, InsiderArticleItem, convert_bi_dt # FT_AuthorItem, AuthorItemLoader
from datetime import date, datetime,timedelta
from pytz import timezone
from dateutil import parser
from scrapy.selector import Selector
from FiScrape.search import query, start_date
from unicodedata import normalize

# from ln_meta import ft_user,ft_pass,wsj_user,wsj_pass
# class LoginSpider(scrapy.Spider):
#     name = 'ftlog'
#     start_urls = ['http://www.example.com/users/login.php']

#     def parse(self, response):
#         return scrapy.FormRequest.from_response(
#             response,
#             formdata={'username': f'{ft_user}', 'password': f'{ft_pass}'},
#             callback=self.after_login
#         )

#     def after_login(self, response):
#         # check login succeed before going on
#         if "authentication failed" in response.body:
#             self.logger.error("Login failed")
#             return

class FtSpider(scrapy.Spider):
    '''
    Spider for the Financial Times.
    name :  'ft'
    '''
    name = "ft"
    allowed_domains = ['ft.com']
    domain_name ='https://www.ft.com'
    start_urls = [f"https://www.ft.com/search?q={query}&sort=date"]

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
                loader.add_css('tags', "a.o-teaser__tag::text")
                loader.add_css('article_link', "div.o-teaser__heading a::attr(href)")
                article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
                # go to the article page and pass the current collected article info
                # self.logger.info('Get article page url')
                article_item = loader.load_item()
                request = response.follow(article_url, self.parse_article, meta={'article_item': article_item})
                request.meta['article_item'] = article_item
                if request:
                    yield request
                else:
                    yield article_item

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
        article_summary = response.xpath('.//*[@class="o-topper__standfirst"]/text()').get()
        if article_summary:
            loader.add_value('article_summary', article_summary)
        image_caption = response.xpath('//*[@id="site-content"]/div[1]/figure/figcaption/text()').getall()
        if image_caption:
            loader.add_value('image_caption', image_caption)
        article_content = response.xpath('//*[contains(@class, "article__content-body n-content-body js-article__content-body")]//text()[not(ancestor::*[@class="n-content-layout__container"])]').getall()
        if article_content:
            loader.add_value('article_content', article_content)
        article_footnote = response.xpath('.//*[@id="site-content"]/div[3]/div[3]/p[1]/em/text()').get()
        if article_footnote:
            loader.add_value('article_footnote', article_footnote)
        article_footnote_2 = response.xpath('.//*[@id="site-content"]/div[3]/div[2]/p[last()-1]/em/text()').get()
        if article_footnote_2:
            loader.add_value('article_footnote', article_footnote_2)
        article_item['authors'] = {}
        article_item['authors']['author'] = {}
        authors = response.css("a.n-content-tag--author")
        if authors:
            for author in authors:
                article_item['authors']['author']['author_name'] = author.css("a.n-content-tag--author::text").get()
                bio_link = author.css("a.n-content-tag--author::attr(href)").extract()
                bio_link = response.urljoin(''.join(map(str, bio_link)))
                article_item['authors']['author']['bio_link'] = bio_link
                yield response.follow(bio_link, callback=self.parse_author, meta={'article_item': article_item})
                #yield from response.follow(author_url, callback=self.parse_author, cb_kwargs={'authors': article_item['authors']})
                # meta={'article_item': article_item}
                # 
        else:
            yield loader.load_item()

    def parse_author(self, response):
        article_item = response.meta['article_item']
        author = response.xpath('//div[@class="sub-header sub-header--author"]')
        # article_item['authors']['author']['author_name'] = author.xpath('//h1[@class="sub-header__page-title"]/text()').get().strip()
        article_item['authors']['author']['author_position'] = author.css("div.sub-header__strapline::text").get().strip()
        author_bio = author.css('.sub-header__description p ::text').getall()
        author_bio = normalize("NFKD", ' '.join(map(str, author_bio)).replace('  ', ' ').strip())
        article_item['authors']['author']['author_bio'] = author_bio
        article_item['authors']['author']['author_email'] = response.xpath("//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href").get().replace("mailto:", '').strip()
        article_item['authors']['author']['author_twitter'] = response.xpath('.//a[@class="sub-header__content__link sub-header__content__link--twitter-handle"]/@href').get().strip()
        yield article_item

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
#                 loader.add_css('tags', "a.o-teaser__tag::text")
#                 loader.add_css('article_link', "div.o-teaser__heading a::attr(href)")
#                 article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
#                 # go to the article page and pass the current collected article info
#                 # self.logger.info('Get article page url')
#                 article_item = loader.load_item()
#                 request = response.follow(article_url, self.parse_article, meta={'article_item': article_item})
#                 request.meta['article_item'] = article_item
#                 if request:
#                     yield request
#                 else:
#                     yield article_item

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
#         loader.add_xpath('image_caption', './/*[@class="n-content-image__caption"]/text()')
#         loader.add_xpath('article_content', './/*[@class="article__content-body n-content-body js-article__content-body"]/p/text()')
#         loader.add_xpath('article_footnote', './/*[@id="site-content"]/div[3]/div[3]/p[1]/em/text()')
#         loader.add_xpath('article_footnote', './/*[@id="site-content"]/div[3]/div[2]/p[last()-1]/em/text()')
#         # authors = response.css("a.n-content-tag--author::text").getall()
#         # print (authors)
#         # loader.add_css('author_names', "a.n-content-tag--author::text")

#         author_urls = response.css("a.n-content-tag--author::attr(href)").getall()
#         # yield from response.follow_all(author_urls, callback=self.add_authors, meta={'article_item': article_item})
#         if author_urls:
#             for author_url in author_urls:
#                 request = response.follow(author_url, callback=self.add_authors, meta={'article_item': article_item})
#                 request.meta['article_item'] = article_item
#                 if request:
#                     yield request
#                 else:
#                     yield loader.load_item()
#         else:
#             yield loader.load_item()

#     # def add_authors(self, response):
#     #     article_item = response.meta['article_item']
#     #     loader = ItemLoader(item=article_item, response=response)
#     #     loader.add_value('authors', self.parse_author(response))
#     #     yield loader.load_item()

#     # def parse_author(self, response):
#     #     # article_item = response.meta['article_item']
#     #     # loader = ItemLoader(item=article_item, response=response)
#     #     # author_item = FT_AuthorItem()
#     #     selector = Selector(response=response, type='html')
#     #     auth_loader = AuthorItemLoader(item=FT_AuthorItem(), selector=selector)
#     #     auth_loader.add_xpath('author_name', './/h1[@class="sub-header__page-title"]/text()')
#     #     auth_loader.add_css('author_position', 'div.sub-header__strapline::text')
#     #     auth_loader.add_xpath('author_bio','.//*[@class="sub-header__description"]/descendant-or-self::*/text()')
#     #     auth_loader.add_xpath('author_email', ".//a[@class='sub-header__content__link sub-header__content__link--email-address']/@href")
#     #     auth_loader.add_xpath('author_twitter', ".//a[@class='sub-header__content__link sub-header__content__link--twitter-handle']/@href")
#     #     yield dict(auth_loader.load_item())

#     def add_authors(self, response):
#         article_item = response.meta['article_item']
#         loader = ItemLoader(item=article_item, response=response)
#         loader.add_value('authors', self.parse_author(response))
#         yield loader.load_item()

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
#         author = dict(auth_loader.load_item())
#         yield author
